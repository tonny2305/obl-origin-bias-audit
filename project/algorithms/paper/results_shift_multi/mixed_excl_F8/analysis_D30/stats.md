# Uji Signifikansi Statistik

## Wilcoxon signed-rank: IFPOA-X vs baseline (per fungsi)

Ringkasan menang/kalah IFPOA-X (α=0,05): '+' unggul signifikan, '−' kalah, '=' tak signifikan.

| Fungsi | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|
| F1 | + | − | = | − | − | + | = |
| F2 | + | − | − | − | − | = | − |
| F3 | = | − | = | − | − | + | − |
| F4 | = | = | + | = | − | + | = |
| F5 | + | − | + | − | − | + | − |
| F6 | + | − | = | − | − | + | = |
| F7 | + | − | + | − | − | + | − |
| F9 | = | = | − | − | − | + | − |
| F10 | = | = | = | − | − | + | − |
| F11 | + | − | + | − | − | + | = |
| F12 | = | − | + | − | − | = | = |
| F13 | = | − | + | − | − | + | = |

**Rekap (menang/kalah/seri) IFPOA-X:**
- vs FPA: 6/0/6
- vs PSO: 0/9/3
- vs DE: 6/2/4
- vs L-SHADE: 0/11/1
- vs GWO: 0/12/0
- vs WOA: 10/0/2
- vs TPE: 0/6/6

## Peringkat Rata-rata (Friedman) & Critical Difference

Friedman: χ²=65.722, p=1.076e-11 (k=8 algoritma, N=12 fungsi)
Critical Difference (Nemenyi, α=0,05): CD = 3.031

| Algoritma | Peringkat Rata-rata |
|---|---|
| GWO | 1.000 |
| L-SHADE | 2.750 |
| PSO | 3.167 |
| TPE | 3.833 |
| IFPOA-X | 5.250 |
| DE | 6.083 |
| FPA | 6.667 |
| WOA | 7.250 |