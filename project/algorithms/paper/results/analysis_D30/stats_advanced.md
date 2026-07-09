# Advanced Statistical Analysis — Classical F1-F13 (D=30)

Algorithms k = 8; functions N = 13; runs per cell = 20; per-function aggregate = median.

## Omnibus test

- Friedman χ² = 60.641, df = 7, p = 1.124e-10
- Iman–Davenport F = 23.970, df = (7, 84), p = 1.346e-17
- Kendall's W (omnibus effect size) = 0.666 (large concordance)

## Mean ranks with 95% bootstrap CI (5000 resamples over functions)

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| IFPOA-X | 1.308 | [1.00, 1.92] |
| GWO | 3.231 | [2.62, 4.15] |
| WOA | 3.385 | [2.23, 4.69] |
| PSO | 3.615 | [3.15, 4.08] |
| FPA | 4.692 | [4.23, 5.23] |
| L-SHADE | 6.000 | [5.77, 6.23] |
| DE | 6.385 | [5.69, 6.92] |
| TPE | 7.385 | [6.38, 8.00] |

## Post-hoc vs control (control = IFPOA-X), adjusted p-values

z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; z < 0 means the other algorithm is better. Significant (p < 0.05) after correction shown in **bold**.

| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |
|---|---|---|---|---|---|
| IFPOA-X vs GWO | -1.92 | +2.00 | 4.533e-02 | 6.128e-02 | 4.533e-02 |
| IFPOA-X vs WOA | -2.08 | +2.16 | 3.064e-02 | 6.128e-02 | 3.565e-02 |
| IFPOA-X vs PSO | -2.31 | +2.40 | 1.631e-02 | **4.893e-02** | 2.276e-02 |
| IFPOA-X vs FPA | -3.38 | +3.52 | 4.270e-04 | **1.708e-03** | 7.471e-04 |
| IFPOA-X vs L-SHADE | -4.69 | +4.88 | 1.040e-06 | **5.200e-06** | 2.427e-06 |
| IFPOA-X vs DE | -5.08 | +5.28 | 1.262e-07 | **7.574e-07** | 4.418e-07 |
| IFPOA-X vs TPE | -6.08 | +6.33 | 2.531e-10 | **1.772e-09** | 1.772e-09 |

## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)

A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 favours IFPOA-X (smaller mean).

| Baseline | mean A12 | interpretation | mean Cohen's d |
|---|---|---|---|
| FPA | 0.980 | IFPOA-X better | -4.90 |
| PSO | 0.946 | IFPOA-X better | -5.12 |
| DE | 0.925 | IFPOA-X better | -7.76 |
| L-SHADE | 0.979 | IFPOA-X better | -8.27 |
| GWO | 0.993 | IFPOA-X better | -3.88 |
| WOA | 0.877 | IFPOA-X better | -2.10 |
| TPE | 0.924 | IFPOA-X better | -10.33 |