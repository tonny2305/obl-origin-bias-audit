#!/usr/bin/env python3
"""
Domain-safe re-run of F8 on the "mixed" multi-shift configuration.
==================================================================
The signed "mixed" shift can push F8's (Schwefel 2.26) evaluation argument
outside [-500,500]^D, where its offset-based non-negativity guarantee does not
hold, producing invalid negative fitness. F8 is the ONLY suite function with a
bounded validity domain; F1-F7, F9-F13 are non-negative on all of R^D and were
correctly shifted by pure translation.

Domain-safe construction (F8 only): g(x) = f8( clip(x - s, lo, hi) ). The shift
vector s (= target - native optimum) is IDENTICAL to the original mixed run, so
the optimum stays at the same off-centre target; clamping the argument into the
Schwefel validity box guarantees every evaluation is non-negative, removing the
need for any post-hoc exclusion.

Runs all 8 algorithms x 15 runs (same seeds as run_multishift.py) and saves to
results_shift_multi/mixed/f8_domainsafe_D30.csv for merging.
"""
import sys, io, time, contextlib, warnings
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
import functions as F0
import functions_shifted as FS
import baselines as B

MIXED = dict(seed=22222, lo_frac=0.30, hi_frac=0.70, signed=True)
LO, HI = -500.0, 500.0
X0 = F0.FUNCTIONS["F8"][2]                 # native optimum per-dim (420.9687)
_f8_raw = F0.FUNCTIONS["F8"][0]

HARNESS_ALGOS = ["ifpoax", "fpa", "pso"]
LABELS = {"ifpoax": "IFPOA-X", "fpa": "FPA", "pso": "PSO"}
ALL_ALGOS = HARNESS_ALGOS + list(B.BASELINES.keys())


def _shift_vector_f8():
    """Reproduce the EXACT mixed-config target for F8, then s = target - x0."""
    funcs = FS.make_functions(**MIXED)      # deterministic per (seed, index)
    t = funcs["F8"][2]                       # stored target (per-dim, 64-dim)
    s = t - np.full_like(t, X0)              # g(x)=f(x-s) has optimum at x=t
    return s, t


def make_f8_domain_safe(s):
    def g(x):
        x = np.asarray(x, float)
        z = np.clip(x - s[:x.size], LO, HI)  # keep argument inside Schwefel box
        return _f8_raw(z)
    return g


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def main(dim=30, budget=500, runs=15):
    s, t = _shift_vector_f8()
    g = make_f8_domain_safe(s)

    # --- validity self-check: optimum value ~0 and NO negative over wide sample ---
    D = dim
    assert abs(g(t[:D])) < 1e-2, f"optimum not preserved: g(t)={g(t[:D])}"
    rng = np.random.default_rng(0)
    X = rng.uniform(LO, HI, size=(5000, D))
    vals = np.array([g(x) for x in X])
    assert vals.min() >= -1e-6, f"domain-safe FAILED: min sample = {vals.min()}"
    print(f"[validity] g(optimum)={g(t[:D]):.2e}, min over 5000 samples={vals.min():.3e}  OK", flush=True)

    bt.register_benchmark_function("F8", g, (LO, HI))
    tmp_dir = str(_HERE / "results_shift_multi" / "mixed" / "_tmp_f8")
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)
    rows = []
    t_start = time.time()
    for algo in ALL_ALGOS:
        label = LABELS.get(algo, algo)
        bests = []
        for run_id in range(runs):
            seed = run_id * 1000
            if algo in HARNESS_ALGOS:
                import random
                random.seed(seed); np.random.seed(seed)
                runner = bt.AlgorithmRunner(algo, "F8", dim, budget, seed,
                                            save_dir=tmp_dir, equal_real_nfe=True)
                with _quiet():
                    out = runner.run()
                best = float(out["best_fitness"])
            else:
                with _quiet():
                    r = B.BASELINES[algo](g, (LO, HI), dim, budget, seed)
                best = float(r["best"])
            bests.append(best)
            rows.append({"Function": "F8", "Algorithm": label, "Run": run_id + 1, "Best": best})
        print(f"{label}={np.median(bests):.3e} (min={min(bests):.2e})  ", end="", flush=True)

    df = pd.DataFrame(rows)
    assert (df["Best"] >= -1e-6).all(), "negative fitness remains!"
    out = _HERE / "results_shift_multi" / "mixed" / "f8_domainsafe_D30.csv"
    df.to_csv(out, index=False, float_format="%.6e")
    print(f"\n[{time.time()-t_start:.0f}s] Saved: {out}  (all non-negative: {(df.Best>=0).all()})")


if __name__ == "__main__":
    main()
