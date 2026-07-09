#!/usr/bin/env python3
"""
Ablation on the SHIFTED (Control-1) suite — enables the OBL x geometry
difference-in-differences requested by reviewers (High 2).

We already have (centred: full, no-OBL) from results/ablation_full_D30.csv and
(shifted: full) from results_shifted/raw_D30.csv. This script fills the missing
cell(s): the ablated variants on the shifted suite, using the identical seed
scheme (seed = run_id*1000) so every run is paired with its centred counterpart.

Default: no-OBL only (the essential cell for the OBL x geometry interaction).
Pass --variants to add no-JADE / base for the full symmetric table.

Example:
  python run_ablation_shifted.py --runs 20
"""
import sys, io, time, contextlib, argparse
from pathlib import Path
import pandas as pd

_HERE = Path(__file__).resolve().parent
_ALGO_DIR = _HERE.parent
_PROJECT_ROOT = _ALGO_DIR.parent.parent
for p in (str(_ALGO_DIR), str(_PROJECT_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import benchmark_tester as bt
import functions_shifted as F          # <-- Control-1 shifted suite

F.register_all(bt)

VARIANTS = {
    "IFPOA-X (no OBL)":    dict(use_obl=False, use_jade_local=True,  use_bandit=True),
    "IFPOA-X (no JADE)":   dict(use_obl=True,  use_jade_local=False, use_bandit=True),
    "IFPOA-X (base/FPA)":  dict(use_obl=False, use_jade_local=False, use_bandit=False),
}
FUNCS = [f"F{i}" for i in range(1, 14)]


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def run_one(flags, func, dim, budget, seed, tmp_dir):
    r = bt.AlgorithmRunner("ifpoax", func, dim, budget, seed, save_dir=tmp_dir,
                            equal_real_nfe=True, **flags)
    with _quiet():
        out = r.run()
    return float(out["best_fitness"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dim", type=int, default=30)
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--variants", type=str, nargs="+", default=["IFPOA-X (no OBL)"])
    ap.add_argument("--out", type=str, default=str(_HERE / "results_shifted" / "ablation_shifted_D30.csv"))
    args = ap.parse_args()

    variants = {k: VARIANTS[k] for k in args.variants}
    tmp_dir = str(_HERE / "results_shifted" / "_tmp")
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)
    rows = []
    t_start = time.time()
    total = len(FUNCS) * len(variants) * args.runs
    done = 0
    for func in FUNCS:
        for vname, flags in variants.items():
            for run_id in range(args.runs):
                best = run_one(flags, func, args.dim, args.budget, run_id * 1000, tmp_dir)
                rows.append({"Function": func, "Variant": vname, "Run": run_id + 1, "Best": best})
                done += 1
                print(f"[{done}/{total}] {func} {vname} run{run_id+1}: {best:.4e} "
                      f"(elapsed {time.time()-t_start:.0f}s)", flush=True)

    out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out_path, index=False, float_format="%.6e")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
