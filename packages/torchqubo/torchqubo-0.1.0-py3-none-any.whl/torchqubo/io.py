
import torch
def load_q(path, device=None, dtype=torch.float32):
    with open(path,"r",encoding="utf-8") as f:
        lines=[ln.strip() for ln in f if ln.strip()]
    if not lines: raise ValueError("Empty Q file")
    fmt="coo"
    if lines[0].lower().startswith("# format:"):
        fmt=lines[0].split(":",1)[1].strip().lower(); lines=lines[1:]
    if fmt in ("coo","coordinate"):
        ijv=[]; mx=-1
        for ln in lines:
            if ln.startswith("#"): continue
            a=ln.split(); 
            if len(a)!=3: raise ValueError(f"Invalid COO line: {ln}")
            i,j,v=int(a[0]),int(a[1]),float(a[2]); ijv.append((i,j,v)); mx=max(mx,i,j)
        n=mx+1; Q=torch.zeros((n,n),dtype=dtype)
        for i,j,v in ijv: Q[i,j]+=v
        Q=(Q+Q.T)*0.5
    elif fmt=="dense":
        n=len(lines); rows=[[float(x) for x in ln.split()] for ln in lines]
        for r in rows:
            if len(r)!=n: raise ValueError("Dense must be n x n")
        Q=torch.tensor(rows,dtype=dtype); Q=(Q+Q.T)*0.5
    else:
        raise ValueError(f"Unknown format: {fmt}")
    if device is None: device="cuda" if torch.cuda.is_available() else "cpu"
    return Q.to(device)

def save_q_coo(path,Q):
    Qc=Q.detach().to("cpu"); n=Qc.shape[0]
    with open(path,"w",encoding="utf-8") as f:
        f.write("# format: coo\n")
        for i in range(n):
            for j in range(i,n):
                v=float(Qc[i,j])
                if v!=0.0: f.write(f"{i} {j} {v:.12g}\n")

def load_solution(path, device=None):
    with open(path,"r",encoding="utf-8") as f: txt=f.read().strip()
    if "\n" in txt and (" " not in txt.splitlines()[0]):
        vals=[float(ln.strip()) for ln in txt.splitlines() if ln.strip()]
    else:
        vals=[float(x) for x in txt.split()]
    x=torch.tensor(vals,dtype=torch.float32).clamp(0,1).round()
    if device is None: device="cuda" if torch.cuda.is_available() else "cpu"
    return x.unsqueeze(0).to(device)

def save_solution(path,x):
    if x.dim()==2 and x.shape[0]==1: x=x[0]
    vals=x.detach().to("cpu").round().int().tolist()
    with open(path,"w",encoding="utf-8") as f:
        for v in vals: f.write(f"{v}\n")
