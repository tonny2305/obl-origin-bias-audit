# Ablation — Mean Best Fitness per Function x Variant (D=30, 500 NFE, 20 paired seeds)

| Func | IFPOA-X (full) | IFPOA-X (no OBL) | IFPOA-X (no JADE) | IFPOA-X (no Bandit) | IFPOA-X (base/FPA) |
|---|---|---|---|---|---|
| F1 | 1.811e+00 | 1.893e+04 | 1.335e-06 | 1.641e+00 | 2.017e+04 |
| F2 | 1.180e-01 | 4.847e+03 | 2.704e-05 | 1.332e-01 | 3.811e+03 |
| F3 | 2.046e+03 | 5.625e+04 | 2.298e+02 | 2.248e+03 | 5.815e+04 |
| F4 | 4.577e+00 | 6.326e+01 | 7.764e-03 | 4.484e+00 | 6.681e+01 |
| F5 | 3.128e+01 | 2.721e+07 | 2.894e+01 | 7.915e+01 | 2.339e+07 |
| F6 | 2.700e+00 | 1.824e+04 | 0.000e+00 | 5.450e+00 | 2.074e+04 |
| F7 | 4.509e-02 | 1.271e+01 | 2.726e-02 | 5.576e-02 | 1.440e+01 |
| F8 | 8.653e+03 | 8.672e+03 | 8.878e+03 | 8.611e+03 | 8.691e+03 |
| F9 | 1.602e+00 | 2.943e+02 | 7.328e-07 | 2.620e-01 | 3.052e+02 |
| F10 | 4.672e-01 | 1.856e+01 | 3.503e-04 | 7.346e-01 | 1.938e+01 |
| F11 | 6.955e-01 | 1.702e+02 | 2.153e-03 | 1.027e+00 | 1.910e+02 |
| F12 | 1.572e+00 | 2.608e+07 | 1.029e+00 | 1.623e+00 | 3.397e+07 |
| F13 | 3.275e+00 | 9.113e+07 | 2.910e+00 | 3.818e+00 | 9.149e+07 |

## Wilcoxon signed-rank: full vs each ablated variant (per function, α=0.05, paired by seed)

| Func | IFPOA-X (no OBL) | IFPOA-X (no JADE) | IFPOA-X (no Bandit) | IFPOA-X (base/FPA) |
|---|---|---|---|---|
| F1 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F2 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F3 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F4 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F5 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F6 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F7 | full better (+) | = (n.s.) | = (n.s.) | full better (+) |
| F8 | = (n.s.) | full better (+) | = (n.s.) | = (n.s.) |
| F9 | full better (+) | variant better (−) | variant better (−) | full better (+) |
| F10 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F11 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F12 | full better (+) | variant better (−) | = (n.s.) | full better (+) |
| F13 | full better (+) | variant better (−) | = (n.s.) | full better (+) |

**Recap (full wins / ablated-variant wins / ties):**
- IFPOA-X (no OBL): 12/0/1
- IFPOA-X (no JADE): 1/11/1
- IFPOA-X (no Bandit): 0/1/12
- IFPOA-X (base/FPA): 12/0/1