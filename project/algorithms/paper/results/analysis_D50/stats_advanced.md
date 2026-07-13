# Advanced Statistical Analysis — results D=50 (D=50)

Algorithms k = 8; functions N = 13; runs per cell = 20; per-function aggregate = median.

## Omnibus test

- Friedman χ² = 61.615, df = 7, p = 7.177e-11
- Iman–Davenport F = 25.162, df = (7, 84), p = 3.554e-18
- Kendall's W (omnibus effect size) = 0.677 (large concordance)

## Mean ranks with 95% bootstrap CI (5000 resamples over functions)

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| IFPOA-X | 1.308 | [1.00, 1.92] |
| WOA | 3.000 | [1.92, 4.31] |
| PSO | 3.462 | [3.00, 3.85] |
| GWO | 3.769 | [3.15, 4.62] |
| FPA | 4.692 | [4.08, 5.31] |
| L-SHADE | 5.923 | [5.77, 6.00] |
| DE | 6.385 | [5.46, 7.00] |
| TPE | 7.462 | [6.62, 8.00] |

## Post-hoc vs control (control = IFPOA-X), adjusted p-values

z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; z < 0 means the other algorithm is better. Significant (p < 0.05) after correction shown in **bold**.

| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |
|---|---|---|---|---|---|
| IFPOA-X vs WOA | -1.69 | +1.76 | 7.817e-02 | 7.817e-02 | 7.817e-02 |
| IFPOA-X vs PSO | -2.15 | +2.24 | 2.497e-02 | **4.995e-02** | 2.908e-02 |
| IFPOA-X vs GWO | -2.46 | +2.56 | 1.041e-02 | **3.122e-02** | 1.454e-02 |
| IFPOA-X vs FPA | -3.38 | +3.52 | 4.270e-04 | **1.708e-03** | 7.471e-04 |
| IFPOA-X vs L-SHADE | -4.62 | +4.80 | 1.556e-06 | **7.782e-06** | 3.632e-06 |
| IFPOA-X vs DE | -5.08 | +5.28 | 1.262e-07 | **7.574e-07** | 4.418e-07 |
| IFPOA-X vs TPE | -6.15 | +6.41 | 1.502e-10 | **1.052e-09** | 1.052e-09 |

## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)

A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 favours IFPOA-X (smaller mean).

| Baseline | mean A12 | interpretation | mean Cohen's d |
|---|---|---|---|
| FPA | 0.983 | IFPOA-X better | -6.73 |
| PSO | 0.936 | IFPOA-X better | -5.42 |
| DE | 0.924 | IFPOA-X better | -8.16 |
| L-SHADE | 0.988 | IFPOA-X better | -9.12 |
| GWO | 0.983 | IFPOA-X better | -4.46 |
| WOA | 0.848 | IFPOA-X better | -1.83 |
| TPE | 0.924 | IFPOA-X better | -11.66 |