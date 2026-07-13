# Statistical Significance Tests

## Mann--Whitney U: IFPOA-X vs baseline (per function)

Win/loss summary for IFPOA-X (α=0.05): '+' significantly better, '−' worse, '=' not significant.

| Function | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|
| F1 | + | − | + | − | − | − | = |
| F2 | = | − | − | − | − | − | − |
| F3 | + | + | = | − | − | = | = |
| F4 | = | = | + | = | − | − | = |
| F5 | + | − | + | − | − | − | = |
| F6 | + | − | = | − | − | − | = |
| F7 | + | − | + | − | − | − | = |
| F8 | + | + | + | = | + | − | + |
| F9 | = | = | − | − | − | − | − |
| F10 | = | = | − | − | − | − | − |
| F11 | + | − | = | − | − | − | = |
| F12 | = | − | + | − | − | − | − |
| F13 | = | − | + | − | − | − | − |

**Recap (win/loss/tie) IFPOA-X:**
- vs FPA: 7/0/6
- vs PSO: 2/8/3
- vs DE: 7/3/3
- vs L-SHADE: 0/11/2
- vs GWO: 1/12/0
- vs WOA: 0/12/1
- vs TPE: 1/5/7

## Mean Rank (Friedman) & Critical Difference

Friedman: χ²=60.897, p=9.990e-11 (k=8 algorithms, N=13 functions)
Critical Difference (Nemenyi, α=0.05): CD = 2.912

| Algorithm | Mean Rank |
|---|---|
| WOA | 1.462 |
| GWO | 2.231 |
| L-SHADE | 3.385 |
| PSO | 4.769 |
| TPE | 4.923 |
| IFPOA-X | 5.769 |
| DE | 6.154 |
| FPA | 7.308 |