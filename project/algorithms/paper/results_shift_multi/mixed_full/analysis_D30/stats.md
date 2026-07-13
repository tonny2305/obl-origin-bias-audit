# Statistical Significance Tests

## Mann--Whitney U: IFPOA-X vs baseline (per function)

Win/loss summary for IFPOA-X (α=0.05): '+' significantly better, '−' worse, '=' not significant.

| Function | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|
| F1 | + | − | = | − | − | + | = |
| F2 | + | − | − | − | − | = | − |
| F3 | = | − | = | − | − | + | − |
| F4 | = | = | + | = | − | + | = |
| F5 | = | − | + | − | − | + | − |
| F6 | + | − | = | − | − | + | = |
| F7 | + | − | + | − | − | + | − |
| F9 | = | = | − | − | − | + | − |
| F10 | = | = | = | − | − | + | − |
| F11 | + | − | + | − | − | + | = |
| F12 | = | − | + | − | − | + | = |
| F13 | + | − | + | − | − | + | = |
| F8 | = | − | − | = | − | − | − |

**Recap (win/loss/tie) IFPOA-X:**
- vs FPA: 6/0/7
- vs PSO: 0/10/3
- vs DE: 6/3/4
- vs L-SHADE: 0/11/2
- vs GWO: 0/13/0
- vs WOA: 11/1/1
- vs TPE: 0/7/6

## Mean Rank (Friedman) & Critical Difference

Friedman: χ²=63.205, p=3.448e-11 (k=8 algorithms, N=13 functions)
Critical Difference (Nemenyi, α=0.05): CD = 2.912

| Algorithm | Mean Rank |
|---|---|
| GWO | 1.077 |
| L-SHADE | 3.077 |
| PSO | 3.308 |
| TPE | 3.769 |
| IFPOA-X | 5.308 |
| DE | 5.692 |
| FPA | 6.769 |
| WOA | 7.000 |