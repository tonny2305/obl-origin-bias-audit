# Advanced Statistical Analysis — Multi-shift MIXED (0.30-0.70, signed, F8 excluded) (D=30)

Algorithms k = 8; functions N = 12; runs per cell = 15; per-function aggregate = median.

## Omnibus test

- Friedman χ² = 65.722, df = 7, p = 1.076e-11
- Iman–Davenport F = 39.553, df = (7, 77), p = 5.379e-23
- Kendall's W (omnibus effect size) = 0.782 (large concordance)

## Mean ranks with 95% bootstrap CI (5000 resamples over functions)

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| GWO | 1.000 | [1.00, 1.00] |
| L-SHADE | 2.750 | [2.08, 3.58] |
| PSO | 3.167 | [2.75, 3.67] |
| TPE | 3.833 | [3.58, 4.00] |
| IFPOA-X | 5.250 | [4.67, 5.83] |
| DE | 6.083 | [4.83, 7.17] |
| FPA | 6.667 | [6.17, 7.17] |
| WOA | 7.250 | [6.83, 7.67] |

## Post-hoc vs control (control = IFPOA-X), adjusted p-values

z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; z < 0 means the other algorithm is better. Significant (p < 0.05) after correction shown in **bold**.

| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |
|---|---|---|---|---|---|
| IFPOA-X vs GWO | +4.25 | -4.25 | 2.138e-05 | **1.496e-04** | 1.496e-04 |
| IFPOA-X vs L-SHADE | +2.50 | -2.50 | 1.242e-02 | 7.452e-02 | 4.280e-02 |
| IFPOA-X vs PSO | +2.08 | -2.08 | 3.722e-02 | 1.861e-01 | 8.470e-02 |
| IFPOA-X vs TPE | +1.42 | -1.42 | 1.566e-01 | 4.697e-01 | 2.121e-01 |
| IFPOA-X vs DE | -0.83 | +0.83 | 4.047e-01 | 4.697e-01 | 4.047e-01 |
| IFPOA-X vs FPA | -1.42 | +1.42 | 1.566e-01 | 4.697e-01 | 2.121e-01 |
| IFPOA-X vs WOA | -2.00 | +2.00 | 4.550e-02 | 1.861e-01 | 8.470e-02 |

## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)

A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 favours IFPOA-X (smaller mean).

| Baseline | mean A12 | interpretation | mean Cohen's d |
|---|---|---|---|
| FPA | 0.723 | IFPOA-X better | -0.84 |
| PSO | 0.173 | baseline better | +1.22 |
| DE | 0.617 | IFPOA-X better | -0.64 |
| L-SHADE | 0.110 | baseline better | +1.94 |
| GWO | 0.026 | baseline better | +2.88 |
| WOA | 0.827 | IFPOA-X better | -1.55 |
| TPE | 0.270 | baseline better | +0.73 |