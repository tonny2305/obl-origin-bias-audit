# Statistical Significance Tests

## Mann--Whitney U: IFPOA-X vs baseline (per function)

Win/loss summary for IFPOA-X (α=0.05): '+' significantly better, '−' worse, '=' not significant.

| Function | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|
| F1 | + | = | + | − | − | − | = |
| F2 | + | = | − | − | − | − | − |
| F3 | + | = | + | − | = | − | + |
| F4 | = | = | + | = | − | − | = |
| F5 | + | − | = | − | − | − | − |
| F6 | + | − | + | − | − | − | = |
| F7 | + | = | + | − | − | − | − |
| F8 | = | − | − | + | + | = | − |
| F9 | + | + | − | − | − | − | = |
| F10 | + | = | = | = | = | − | − |
| F11 | + | − | + | − | − | − | + |
| F12 | + | − | + | − | − | − | = |
| F13 | + | − | = | − | − | − | = |

**Recap (win/loss/tie) IFPOA-X:**
- vs FPA: 11/0/2
- vs PSO: 1/6/6
- vs DE: 7/3/3
- vs L-SHADE: 1/10/2
- vs GWO: 1/10/2
- vs WOA: 0/12/1
- vs TPE: 2/5/6

## Mean Rank (Friedman) & Critical Difference

Friedman: χ²=55.051, p=1.456e-09 (k=8 algorithms, N=13 functions)
Critical Difference (Nemenyi, α=0.05): CD = 2.912

| Algorithm | Mean Rank |
|---|---|
| WOA | 1.231 |
| GWO | 3.154 |
| L-SHADE | 3.615 |
| PSO | 4.538 |
| TPE | 4.769 |
| IFPOA-X | 5.231 |
| DE | 5.846 |
| FPA | 7.615 |