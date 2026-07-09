#!/usr/bin/env python3
"""
Runner benchmark SHIFTED (origin-bias control) — PAPER 1.
=========================================================
Identik dengan run_benchmark.py tetapi memakai suite F1-F13 TER-GESER
(functions_shifted). Optimum digeser jauh dari pusat domain sehingga
keunggulan OBL yang berbasis refleksi-pusat tidak lagi selaras dengan optimum.
Protokol equal-NFE & pembanding sama persis. Algoritma tidak diubah.

Contoh:
  python run_shifted.py --dims 30 --budget 500 --runs 20
"""
import os, sys, io, time, argparse, contextlib, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_ALGO_DIR = _HERE.parent
_PROJECT_ROOT = _ALGO_DIR.parent.parent
for p in (str(_ALGO_DIR), str(_PROJECT_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import benchmark_tester as bt
import functions_shifted as F        # <-- suite ter-geser
import baselines as B

F.register_all(bt)

HARNESS_ALGOS = ["ifpoax", "fpa", "pso"]
LABELS = {"ifpoax": "IFPOA-X", "fpa": "FPA", "pso": "PSO"}
ALL_ALGOS = ["ifpoax", "fpa", "pso"] + list(B.BASELINES.keys())


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def _curve_from_harness(out, budget):
    fits = [e["fitness"] for e in out.get("all_evaluations", [])]
    if not fits:
        return np.full(budget, np.inf)
    curve = np.minimum.accumulate(np.asarray(fits, float))[:budget]
    if len(curve) < budget:
        curve = np.concatenate([curve, np.full(budget - len(curve), curve[-1])])
    return curve


def run_one(algo, func_name, dim, budget, seed, tmp_dir):
    if algo in HARNESS_ALGOS:
        import random
        random.seed(seed); np.random.seed(seed)
        runner = bt.AlgorithmRunner(algo, func_name, dim, budget, seed,
                                    save_dir=tmp_dir, equal_real_nfe=True)
        with _quiet():
            out = runner.run()
        return float(out["best_fitness"]), _curve_from_harness(out, budget)
    else:
        fn, bounds, _t, _m = F.FUNCTIONS[func_name]
        with _quiet():
            r = B.BASELINES[algo](fn, bounds, dim, budget, seed)
        return float(r["best"]), np.asarray(r["curve"], float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dims", type=int, nargs="+", default=[30])
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--funcs", type=str, nargs="+", default=list(F.FUNCTIONS.keys()))
    ap.add_argument("--algos", type=str, nargs="+", default=ALL_ALGOS)
    ap.add_argument("--out", type=str, default=str(_HERE / "results_shifted"))
    args = ap.parse_args()

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = str(out_dir / "_tmp"); Path(tmp_dir).mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    for dim in args.dims:
        print(f"\n{'='*70}\n[SHIFTED] DIM={dim} | budget={args.budget} | runs={args.runs}\n{'='*70}", flush=True)
        rows, curves = [], {}
        for func in args.funcs:
            print(f"\n[{func}] ", end="", flush=True)
            for algo in args.algos:
                label = LABELS.get(algo, algo)
                bests = []
                for run_id in range(args.runs):
                    best, curve = run_one(algo, func, dim, args.budget, run_id * 1000, tmp_dir)
                    bests.append(best)
                    curves.setdefault(f"{func}|{label}", []).append(curve)
                    rows.append({"Function": func, "Algorithm": label,
                                 "Run": run_id + 1, "Best": best})
                print(f"{label}={np.median(bests):.2e} ", end="", flush=True)
            print(f"  (elapsed {time.time()-t_start:.0f}s)", end="", flush=True)
        df = pd.DataFrame(rows)
        df.to_csv(out_dir / f"raw_D{dim}.csv", index=False, float_format="%.6e")
        np.savez_compressed(out_dir / f"curves_D{dim}.npz",
                            **{k: np.asarray(v, float) for k, v in curves.items()})
        print(f"\nSaved: {out_dir / f'raw_D{dim}.csv'}", flush=True)

    print("\nDONE (shifted).", flush=True)


if __name__ == "__main__":
    main()
