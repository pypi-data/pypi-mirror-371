
import torch
def qubo_energy(Q, x):
    return torch.einsum("bi,ij,bj->b", x, Q, x)
@torch.no_grad()
def delta_energy_all(Q, x):
    Qsym=(Q+Q.T)*0.5
    d=torch.diag(Qsym); Qx=x@Qsym; s=(1-2*x)
    return s*(2*Qx-2*x*d+d)
