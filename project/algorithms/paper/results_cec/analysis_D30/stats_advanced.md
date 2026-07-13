# Advanced Statistical Analysis — results_cec D=30 (D=30)

Algorithms k = 8; functions N = 10; runs per cell = 20; per-function aggregate = median.

## Omnibus test

- Friedman χ² = 42.667, df = 7, p = 3.868e-07
- Iman–Davenport F = 14.049, df = (7, 63), p = 7.978e-11
- Kendall's W (omnibus effect size) = 0.610 (large concordance)

## Mean ranks with 95% bootstrap CI (5000 resamples over functions)

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| GWO | 1.300 | [1.00, 1.90] |
| PSO | 2.700 | [2.10, 3.30] |
| L-SHADE | 3.600 | [2.40, 5.20] |
| TPE | 4.200 | [3.40, 5.00] |
| IFPOA-X | 5.300 | [4.70, 5.90] |
| DE | 5.700 | [5.30, 6.00] |
| FPA | 6.200 | [5.00, 7.20] |
| WOA | 7.000 | [5.60, 7.80] |

## Post-hoc vs control (control = IFPOA-X), adjusted p-values

z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; z < 0 means the other algorithm is better. Significant (p < 0.05) after correction shown in **bold**.

| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |
|---|---|---|---|---|---|
| IFPOA-X vs GWO | +4.00 | -3.65 | 2.607e-04 | **1.825e-03** | 1.824e-03 |
| IFPOA-X vs PSO | +2.60 | -2.37 | 1.762e-02 | 1.057e-01 | 6.033e-02 |
| IFPOA-X vs L-SHADE | +1.70 | -1.55 | 1.207e-01 | 6.035e-01 | 2.593e-01 |
| IFPOA-X vs TPE | +1.10 | -1.00 | 3.153e-01 | 9.459e-01 | 4.116e-01 |
| IFPOA-X vs DE | -0.40 | +0.37 | 7.150e-01 | 9.459e-01 | 7.150e-01 |
| IFPOA-X vs FPA | -0.90 | +0.82 | 4.113e-01 | 9.459e-01 | 4.611e-01 |
| IFPOA-X vs WOA | -1.70 | +1.55 | 1.207e-01 | 6.035e-01 | 2.593e-01 |

## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)

A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 favours IFPOA-X (smaller mean).

| Baseline | mean A12 | interpretation | mean Cohen's d |
|---|---|---|---|
| FPA | 0.724 | IFPOA-X better | -1.05 |
| PSO | 0.132 | baseline better | +1.56 |
| DE | 0.556 | negligible | -0.27 |
| L-SHADE | 0.158 | baseline better | +1.87 |
| GWO | 0.083 | baseline better | +2.89 |
| WOA | 0.799 | IFPOA-X better | -1.38 |
| TPE | 0.276 | baseline better | +0.94 |