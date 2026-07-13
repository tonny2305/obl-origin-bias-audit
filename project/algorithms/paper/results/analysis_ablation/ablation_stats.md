# Ablation — Mean Best Fitness per Function x Variant (D=30, 500 NFE)

| Func | IFPOA-X (full) | IFPOA-X (no OBL) | IFPOA-X (no JADE) | IFPOA-X (no Bandit) | IFPOA-X (base/FPA) |
|---|---|---|---|---|---|
| F1 | 1.811e+00 | 1.643e+04 | 1.299e-08 | 1.868e+00 | 1.906e+04 |
| F5 | 3.128e+01 | 2.479e+07 | 2.892e+01 | 1.411e+02 | 2.591e+07 |
| F8 | 8.653e+03 | 8.716e+03 | 8.433e+03 | 8.656e+03 | 8.675e+03 |
| F9 | 1.602e+00 | 2.853e+02 | 1.437e-07 | 1.439e-01 | 2.982e+02 |
| F10 | 4.672e-01 | 1.811e+01 | 3.933e-05 | 3.037e-01 | 1.963e+01 |
| F13 | 3.275e+00 | 1.255e+08 | 2.942e+00 | 4.134e+00 | 7.333e+07 |

## Wilcoxon: full vs each ablated variant (per function, α=0.05)

| Func | IFPOA-X (no OBL) | IFPOA-X (no JADE) | IFPOA-X (no Bandit) | IFPOA-X (base/FPA) |
|---|---|---|---|---|
| F1 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F5 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F8 | = (n.s.) | = (n.s.) | = (n.s.) | = (n.s.) |
| F9 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F10 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F13 | full better (+) | variant better (−) | = (n.s.) | full better (+) |

**Recap (full wins / ablated-variant wins / ties):**
- IFPOA-X (no OBL): 5/0/1
- IFPOA-X (no JADE): 0/5/1
- IFPOA-X (no Bandit): 0/0/6
- IFPOA-X (base/FPA): 5/0/1