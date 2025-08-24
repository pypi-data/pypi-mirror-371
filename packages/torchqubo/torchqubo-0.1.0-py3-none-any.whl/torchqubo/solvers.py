import torch
from .utils import qubo_energy, delta_energy_all

@torch.no_grad()
def local_search(Q, x0=None, n=None, restarts=64, iters=300, tabu=0, device=None, seed=None):
    if seed is not None: torch.manual_seed(seed)
    Q=(Q+Q.T)*0.5; n=Q.shape[0] if n is None else n
    device=Q.device if device is None else device
    B=restarts if x0 is None else x0.shape[0]
    x=torch.randint(0,2,(B,n),device=device,dtype=torch.float32) if x0 is None else x0.clone()
    best_x=x.clone(); best_e=qubo_energy(Q,x)
    for _ in range(iters):
        dE=delta_energy_all(Q,x)
        idx=torch.argmin(dE,dim=1)
        rows=torch.arange(B,device=device)
        x[rows, idx] = 1.0 - x[rows, idx]   # flip bit for float tensors
        e=qubo_energy(Q,x); imp=e<best_e; best_x[imp]=x[imp]; best_e[imp]=e[imp]
    b=torch.argmin(best_e); return best_x[b:b+1], best_e[b]

@torch.no_grad()
def simulated_annealing(Q, restarts=64, steps=300, T0=2.0, Tend=0.01, device=None, seed=None):
    if seed is not None: torch.manual_seed(seed)
    Q=(Q+Q.T)*0.5; n=Q.shape[0]; device=Q.device if device is None else device
    B=restarts; x=torch.randint(0,2,(B,n),device=device,dtype=torch.float32)
    for t in range(steps):
        T=T0*(Tend/T0)**(t/max(steps-1,1)); dE=delta_energy_all(Q,x)
        probs=torch.softmax(-dE/max(T,1e-6),dim=1); idx=torch.multinomial(probs,1).squeeze(1)
        rows=torch.arange(B,device=device)
        x[rows, idx] = 1.0 - x[rows, idx]
    E=qubo_energy(Q,x); b=torch.argmin(E); return x[b:b+1], E[b]

@torch.no_grad()
def parallel_tempering(Q, replicas=16, steps=300, T_min=0.05, T_max=3.0, swap_every=10, device=None, seed=None):
    if seed is not None: torch.manual_seed(seed)
    Q=(Q+Q.T)*0.5; n=Q.shape[0]; device=Q.device if device is None else device
    B=replicas; temps=torch.logspace(torch.log10(torch.tensor(T_min)), torch.log10(torch.tensor(T_max)), B, device=device).float()
    x=torch.randint(0,2,(B,n),device=device,dtype=torch.float32); E=qubo_energy(Q,x)
    for t in range(steps):
        dE=delta_energy_all(Q,x); probs=torch.softmax(-dE/temps.unsqueeze(1).clamp_min(1e-6),dim=1)
        idx=torch.multinomial(probs,1).squeeze(1)
        rows=torch.arange(B,device=device)
        x[rows, idx] = 1.0 - x[rows, idx]
        E=qubo_energy(Q,x)
        if (t+1)%swap_every==0:
            for i in range(0,B-1,2):
                d=(1.0/temps[i]-1.0/temps[i+1])*(E[i+1]-E[i])
                if torch.rand((),device=device)<torch.exp(d.clamp(max=50)): x[i],x[i+1]=x[i+1].clone(),x[i].clone(); E[i],E[i+1]=E[i+1],E[i]
    b=torch.argmin(E); return x[b:b+1], E[b]

class _QUBOSte(torch.nn.Module):
    def __init__(self,n,tau): 
        super().__init__()
        self.theta=torch.nn.Parameter(torch.zeros(n))
        self.tau=tau
    def hard_x(self):
        p=torch.sigmoid(self.theta/self.tau)
        return (p>0.5).float()
    def forward(self,Q,lambda_bin=1e-2, lambda_mean=0.0, rho=0.5):
        p=torch.sigmoid(self.theta/self.tau)
        x_hard=(p>0.5).float()
        x = x_hard + (p - p.detach())          # STE
        E = torch.einsum("i,ij,j->", x, Q, x)
        penalty_bin  = lambda_bin * (p*(1-p)).sum()           # 推兩端 0/1
        penalty_mean = lambda_mean * (p.mean()-rho).pow(2)    # 控制平均密度
        return E + penalty_bin + penalty_mean

def ste_solve(Q, steps=1500, lr=0.05, tau0=1.0, tau_end=0.1,
              device=None, seed=None,
              lambda_bin=1e-2, lambda_mean=0.0, rho=0.5,
              init_std=0.5, refine_iters=0):
    if seed is not None: torch.manual_seed(seed)
    Q=(Q+Q.T)*0.5
    n=Q.shape[0]
    device=Q.device if device is None else device
    m=_QUBOSte(n,tau0).to(device)
    with torch.no_grad():
        m.theta.normal_(0.0, init_std)  # 隨機起始，避免全 0 陷阱
    opt=torch.optim.Adam(m.parameters(), lr=lr)
    for t in range(steps):
        m.tau = tau0 * (tau_end/tau0) ** (t / max(steps-1,1))
        opt.zero_grad()
        loss = m(Q, lambda_bin=lambda_bin, lambda_mean=lambda_mean, rho=rho)
        loss.backward(); opt.step()
    x = m.hard_x().unsqueeze(0)
    E = torch.einsum("bi,ij,bj->b", x, Q, x)[0]
    if refine_iters>0:
        from .solvers import local_search  # 避免循環引用時可移到頂端
        x,E = local_search(Q, x0=x, iters=refine_iters, tabu=5)
        if hasattr(E,"dim") and E.dim()==0: return x,E
        b=torch.argmin(E); return x[b:b+1], E[b]
    return x,E

def _gumbel_sigmoid(logits,tau):
    u=torch.rand_like(logits).clamp_min(1e-9); g=-torch.log(-torch.log(u)); return torch.sigmoid((logits+g)/tau)
def gumbel_solve(Q, restarts=16, steps=1000, lr=0.05, tau0=1.5, tau_end=0.1, device=None, seed=None):
    if seed is not None: torch.manual_seed(seed)
    Q=(Q+Q.T)*0.5; n=Q.shape[0]; device=Q.device if device is None else device
    B=restarts; logits=torch.zeros(B,n,device=device,requires_grad=True); opt=torch.optim.Adam([logits],lr=lr)
    for t in range(steps):
        tau=tau0*(tau_end/tau0)**(t/max(steps-1,1)); y=_gumbel_sigmoid(logits,tau); E=torch.einsum("bi,ij,bj->b",y,Q,y).mean()
        opt.zero_grad(); E.backward(); opt.step()
    with torch.no_grad():
        x=(torch.sigmoid(logits)>0.5).float(); e=qubo_energy(Q,x); b=torch.argmin(e); return x[b:b+1], e[b]

@torch.no_grad()
def spectral_rounding(Q, rounds=256, k=8, refine_iters=0, device=None, seed=None):
    if seed is not None: torch.manual_seed(seed)
    Q=(Q+Q.T)*0.5; device=Q.device if device is None else device; n=Q.shape[0]
    evals,evecs=torch.linalg.eigh(Q); U=evecs[:, :min(k,n)]; R=torch.randn(U.shape[1],rounds,device=device)
    Y=(U@R>0).T.float(); E=qubo_energy(Q,Y); b=torch.argmin(E); x=Y[b:b+1]; return x, E[b]

@torch.no_grad()
def grasp_plus_local(Q, restarts=128, alpha=0.3, ls_iters=100, device=None, seed=None):
    if seed is not None: torch.manual_seed(seed)
    Q=(Q+Q.T)*0.5; device=Q.device if device is None else device; n=Q.shape[0]
    ones=torch.ones(n,device=device); score=-(Q@ones); score=score/(score.std()+1e-9)
    B=restarts; noise=torch.randn(B,n,device=device); logits=score.unsqueeze(0)+alpha*noise
    x0=(torch.sigmoid(logits)>0.5).float()
    x_best,e_best=local_search(Q,x0=x0,iters=ls_iters,tabu=5)
    # local_search returns (1,n) and scalar energy when given a batch; handle both cases
    if hasattr(e_best, "dim") and e_best.dim()==0:
        return x_best, e_best
    b=torch.argmin(e_best); return x_best[b:b+1], e_best[b]



def solve(Q, method="local_search", **kw):
    m=method.lower()
    if m in ["local","local_search","tabu"]: return local_search(Q, **kw)
    if m in ["sa","anneal","simulated_annealing"]: return simulated_annealing(Q, **kw)
    if m in ["pt","parallel_tempering","replica"]: return parallel_tempering(Q, **kw)
    if m in ["ste"]: return ste_solve(Q, **kw)
    if m in ["gumbel","concrete"]: return gumbel_solve(Q, **kw)
    if m in ["spectral"]: return spectral_rounding(Q, **kw)
    if m in ["grasp"]: return grasp_plus_local(Q, **kw)
    raise ValueError(f"Unknown method: {method}")
