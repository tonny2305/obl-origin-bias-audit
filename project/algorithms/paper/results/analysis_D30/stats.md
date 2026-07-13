# Statistical Significance Tests

## Mann--Whitney U: IFPOA-X vs baseline (per function)

Win/loss summary for IFPOA-X (α=0.05): '+' significantly better, '−' worse, '=' not significant.

| Function | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|
| F1 | + | + | + | + | + | + | + |
| F2 | + | + | + | + | + | + | + |
| F3 | + | + | + | + | + | + | + |
| F4 | + | + | + | + | + | + | + |
| F5 | + | + | + | + | + | + | + |
| F6 | + | + | + | + | + | + | + |
| F7 | + | + | + | + | + | + | + |
| F8 | + | = | − | + | + | − | − |
| F9 | + | + | + | + | + | + | + |
| F10 | + | + | + | + | + | + | + |
| F11 | + | + | + | + | + | + | + |
| F12 | + | + | + | + | + | + | + |
| F13 | + | + | + | + | + | + | + |

**Recap (win/loss/tie) IFPOA-X:**
- vs FPA: 13/0/0
- vs PSO: 12/0/1
- vs DE: 12/1/0
- vs L-SHADE: 13/0/0
- vs GWO: 13/0/0
- vs WOA: 12/1/0
- vs TPE: 12/1/0

## Mean Rank (Friedman) & Critical Difference

Friedman: χ²=60.641, p=1.124e-10 (k=8 algorithms, N=13 functions)
Critical Difference (Nemenyi, α=0.05): CD = 2.912

| Algorithm | Mean Rank |
|---|---|
| IFPOA-X | 1.308 |
| GWO | 3.231 |
| WOA | 3.385 |
| PSO | 3.615 |
| FPA | 4.692 |
| L-SHADE | 6.000 |
| DE | 6.385 |
| TPE | 7.385 |