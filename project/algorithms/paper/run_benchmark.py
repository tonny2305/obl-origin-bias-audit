#!/usr/bin/env python3
"""
Runner benchmark PAPER 1 — IFPOA-X vs baseline pada suite F1-F13.
================================================================
Menjalankan algoritma USULAN (IFPOA-X) dan pembanding (FPA, PSO, DE, L-SHADE,
GWO, WOA, TPE) pada objektif & anggaran evaluasi objektif nyata (NFE) yang
identik (equal-NFE), lintas fungsi F1-F13 dan beberapa dimensi.

IFPOA-X/FPA/PSO dijalankan lewat harness benchmark_tester (tanpa mengubah
algoritma); baseline lain lewat paper/baselines.py. Luaran:
  results/raw_D{dim}.csv    : Function, Algorithm, Run, Best  (untuk statistik)
  results/curves_D{dim}.npz : kunci "F|ALGO" -> array (runs x budget) best-so-far

Contoh:
  python run_benchmark.py --dims 30 50 --budget 500 --runs 20
"""
import os, sys, io, json, time, argparse, contextlib, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_ALGO_DIR = _HERE.parent               # project/algorithms
_PROJECT_ROOT = _ALGO_DIR.parent.parent
for p in (str(_ALGO_DIR), str(_PROJECT_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import benchmark_tester as bt          # harness (equal-NFE) untuk IFPOA-X/FPA/PSO
import functions as F                  # F1-F13
import baselines as B                  # DE/L-SHADE/GWO/WOA/TPE

F.register_all(bt)                     # daftarkan F1-F13 ke harness

HARNESS_ALGOS = ["ifpoax", "fpa", "pso"]
LABELS = {"ifpoax": "IFPOA-X", "fpa": "FPA", "pso": "PSO"}
ALL_ALGOS = ["ifpoax", "fpa", "pso"] + list(B.BASELINES.keys())


@contextlib.contextmanager
def _quiet():
    """Bungkam stdout (mis. log per-trial IFPOA-X) tanpa menyentuh algoritma."""
    with contextlib.redirect_stdout(io.StringIO()):
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
    """Kembalikan (best, curve[budget]) untuk satu (algo, fungsi, run)."""
    if algo in HARNESS_ALGOS:
        import random
        random.seed(seed); np.random.seed(seed)
        runner = bt.AlgorithmRunner(algo, func_name, dim, budget, seed,
                                    save_dir=tmp_dir, equal_real_nfe=True)
        with _quiet():
            out = runner.run()
        return float(out["best_fitness"]), _curve_from_harness(out, budget)
    else:
        fn, bounds, _x, _m = F.FUNCTIONS[func_name]
        with _quiet():
            r = B.BASELINES[algo](fn, bounds, dim, budget, seed)
        curve = np.asarray(r["curve"], float)
        return float(r["best"]), curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dims", type=int, nargs="+", default=[30, 50])
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--funcs", type=str, nargs="+", default=list(F.FUNCTIONS.keys()))
    ap.add_argument("--algos", type=str, nargs="+", default=ALL_ALGOS)
    ap.add_argument("--out", type=str, default=str(_HERE / "results"))
    args = ap.parse_args()

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = str(out_dir / "_tmp"); Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    for dim in args.dims:
        print(f"\n{'='*70}\nDIM = {dim}  | budget(NFE) = {args.budget} | runs = {args.runs}\n{'='*70}")
        rows = []
        curves = {}  # "F|ALGO" -> list of curves
        for func in args.funcs:
            print(f"\n[{func}] ", end="", flush=True)
            for algo in args.algos:
                label = LABELS.get(algo, algo)
                bests = []
                for run_id in range(args.runs):
                    seed = run_id * 1000
                    t0 = time.time()
                    best, curve = run_one(algo, func, dim, args.budget, seed, tmp_dir)
                    bests.append(best)
                    curves.setdefault(f"{func}|{label}", []).append(curve)
                    rows.append({"Function": func, "Algorithm": label,
                                 "Run": run_id + 1, "Best": best})
                print(f"{label}={np.median(bests):.2e} ", end="", flush=True)
        # simpan per dimensi
        df = pd.DataFrame(rows)
        raw_path = out_dir / f"raw_D{dim}.csv"
        df.to_csv(raw_path, index=False, float_format="%.6e")
        npz = {k: np.asarray(v, float) for k, v in curves.items()}
        np.savez_compressed(out_dir / f"curves_D{dim}.npz", **npz)
        print(f"\n\nSaved: {raw_path}  &  curves_D{dim}.npz")

    print("\nDONE.")


if __name__ == "__main__":
    main()
