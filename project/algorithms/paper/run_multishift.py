#!/usr/bin/env python3
"""
Robustness lintas BEBERAPA vektor pergeseran (multi-shift) — PAPER 1.
=====================================================================
Menjawab keberatan reviewer bahwa pembalikan peringkat di §5.7 mungkin artefak
SATU vektor shift tertentu. Kita uji ulang pada beberapa konfigurasi shift yang
berbeda arah & magnitudo:
  - "far"   : optimum digeser jauh (0.60-0.90)*hi, positif
  - "mixed" : magnitudo 0.30-0.70, arah acak (+/-) per dimensi

Setiap konfigurasi menjalankan 8 algoritma × 13 fungsi × N run, equal-NFE.
Luaran: results_shift_multi/{config}/raw_D30.csv (+ curves).
Algoritma tidak diubah.

Contoh:
  python run_multishift.py --runs 15
"""
import sys, io, time, argparse, contextlib, warnings
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
import functions_shifted as FS
import baselines as B

HARNESS_ALGOS = ["ifpoax", "fpa", "pso"]
LABELS = {"ifpoax": "IFPOA-X", "fpa": "FPA", "pso": "PSO"}
ALL_ALGOS = HARNESS_ALGOS + list(B.BASELINES.keys())

CONFIGS = {
    "far":   dict(seed=11111, lo_frac=0.60, hi_frac=0.90, signed=False),
    "mixed": dict(seed=22222, lo_frac=0.30, hi_frac=0.70, signed=True),
}


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def _curve_from_harness(out, budget):
    fits = [e["fitness"] for e in out.get("all_evaluations", [])]
    if not fits:
        return np.full(budget, np.inf)
    c = np.minimum.accumulate(np.asarray(fits, float))[:budget]
    if len(c) < budget:
        c = np.concatenate([c, np.full(budget - len(c), c[-1])])
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dim", type=int, default=30)
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--runs", type=int, default=15)
    ap.add_argument("--out", type=str, default=str(_HERE / "results_shift_multi"))
    args = ap.parse_args()

    funcs = list(FS.FUNCTIONS.keys())
    t_start = time.time()

    for cfg_name, cfg in CONFIGS.items():
        FUNCS = FS.make_functions(**cfg)          # dict name -> (fn,bounds,t,mod)
        # register ke harness (menimpa registrasi sebelumnya — proses yg sama, aman)
        for name, (fn, bounds, _t, _m) in FUNCS.items():
            bt.register_benchmark_function(name, fn, bounds)

        out_dir = Path(args.out) / cfg_name
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp_dir = str(out_dir / "_tmp"); Path(tmp_dir).mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*70}\n[MULTISHIFT:{cfg_name}] {cfg}\n{'='*70}", flush=True)
        rows, curves = [], {}

        for func in funcs:
            print(f"\n[{cfg_name}:{func}] ", end="", flush=True)
            for algo in ALL_ALGOS:
                label = LABELS.get(algo, algo)
                bests = []
                for run_id in range(args.runs):
                    seed = run_id * 1000
                    if algo in HARNESS_ALGOS:
                        import random
                        random.seed(seed); np.random.seed(seed)
                        runner = bt.AlgorithmRunner(algo, func, args.dim, args.budget, seed,
                                                    save_dir=tmp_dir, equal_real_nfe=True)
                        with _quiet():
                            out = runner.run()
                        best = float(out["best_fitness"]); curve = _curve_from_harness(out, args.budget)
                    else:
                        fn, bounds, _t, _m = FUNCS[func]
                        with _quiet():
                            r = B.BASELINES[algo](fn, bounds, args.dim, args.budget, seed)
                        best = float(r["best"]); curve = np.asarray(r["curve"], float)
                    bests.append(best)
                    curves.setdefault(f"{func}|{label}", []).append(curve)
                    rows.append({"Function": func, "Algorithm": label, "Run": run_id + 1, "Best": best})
                print(f"{label}={np.median(bests):.2e} ", end="", flush=True)
            print(f"  (elapsed {time.time()-t_start:.0f}s)", end="", flush=True)

        pd.DataFrame(rows).to_csv(out_dir / f"raw_D{args.dim}.csv", index=False, float_format="%.6e")
        np.savez_compressed(out_dir / f"curves_D{args.dim}.npz",
                            **{k: np.asarray(v, float) for k, v in curves.items()})
        print(f"\nSaved: {out_dir / f'raw_D{args.dim}.csv'}", flush=True)

    print("\nDONE (multishift).", flush=True)


if __name__ == "__main__":
    main()
