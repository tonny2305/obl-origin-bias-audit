# Advanced Statistical Analysis — Origin-shifted F1-F13 (D=30)

Algorithms k = 8; functions N = 13; runs per cell = 20; per-function aggregate = median.

## Omnibus test

- Friedman χ² = 60.897, df = 7, p = 9.990e-11
- Iman–Davenport F = 24.276, df = (7, 84), p = 9.523e-18
- Kendall's W (omnibus effect size) = 0.669 (large concordance)

## Mean ranks with 95% bootstrap CI (5000 resamples over functions)

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| WOA | 1.462 | [1.00, 2.23] |
| GWO | 2.231 | [1.69, 3.15] |
| L-SHADE | 3.385 | [2.92, 4.00] |
| PSO | 4.769 | [4.15, 5.46] |
| TPE | 4.923 | [4.46, 5.38] |
| IFPOA-X | 5.769 | [4.85, 6.54] |
| DE | 6.154 | [5.08, 7.15] |
| FPA | 7.308 | [6.69, 7.77] |

## Post-hoc vs control (control = IFPOA-X), adjusted p-values

z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; z < 0 means the other algorithm is better. Significant (p < 0.05) after correction shown in **bold**.

| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |
|---|---|---|---|---|---|
| IFPOA-X vs WOA | +4.31 | -4.48 | 7.340e-06 | **5.138e-05** | 5.138e-05 |
| IFPOA-X vs GWO | +3.54 | -3.68 | 2.306e-04 | **1.383e-03** | 8.067e-04 |
| IFPOA-X vs L-SHADE | +2.38 | -2.48 | 1.307e-02 | 6.533e-02 | 3.022e-02 |
| IFPOA-X vs PSO | +1.00 | -1.04 | 2.980e-01 | 8.939e-01 | 3.906e-01 |
| IFPOA-X vs TPE | +0.85 | -0.88 | 3.785e-01 | 8.939e-01 | 4.258e-01 |
| IFPOA-X vs DE | -0.38 | +0.40 | 6.889e-01 | 8.939e-01 | 6.889e-01 |
| IFPOA-X vs FPA | -1.54 | +1.60 | 1.093e-01 | 4.373e-01 | 1.834e-01 |

## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)

A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 favours IFPOA-X (smaller mean).

| Baseline | mean A12 | interpretation | mean Cohen's d |
|---|---|---|---|
| FPA | 0.766 | IFPOA-X better | -1.62 |
| PSO | 0.331 | baseline better | +0.66 |
| DE | 0.575 | IFPOA-X better | -0.39 |
| L-SHADE | 0.141 | baseline better | +1.88 |
| GWO | 0.105 | baseline better | +2.47 |
| WOA | 0.060 | baseline better | +3.72 |
| TPE | 0.361 | baseline better | +0.39 |