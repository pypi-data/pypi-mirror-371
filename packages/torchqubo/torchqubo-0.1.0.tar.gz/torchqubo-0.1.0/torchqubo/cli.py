
import argparse, torch, time, sys, io
from .solvers import (
    local_search, simulated_annealing, parallel_tempering,
    ste_solve, gumbel_solve, spectral_rounding, grasp_plus_local
)
from .utils import qubo_energy
from .io import load_q, save_q_coo, load_solution, save_solution

def _resolve_device(arg_device):
    if arg_device is None or str(arg_device).lower() == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return arg_device

def _parse_seed(arg_seed):
    if arg_seed is None: return None
    s = str(arg_seed).strip().lower()
    if s in ["none","null","na",""]: return None
    return int(arg_seed)

def _write_log(path, text):
    if path is None:
        path = "log.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

# ------------------------ make-q ------------------------
def cmd_make_q(args):
    if args.seed is not None:
        torch.manual_seed(int(args.seed))
    n, density, scale = args.n, args.density, args.scale
    Q = torch.zeros((n, n), dtype=torch.float32)
    nnz_upper = max(1, int(density * (n*(n+1)//2)))
    ii = torch.randint(0, n, (nnz_upper,))
    jj = torch.randint(0, n, (nnz_upper,))
    a = torch.minimum(ii, jj); b = torch.maximum(ii, jj)
    vals = torch.randn(nnz_upper) * scale
    for i, j, v in zip(a.tolist(), b.tolist(), vals.tolist()):
        Q[i, j] += v
    Q = (Q + Q.T) * 0.5
    save_q_coo(args.out, Q)

# ------------------------ local_search ------------------------
def cmd_solve_local(args):
    dev = _resolve_device(args.device)
    seed = _parse_seed(args.seed)
    Q = load_q(args.Q, device=dev)
    t0 = time.time()
    x, E = local_search(Q, restarts=args.restarts, iters=args.iters, tabu=args.tabu, seed=seed)
    dt = time.time() - t0
    if args.out: save_solution(args.out, x)
    _write_log(args.log, f"""method: local_search
n: {Q.shape[0]}
device: {dev}
restarts: {args.restarts}
iters: {args.iters}
tabu: {args.tabu}
seed: {seed}
solution_path: {args.out}
energy: {E.item():.12g}
runtime_sec: {dt:.6f}
""")

# ------------------------ simulated_annealing ------------------------
def cmd_solve_sa(args):
    dev = _resolve_device(args.device)
    seed = _parse_seed(args.seed)
    Q = load_q(args.Q, device=dev)
    t0 = time.time()
    x, E = simulated_annealing(Q, restarts=args.restarts, steps=args.steps, T0=args.T0, Tend=args.Tend, seed=seed)
    dt = time.time() - t0
    if args.out: save_solution(args.out, x)
    _write_log(args.log, f"""method: simulated_annealing
n: {Q.shape[0]}
device: {dev}
restarts: {args.restarts}
steps: {args.steps}
T0: {args.T0}
Tend: {args.Tend}
seed: {seed}
solution_path: {args.out}
energy: {E.item():.12g}
runtime_sec: {dt:.6f}
""")

# ------------------------ parallel_tempering ------------------------
def cmd_solve_pt(args):
    dev = _resolve_device(args.device)
    seed = _parse_seed(args.seed)
    Q = load_q(args.Q, device=dev)
    t0 = time.time()
    x, E = parallel_tempering(Q, replicas=args.replicas, steps=args.steps, T_min=args.T_min, T_max=args.T_max, swap_every=args.swap_every, seed=seed)
    dt = time.time() - t0
    if args.out: save_solution(args.out, x)
    _write_log(args.log, f"""method: parallel_tempering
n: {Q.shape[0]}
device: {dev}
replicas: {args.replicas}
steps: {args.steps}
T_min: {args.T_min}
T_max: {args.T_max}
swap_every: {args.swap_every}
seed: {seed}
solution_path: {args.out}
energy: {E.item():.12g}
runtime_sec: {dt:.6f}
""")

# ------------------------ ste ------------------------
def cmd_solve_ste(args):
    dev = _resolve_device(args.device)
    seed = _parse_seed(args.seed)
    Q = load_q(args.Q, device=dev)
    t0 = time.time()
    x, E = ste_solve(Q, steps=args.steps, lr=args.lr, tau0=args.tau0, tau_end=args.tau_end, seed=seed)
    dt = time.time() - t0
    if args.out: save_solution(args.out, x)
    _write_log(args.log, f"""method: ste
n: {Q.shape[0]}
device: {dev}
steps: {args.steps}
lr: {args.lr}
tau0: {args.tau0}
tau_end: {args.tau_end}
seed: {seed}
solution_path: {args.out}
energy: {E.item():.12g}
runtime_sec: {dt:.6f}
""")

# ------------------------ gumbel ------------------------
def cmd_solve_gumbel(args):
    dev = _resolve_device(args.device)
    seed = _parse_seed(args.seed)
    Q = load_q(args.Q, device=dev)
    t0 = time.time()
    x, E = gumbel_solve(Q, restarts=args.restarts, steps=args.steps, lr=args.lr, tau0=args.tau0, tau_end=args.tau_end, seed=seed)
    dt = time.time() - t0
    if args.out: save_solution(args.out, x)
    _write_log(args.log, f"""method: gumbel
n: {Q.shape[0]}
device: {dev}
restarts: {args.restarts}
steps: {args.steps}
lr: {args.lr}
tau0: {args.tau0}
tau_end: {args.tau_end}
seed: {seed}
solution_path: {args.out}
energy: {E.item():.12g}
runtime_sec: {dt:.6f}
""")

# ------------------------ spectral ------------------------
def cmd_solve_spectral(args):
    dev = _resolve_device(args.device)
    seed = _parse_seed(args.seed)
    Q = load_q(args.Q, device=dev)
    t0 = time.time()
    x, E = spectral_rounding(Q, rounds=args.rounds, k=args.k, refine_iters=args.refine_iters, seed=seed)
    dt = time.time() - t0
    if args.out: save_solution(args.out, x)
    _write_log(args.log, f"""method: spectral
n: {Q.shape[0]}
device: {dev}
rounds: {args.rounds}
k: {args.k}
refine_iters: {args.refine_iters}
seed: {seed}
solution_path: {args.out}
energy: {E.item():.12g}
runtime_sec: {dt:.6f}
""")

# ------------------------ grasp ------------------------
def cmd_solve_grasp(args):
    dev = _resolve_device(args.device)
    seed = _parse_seed(args.seed)
    Q = load_q(args.Q, device=dev)
    t0 = time.time()
    x, E = grasp_plus_local(Q, restarts=args.restarts, alpha=args.alpha, ls_iters=args.ls_iters, seed=seed)
    dt = time.time() - t0
    if args.out: save_solution(args.out, x)
    _write_log(args.log, f"""method: grasp
n: {Q.shape[0]}
device: {dev}
restarts: {args.restarts}
alpha: {args.alpha}
ls_iters: {args.ls_iters}
seed: {seed}
solution_path: {args.out}
energy: {E.item():.12g}
runtime_sec: {dt:.6f}
""")

# ------------------------ energy ------------------------
def cmd_energy(args):
    dev = _resolve_device(args.device)
    Q = load_q(args.Q, device=dev)
    x = load_solution(args.sol, device=Q.device)
    E = qubo_energy(Q, x)[0].item()
    _write_log(args.log, f"""task: energy
n: {Q.shape[0]}
device: {dev}
Q: {args.Q}
sol: {args.sol}
energy: {E:.12g}
""")

def main():
    AD = argparse.ArgumentDefaultsHelpFormatter
    RT = argparse.RawTextHelpFormatter
    p = argparse.ArgumentParser(
        prog="torchqubo",
        description="TorchQUBO CLI (Q-only)",
        formatter_class=lambda *a, **k: AD(*a, **k)
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # make-q
    ep_make = """Examples:
  torchqubo make-q --n 256 --density 0.03 --scale 1.0 --seed 42 --out q.txt
"""
    p_m = sub.add_parser("make-q", help="Generate a random Q (COO text).", epilog=ep_make, formatter_class=RT)
    p_m.add_argument("--n", type=int, required=True)
    p_m.add_argument("--density", type=float, default=0.02, help="fraction of non-zeros in upper triangle [0,1]")
    p_m.add_argument("--scale", type=float, default=1.0, help="std of random values")
    p_m.add_argument("--seed", type=str, default=None)
    p_m.add_argument("--out", type=str, default="q.txt", help="output Q file (COO)")
    p_m.set_defaults(func=cmd_make_q)

    # helper
    def add_common_io(g):
        g.add_argument("--Q", type=str, required=True, help="path to Q file (COO or dense)")
        g.add_argument("--out", type=str, default="sol.txt", help="where to save 0/1 solution")
        g.add_argument("--log", type=str, default="log.txt", help="where to save run summary (text)")
        g.add_argument("--device", type=str, default="auto", help="cpu | cuda | auto")
        g.add_argument("--seed", type=str, default=None, help='random seed int, or "None" for no seed fix')

    # local_search
    ep_local = """Examples:
  torchqubo solve-local --Q q.txt --restarts 64 --iters 300 --tabu 5 --out sol.txt --log run_local.txt
"""
    p_l = sub.add_parser("solve-local", help="Greedy / Tabu local search.", epilog=ep_local, formatter_class=RT)
    add_common_io(p_l)
    p_l.add_argument("--restarts", type=int, default=64)
    p_l.add_argument("--iters", type=int, default=300)
    p_l.add_argument("--tabu", type=int, default=0, help="tabu tenure (0 to disable)")
    p_l.set_defaults(func=cmd_solve_local)

    # simulated_annealing
    ep_sa = """Examples:
  torchqubo solve-sa --Q q.txt --restarts 64 --steps 300 --T0 2.0 --Tend 0.01 --out sol.txt --log run_sa.txt
"""
    p_sa = sub.add_parser("solve-sa", help="Simulated annealing.", epilog=ep_sa, formatter_class=RT)
    add_common_io(p_sa)
    p_sa.add_argument("--restarts", type=int, default=64)
    p_sa.add_argument("--steps", type=int, default=300)
    p_sa.add_argument("--T0", type=float, default=2.0)
    p_sa.add_argument("--Tend", type=float, default=0.01)
    p_sa.set_defaults(func=cmd_solve_sa)

    # parallel_tempering
    ep_pt = """Examples:
  torchqubo solve-pt --Q q.txt --replicas 16 --steps 400 --T_min 0.05 --T_max 3.0 --swap_every 10 --out sol.txt --log run_pt.txt
"""
    p_pt = sub.add_parser("solve-pt", help="Parallel tempering / replica exchange.", epilog=ep_pt, formatter_class=RT)
    add_common_io(p_pt)
    p_pt.add_argument("--replicas", type=int, default=16)
    p_pt.add_argument("--steps", type=int, default=400)
    p_pt.add_argument("--T_min", type=float, default=0.05)
    p_pt.add_argument("--T_max", type=float, default=3.0)
    p_pt.add_argument("--swap_every", type=int, default=10)
    p_pt.set_defaults(func=cmd_solve_pt)

    # ste
    ep_ste = """Examples:
  torchqubo solve-ste --Q q.txt --steps 1500 --lr 0.05 --tau0 1.0 --tau_end 0.1 --out sol.txt --log run_ste.txt
"""
    p_ste = sub.add_parser("solve-ste", help="Straight-through estimator (gradient-based).", epilog=ep_ste, formatter_class=RT)
    add_common_io(p_ste)
    p_ste.add_argument("--steps", type=int, default=1500)
    p_ste.add_argument("--lr", type=float, default=0.05)
    p_ste.add_argument("--tau0", type=float, default=1.0)
    p_ste.add_argument("--tau_end", type=float, default=0.1)
    p_ste.set_defaults(func=cmd_solve_ste)

    # gumbel
    ep_g = """Examples:
  torchqubo solve-gumbel --Q q.txt --restarts 16 --steps 1000 --lr 0.05 --tau0 1.5 --tau_end 0.1 --out sol.txt --log run_gumbel.txt
"""
    p_g = sub.add_parser("solve-gumbel", help="Gumbel-Sigmoid / Concrete relaxation.", epilog=ep_g, formatter_class=RT)
    add_common_io(p_g)
    p_g.add_argument("--restarts", type=int, default=16)
    p_g.add_argument("--steps", type=int, default=1000)
    p_g.add_argument("--lr", type=float, default=0.05)
    p_g.add_argument("--tau0", type=float, default=1.5)
    p_g.add_argument("--tau_end", type=float, default=0.1)
    p_g.set_defaults(func=cmd_solve_gumbel)

    # spectral
    ep_sp = """Examples:
  torchqubo solve-spectral --Q q.txt --rounds 256 --k 8 --refine_iters 0 --out sol.txt --log run_spectral.txt
"""
    p_sp = sub.add_parser("solve-spectral", help="Spectral rounding (low-rank).", epilog=ep_sp, formatter_class=RT)
    add_common_io(p_sp)
    p_sp.add_argument("--rounds", type=int, default=256)
    p_sp.add_argument("--k", type=int, default=8)
    p_sp.add_argument("--refine_iters", type=int, default=0, help="if >0, run a brief local search refine")
    p_sp.set_defaults(func=cmd_solve_spectral)

    # grasp
    ep_gr = """Examples:
  torchqubo solve-grasp --Q q.txt --restarts 128 --alpha 0.3 --ls_iters 100 --out sol.txt --log run_grasp.txt
"""
    p_gr = sub.add_parser("solve-grasp", help="GRASP construction + local refine.", epilog=ep_gr, formatter_class=RT)
    add_common_io(p_gr)
    p_gr.add_argument("--restarts", type=int, default=128)
    p_gr.add_argument("--alpha", type=float, default=0.3)
    p_gr.add_argument("--ls_iters", type=int, default=100)
    p_gr.set_defaults(func=cmd_solve_grasp)

    # energy
    ep_en = """Examples:
  torchqubo energy --Q q.txt --sol sol.txt --log energy.txt
"""
    p_e = sub.add_parser("energy", help="Compute energy x^T Q x for solution and Q.", epilog=ep_en, formatter_class=RT)
    p_e.add_argument("--Q", type=str, required=True)
    p_e.add_argument("--sol", type=str, required=True)
    p_e.add_argument("--device", type=str, default="auto", help="cpu | cuda | auto")
    p_e.add_argument("--log", type=str, default="energy.txt", help="where to save the energy report")
    p_e.set_defaults(func=cmd_energy)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
