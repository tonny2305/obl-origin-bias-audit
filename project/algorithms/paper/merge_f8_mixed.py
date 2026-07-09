#!/usr/bin/env python3
"""Merge the domain-safe F8 re-run into the 'mixed' multi-shift results,
producing a full 13-function valid dataset (no post-hoc exclusion), then
report the updated win/loss/tie and mean ranks."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

_HERE = Path(__file__).resolve().parent
mixed = pd.read_csv(_HERE / "results_shift_multi" / "mixed" / "raw_D30.csv")
f8 = pd.read_csv(_HERE / "results_shift_multi" / "mixed" / "f8_domainsafe_D30.csv")

assert (f8["Best"] >= -1e-6).all(), "F8 re-run still has negatives!"
merged = pd.concat([mixed[mixed.Function != "F8"], f8], ignore_index=True)
assert merged.Function.nunique() == 13, f"expected 13 funcs, got {merged.Function.nunique()}"
out = _HERE / "results_shift_multi" / "mixed_full"
out.mkdir(parents=True, exist_ok=True)
merged.to_csv(out / "raw_D30.csv", index=False, float_format="%.6e")
print(f"Merged -> {out/'raw_D30.csv'} ({merged.Function.nunique()} funcs, {len(merged)} rows)")

# win/loss/tie + mean ranks
PROPOSED = "IFPOA-X"
algos = list(dict.fromkeys(merged.Algorithm))
funcs = sorted(merged.Function.unique(), key=lambda f: int(f[1:]))
med = merged.groupby(["Function", "Algorithm"])["Best"].median().unstack()[algos]
ranks = med.rank(axis=1, method="average").mean(axis=0).sort_values()
print("\nMean Friedman ranks (mixed, full 13 functions, domain-safe F8):")
for a in ranks.index:
    print(f"  {a:10s} {ranks[a]:.2f}")

baselines = [a for a in algos if a != PROPOSED]
print("\nIFPOA-X vs baseline (Wilcoxon per function, win/loss/tie):")
for b in baselines:
    w = l = t = 0
    for f in funcs:
        d1 = merged[(merged.Function == f) & (merged.Algorithm == PROPOSED)].sort_values("Run")["Best"].values
        d2 = merged[(merged.Function == f) & (merged.Algorithm == b)].sort_values("Run")["Best"].values
        n = min(len(d1), len(d2))
        try:
            _, p = stats.ranksums(d1[:n], d2[:n])
        except Exception:
            p = 1.0
        better = np.median(d1) < np.median(d2)
        if p < 0.05 and better: w += 1
        elif p < 0.05: l += 1
        else: t += 1
    print(f"  {b:10s} {w}/{l}/{t}")

# F8 specifically
f8med = merged[merged.Function == "F8"].groupby("Algorithm")["Best"].median().sort_values()
print("\nF8 (domain-safe) median per algorithm:")
for a in f8med.index:
    print(f"  {a:10s} {f8med[a]:.3e}")
