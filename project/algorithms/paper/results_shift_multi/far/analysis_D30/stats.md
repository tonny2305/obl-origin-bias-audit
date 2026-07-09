# Uji Signifikansi Statistik

## Wilcoxon signed-rank: IFPOA-X vs baseline (per fungsi)

Ringkasan menang/kalah IFPOA-X (α=0,05): '+' unggul signifikan, '−' kalah, '=' tak signifikan.

| Fungsi | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|
| F1 | + | = | + | − | − | − | = |
| F2 | + | = | − | − | = | − | − |
| F3 | + | = | + | = | = | − | + |
| F4 | = | = | + | = | − | − | = |
| F5 | + | − | = | − | − | − | − |
| F6 | + | − | + | − | − | − | = |
| F7 | + | = | = | − | − | − | − |
| F8 | = | − | − | + | + | = | − |
| F9 | + | + | − | − | − | − | = |
| F10 | + | = | = | = | = | − | − |
| F11 | + | − | + | − | − | − | + |
| F12 | + | − | + | − | − | − | = |
| F13 | + | − | = | − | − | − | = |

**Rekap (menang/kalah/seri) IFPOA-X:**
- vs FPA: 11/0/2
- vs PSO: 1/6/6
- vs DE: 6/3/4
- vs L-SHADE: 1/9/3
- vs GWO: 1/9/3
- vs WOA: 0/12/1
- vs TPE: 2/5/6

## Peringkat Rata-rata (Friedman) & Critical Difference

Friedman: χ²=55.051, p=1.456e-09 (k=8 algoritma, N=13 fungsi)
Critical Difference (Nemenyi, α=0,05): CD = 2.912

| Algoritma | Peringkat Rata-rata |
|---|---|
| WOA | 1.231 |
| GWO | 3.154 |
| L-SHADE | 3.615 |
| PSO | 4.538 |
| TPE | 4.769 |
| IFPOA-X | 5.231 |
| DE | 5.846 |
| FPA | 7.615 |