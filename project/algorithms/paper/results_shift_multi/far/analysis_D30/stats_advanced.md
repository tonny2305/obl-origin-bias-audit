# Advanced Statistical Analysis — Multi-shift FAR (0.60-0.90, unsigned) (D=30)

Algorithms k = 8; functions N = 13; runs per cell = 15; per-function aggregate = median.

## Omnibus test

- Friedman χ² = 55.051, df = 7, p = 1.456e-09
- Iman–Davenport F = 18.377, df = (7, 84), p = 1.290e-14
- Kendall's W (omnibus effect size) = 0.605 (large concordance)

## Mean ranks with 95% bootstrap CI (5000 resamples over functions)

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| WOA | 1.231 | [1.00, 1.69] |
| GWO | 3.154 | [2.23, 4.31] |
| L-SHADE | 3.615 | [2.92, 4.38] |
| PSO | 4.538 | [4.00, 5.15] |
| TPE | 4.769 | [3.92, 5.54] |
| IFPOA-X | 5.231 | [4.62, 5.77] |
| DE | 5.846 | [4.54, 7.00] |
| FPA | 7.615 | [7.15, 8.00] |

## Post-hoc vs control (control = IFPOA-X), adjusted p-values

z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; z < 0 means the other algorithm is better. Significant (p < 0.05) after correction shown in **bold**.

| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |
|---|---|---|---|---|---|
| IFPOA-X vs WOA | +4.00 | -4.16 | 3.136e-05 | **2.195e-04** | 2.195e-04 |
| IFPOA-X vs GWO | +2.08 | -2.16 | 3.064e-02 | 1.532e-01 | 7.004e-02 |
| IFPOA-X vs L-SHADE | +1.62 | -1.68 | 9.270e-02 | 3.708e-01 | 1.565e-01 |
| IFPOA-X vs PSO | +0.69 | -0.72 | 4.712e-01 | 1.000e+00 | 5.901e-01 |
| IFPOA-X vs TPE | +0.46 | -0.48 | 6.310e-01 | 1.000e+00 | 6.310e-01 |
| IFPOA-X vs DE | -0.62 | +0.64 | 5.218e-01 | 1.000e+00 | 5.901e-01 |
| IFPOA-X vs FPA | -2.38 | +2.48 | 1.307e-02 | 7.839e-02 | 4.499e-02 |

## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)

A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 favours IFPOA-X (smaller mean).

| Baseline | mean A12 | interpretation | mean Cohen's d |
|---|---|---|---|
| FPA | 0.912 | IFPOA-X better | -2.92 |
| PSO | 0.393 | baseline better | +0.38 |
| DE | 0.634 | IFPOA-X better | -0.62 |
| L-SHADE | 0.227 | baseline better | +1.40 |
| GWO | 0.210 | baseline better | +1.48 |
| WOA | 0.040 | baseline better | +4.87 |
| TPE | 0.407 | baseline better | +0.27 |