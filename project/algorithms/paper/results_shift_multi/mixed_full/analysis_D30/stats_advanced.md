# Advanced Statistical Analysis — mixed_full D=30 (D=30)

Algorithms k = 8; functions N = 13; runs per cell = 15; per-function aggregate = median.

## Omnibus test

- Friedman χ² = 63.205, df = 7, p = 3.448e-11
- Iman–Davenport F = 27.288, df = (7, 84), p = 3.655e-19
- Kendall's W (omnibus effect size) = 0.695 (large concordance)

## Mean ranks with 95% bootstrap CI (5000 resamples over functions)

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| GWO | 1.077 | [1.00, 1.23] |
| L-SHADE | 3.077 | [2.23, 4.08] |
| PSO | 3.308 | [2.85, 3.85] |
| TPE | 3.769 | [3.54, 4.00] |
| IFPOA-X | 5.308 | [4.77, 5.85] |
| DE | 5.692 | [4.31, 6.92] |
| FPA | 6.769 | [6.23, 7.31] |
| WOA | 7.000 | [6.38, 7.54] |

## Post-hoc vs control (control = IFPOA-X), adjusted p-values

z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; z < 0 means the other algorithm is better. Significant (p < 0.05) after correction shown in **bold**.

| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |
|---|---|---|---|---|---|
| IFPOA-X vs GWO | +4.23 | -4.40 | 1.065e-05 | **7.455e-05** | 7.455e-05 |
| IFPOA-X vs L-SHADE | +2.23 | -2.32 | 2.024e-02 | 1.214e-01 | 6.907e-02 |
| IFPOA-X vs PSO | +2.00 | -2.08 | 3.737e-02 | 1.869e-01 | 8.504e-02 |
| IFPOA-X vs TPE | +1.54 | -1.60 | 1.093e-01 | 3.279e-01 | 1.496e-01 |
| IFPOA-X vs DE | -0.38 | +0.40 | 6.889e-01 | 6.889e-01 | 6.889e-01 |
| IFPOA-X vs FPA | -1.46 | +1.52 | 1.282e-01 | 3.279e-01 | 1.496e-01 |
| IFPOA-X vs WOA | -1.69 | +1.76 | 7.817e-02 | 3.127e-01 | 1.328e-01 |

## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)

A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 favours IFPOA-X (smaller mean).

| Baseline | mean A12 | interpretation | mean Cohen's d |
|---|---|---|---|
| FPA | 0.719 | IFPOA-X better | -0.82 |
| PSO | 0.170 | baseline better | +1.24 |
| DE | 0.570 | IFPOA-X better | -0.28 |
| L-SHADE | 0.138 | baseline better | +1.80 |
| GWO | 0.041 | baseline better | +2.75 |
| WOA | 0.766 | IFPOA-X better | -1.24 |
| TPE | 0.254 | baseline better | +0.87 |