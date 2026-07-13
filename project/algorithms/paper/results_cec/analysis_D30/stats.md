# Statistical Significance Tests

## Mann--Whitney U: IFPOA-X vs baseline (per function)

Win/loss summary for IFPOA-X (α=0.05): '+' significantly better, '−' worse, '=' not significant.

| Function | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|
| F1 | + | − | + | − | − | + | = |
| F3 | + | − | = | − | − | + | = |
| F4 | + | − | = | − | − | + | = |
| F5 | − | − | − | = | − | = | − |
| F7 | − | − | − | − | − | + | − |
| F9 | = | − | = | + | = | − | = |
| F10 | + | − | = | − | − | + | − |
| F11 | + | − | = | − | − | + | − |
| F14 | + | − | = | − | − | + | − |
| F21 | + | = | + | − | − | + | = |

**Recap (win/loss/tie) IFPOA-X:**
- vs FPA: 7/2/1
- vs PSO: 0/9/1
- vs DE: 2/2/6
- vs L-SHADE: 1/8/1
- vs GWO: 0/9/1
- vs WOA: 8/1/1
- vs TPE: 0/5/5

## Mean Rank (Friedman) & Critical Difference

Friedman: χ²=42.667, p=3.868e-07 (k=8 algorithms, N=10 functions)
Critical Difference (Nemenyi, α=0.05): CD = 3.320

| Algorithm | Mean Rank |
|---|---|
| GWO | 1.300 |
| PSO | 2.700 |
| L-SHADE | 3.600 |
| TPE | 4.200 |
| IFPOA-X | 5.300 |
| DE | 5.700 |
| FPA | 6.200 |
| WOA | 7.000 |