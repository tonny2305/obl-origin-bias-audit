---
documentclass: extarticle
fontsize: 9pt
geometry:
  - landscape
  - margin=0.35in
header-includes:
  - \hfuzz=0.3pt
---

# Supplementary Material

*Supplementary tables and figures for* “When Does Opposition-Based Learning Actually Help? …”. *Numbers cross-reference the main text.*

## Supplementary Tables

**Supplementary Table S1. Parameter settings of the compared algorithms (population-based algorithms: population size = 24; all: $\mathrm{NFE}_{\max} = 500$; 20 independent runs for the classical, origin-shifted, CEC2017, ablation, and factorial analyses; 15 independent runs for the far and mixed controls).**

| Algorithm | Parameter | Value | Source |
|---|---|---|---|
| **IFPOA-X** | Bandit exploration constant $c$ | 1.4 | `bandit_c` |
| | Bandit reward signal | normalized HV gain | `bandit_reward = "hv"` |
| | Lévy stability index $\beta$ | 1.5 | `levy_beta` |
| | Initial step scale $c_0$ (bounds) | 0.15 ($[0.01, 0.5]$) | `c0` (`c_min`, `c_max`) |
| | Step anneal exponent $\eta$ | 1.5 | `eta_anneal` |
| | 1/5-rule target acceptance $\rho^\ast$ (adapt factors) | 0.20 (×1.15 / ×0.85) | `acc_target` (`c_adapt_delta`, `c_adapt_gamma`) |
| | OBL trigger frequency | every 3 evaluations | `obl_frequency` |
| | OBL elite pool size | top-3 (front-1, by crowding) | `obl_top_k` |
| | JADE p-best fraction | 20% | `jade_p` |
| | JADE $F$ (Cauchy), $CR$ (Normal) | $\mathrm{Cauchy}(0.5,0.1)$, $\mathcal{N}(0.5,0.1)$ | `jade_fmean`, `jade_cmean` |
| | JADE external archive size | 128 | `jade_arch_max` |
| | Pareto archive size | 64 | `archive_max` |
| | $k$-NN surrogate / ASHA pruning | **disabled** for this benchmark | `use_knn_screen = False` (see §3.4) |
| **FPA** | Switch probability $p$ | 0.8 | `p_switch` |
| | Local search scale $\gamma$ | 0.1 | `gamma` |
| | Global (Lévy) step scale | 0.25 | `levy_gamma` |
| **PSO** | Inertia weight $w$ | 0.7 | `w` |
| | Cognitive / social coefficients $c_1, c_2$ | 1.5, 1.5 | `c1`, `c2` |
| **DE** | Mutation factor $F$ (`wf`) | 0.1 *(mealpy default, not tuned)* | `mealpy DE.OriginalDE` |
| | Crossover rate $CR$ (`cr`) | 0.9 *(mealpy default, not tuned)* | idem |
| | Strategy | `rand/1/bin` (strategy = 0) | idem |
| **L-SHADE** | Initial $\mu_F$, $\mu_{CR}$ | 0.5, 0.5 *(mealpy default, not tuned)* | `mealpy SHADE.L_SHADE` |
| | Population reduction | linear (L-SHADE default schedule) | idem |
| **GWO** | — | parameter-free by design ($a$: linear $2\to0$) | `mealpy GWO.OriginalGWO` |
| **WOA** | — | parameter-free by design ($a$: linear $2\to0$; spiral $b=1$) | `mealpy WOA.OriginalWOA` |
| **TPE** | $n_{\text{startup\_trials}}$ | 10 *(optuna default, not tuned)* | `optuna.samplers.TPESampler` |
| | $n_{\text{ei\_candidates}}$ | 24 *(optuna default, not tuned)* | idem |
| | Prior weight, multivariate | 1.0, off *(optuna default)* | idem |

**Supplementary Table S2. Summary statistics of final fitness (mean, D=50, 500 NFE, 20 runs). Best in bold.**

| Func | IFPOA-X | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|---|
| F1 | **7.38e+00** | 1.08e+04 | 8.41e+03 | 5.37e+04 | 2.13e+04 | 5.49e+03 | 3.18e+02 | 6.23e+04 |
| F2 | **4.61e-01** | 6.08e+01 | 5.77e+01 | 5.37e+05 | 1.04e+05 | 4.89e+01 | 3.64e+00 | 1.91e+10 |
| F3 | **1.17e+04** | 3.92e+04 | 3.28e+04 | 1.01e+05 | 9.96e+04 | 4.92e+04 | 3.26e+05 | 1.24e+05 |
| F4 | **8.40e+00** | 3.31e+01 | 3.19e+01 | 7.21e+01 | 6.81e+01 | 4.54e+01 | 8.90e+01 | 7.61e+01 |
| F5 | **8.42e+01** | 4.75e+06 | 2.92e+06 | 1.22e+08 | 2.38e+07 | 2.71e+06 | 2.23e+06 | 1.58e+08 |
| F6 | **8.20e+00** | 1.07e+04 | 8.67e+03 | 5.35e+04 | 2.20e+04 | 5.54e+03 | 1.76e+02 | 6.20e+04 |
| F7 | **9.00e-02** | 4.06e+00 | 2.63e+00 | 8.69e+01 | 2.11e+01 | 2.36e+00 | 1.41e+00 | 1.13e+02 |
| F8 | 1.59e+04 | 1.69e+04 | 1.54e+04 | 1.41e+04 | 1.64e+04 | 1.70e+04 | **6.29e+03** | 1.43e+04 |
| F9 | **4.47e+00** | 4.17e+02 | 3.80e+02 | 4.98e+02 | 4.95e+02 | 4.25e+02 | 2.48e+02 | 5.68e+02 |
| F10 | **6.38e-01** | 1.36e+01 | 1.31e+01 | 1.91e+01 | 1.69e+01 | 1.15e+01 | 2.08e+00 | 1.96e+01 |
| F11 | **9.22e-01** | 9.85e+01 | 7.67e+01 | 4.84e+02 | 1.93e+02 | 5.04e+01 | 3.86e+00 | 5.62e+02 |
| F12 | **1.40e+00** | 3.49e+05 | 1.58e+05 | 1.90e+08 | 1.82e+07 | 3.99e+05 | 2.12e+07 | 2.30e+08 |
| F13 | **6.30e+00** | 6.02e+06 | 3.09e+06 | 4.15e+08 | 5.69e+07 | 1.55e+06 | 5.32e+06 | 5.52e+08 |
| **Mean rank** | **1.31** | 4.69 | 3.46 | 6.38 | 5.92 | 3.77 | 3.00 | 7.46 |

**Supplementary Table S3. IFPOA-X vs baseline — per-function win/loss/tie (Mann–Whitney U, $\alpha=0.05$, D=30). Per-function outcomes, not a cross-function significance claim (see §5.1).**

| Baseline | Win | Loss | Tie |
|---|---|---|---|
| FPA | 13 | 0 | 0 |
| PSO | 12 | 0 | 1 |
| DE | 12 | 1 | 0 |
| L-SHADE | 13 | 0 | 0 |
| GWO | 13 | 0 | 0 |
| WOA | 12 | 1 | 0 |
| TPE | 12 | 1 | 0 |

**Supplementary Table S4. Native-optimum verification of the shift transform (representative functions; full list in `verify_shift.py`).** Residual is $|g(o)|$ at the shifted optimum; F7 is stochastic (noise term), so its residual reflects the noise floor.

| Function | Native optimum $x_0$ | Shifted optimum $o$ (per-dim range) | $\min f$ | Verified $|g(o)|$ |
|---|---|---|---|---|
| F1 Sphere | $\mathbf{0}$ | 30–70% of $[-100,100]$ | 0 | 0.0e+00 |
| F5 Rosenbrock | $\mathbf{1}$ | 30–70% of $[-30,30]$ | 0 | 0.0e+00 |
| F8 Schwefel 2.26 | $420.97\cdot\mathbf{1}$ | in-bounds target | 0 | 8.1e-09 |
| F10 Ackley | $\mathbf{0}$ | 30–70% of $[-32,32]$ | 0 | 4.4e-16 |
| F12 Penalized 1 | $-\mathbf{1}$ | 30–70% of $[-50,50]$ | 0 | 3.6e-32 |
| F13 Penalized 2 | $\mathbf{1}$ | 30–70% of $[-50,50]$ | 0 | 1.4e-32 |

<!-- GENERATED_STATS_START -->

## Complete statistical results promised in the main manuscript

All entries below are regenerated from the released raw CSV files. External inter-algorithm effects use independent run samples; ranks use the per-function medians.

**Supplementary Table S5. CEC2017 final error: median [Q1, Q3] over 20 independent runs (D=30, 500 NFE).**

| Function | IFPOA-X | FPA | PSO | DE | L-SHADE | GWO | WOA | TPE |
|---|---|---|---|---|---|---|---|---|
| F1 | 4.062e+10 [3.853e+10, 4.665e+10] | 5.437e+10 [4.715e+10, 6.051e+10] | 2.803e+10 [2.409e+10, 3.322e+10] | 5.142e+10 [4.053e+10, 5.895e+10] | 2.162e+10 [1.835e+10, 2.415e+10] | 9.577e+09 [7.111e+09, 1.270e+10] | 5.666e+10 [5.179e+10, 6.500e+10] | 4.244e+10 [3.724e+10, 4.666e+10] |
| F3 | 8.068e+03 [6.392e+03, 9.694e+03] | 1.186e+04 [9.624e+03, 1.441e+04] | 4.488e+03 [3.195e+03, 5.765e+03] | 9.902e+03 [7.698e+03, 1.207e+04] | 3.592e+03 [2.690e+03, 3.940e+03] | 1.335e+03 [8.138e+02, 1.889e+03] | 1.868e+04 [1.424e+04, 2.002e+04] | 6.370e+03 [5.194e+03, 7.983e+03] |
| F4 | 5.659e+04 [4.588e+04, 6.191e+04] | 7.496e+04 [6.484e+04, 8.533e+04] | 3.154e+04 [2.675e+04, 4.431e+04] | 5.408e+04 [4.829e+04, 7.417e+04] | 2.569e+04 [2.203e+04, 3.000e+04] | 1.277e+04 [1.018e+04, 1.786e+04] | 8.117e+04 [7.373e+04, 8.859e+04] | 5.295e+04 [3.955e+04, 5.703e+04] |
| F5 | 5.314e-02 [4.414e-02, 6.599e-02] | 4.316e-02 [3.479e-02, 5.114e-02] | 2.436e-02 [2.109e-02, 3.373e-02] | 3.259e-02 [2.479e-02, 4.367e-02] | 5.752e-02 [4.703e-02, 6.310e-02] | 2.363e-02 [1.474e-02, 4.678e-02] | 5.170e-02 [4.159e-02, 6.438e-02] | 3.111e-02 [2.078e-02, 3.485e-02] |
| F7 | 7.475e+02 [6.891e+02, 7.760e+02] | 6.347e+02 [5.837e+02, 7.425e+02] | 6.458e+02 [5.893e+02, 7.019e+02] | 6.812e+02 [5.659e+02, 7.326e+02] | 6.457e+02 [6.119e+02, 6.925e+02] | 5.875e+02 [5.170e+02, 6.326e+02] | 8.318e+02 [7.698e+02, 8.739e+02] | 6.335e+02 [6.002e+02, 6.924e+02] |
| F9 | 8.305e+03 [7.893e+03, 8.598e+03] | 7.951e+03 [7.681e+03, 8.383e+03] | 7.574e+03 [7.250e+03, 7.875e+03] | 8.371e+03 [7.992e+03, 8.660e+03] | 8.626e+03 [8.296e+03, 8.901e+03] | 8.283e+03 [8.161e+03, 8.731e+03] | 7.839e+03 [7.410e+03, 8.063e+03] | 8.440e+03 [8.025e+03, 8.642e+03] |
| F10 | 7.471e+08 [4.922e+08, 1.154e+09] | 2.809e+09 [1.646e+09, 3.837e+09] | 8.307e+07 [3.932e+07, 1.245e+08] | 1.929e+09 [5.577e+08, 3.171e+09] | 1.161e+08 [6.444e+07, 1.904e+08] | 2.237e+06 [8.857e+05, 1.619e+07] | 3.050e+09 [1.296e+09, 3.736e+09] | 2.015e+08 [8.033e+07, 3.210e+08] |
| F11 | 5.014e+09 [4.562e+09, 5.695e+09] | 1.154e+10 [8.322e+09, 1.486e+10] | 1.786e+09 [1.291e+09, 2.212e+09] | 5.714e+09 [3.863e+09, 7.725e+09] | 1.738e+09 [1.504e+09, 2.221e+09] | 3.251e+08 [2.390e+08, 5.845e+08] | 9.944e+09 [8.075e+09, 1.307e+10] | 2.756e+09 [1.865e+09, 3.504e+09] |
| F14 | 2.300e+09 [1.789e+09, 2.844e+09] | 6.213e+09 [5.131e+09, 6.990e+09] | 3.805e+08 [1.861e+08, 8.709e+08] | 2.332e+09 [1.370e+09, 4.706e+09] | 6.469e+08 [5.068e+08, 7.526e+08] | 3.147e+07 [1.666e+07, 8.700e+07] | 4.554e+09 [3.116e+09, 6.847e+09] | 7.398e+08 [5.495e+08, 9.908e+08] |
| F21 | 9.015e+02 [7.276e+02, 1.058e+03] | 2.542e+03 [2.301e+03, 2.985e+03] | 6.869e+02 [6.037e+02, 8.620e+02] | 1.313e+03 [9.916e+02, 2.136e+03] | 4.705e+02 [4.387e+02, 5.432e+02] | 3.407e+02 [3.065e+02, 3.978e+02] | 3.092e+03 [2.200e+03, 4.215e+03] | 9.018e+02 [8.134e+02, 9.890e+02] |

**Supplementary Table S6. CEC2017 mean Friedman ranks and 95% bootstrap confidence intervals (5000 resamples over functions).**

| Algorithm | Mean rank | 95% CI |
|---|---|---|
| GWO | 1.300 | [1.00, 1.90] |
| PSO | 2.700 | [2.10, 3.30] |
| L-SHADE | 3.600 | [2.40, 5.20] |
| TPE | 4.200 | [3.40, 5.00] |
| IFPOA-X | 5.300 | [4.70, 5.90] |
| DE | 5.700 | [5.30, 6.00] |
| FPA | 6.200 | [5.00, 7.20] |
| WOA | 7.000 | [5.60, 7.80] |

**Supplementary Table S7. CEC2017 post-hoc comparisons against IFPOA-X (two-sided normal approximation to mean-rank differences).**

| Comparison | Delta rank | z | p raw | p Holm | p Finner |
|---|---|---|---|---|---|
| IFPOA-X vs GWO | +4.00 | -3.65 | 2.607e-04 | 1.825e-03 | 1.824e-03 |
| IFPOA-X vs PSO | +2.60 | -2.37 | 1.762e-02 | 1.057e-01 | 6.033e-02 |
| IFPOA-X vs L-SHADE | +1.70 | -1.55 | 1.207e-01 | 6.035e-01 | 2.593e-01 |
| IFPOA-X vs TPE | +1.10 | -1.00 | 3.153e-01 | 9.459e-01 | 4.116e-01 |
| IFPOA-X vs DE | -0.40 | +0.37 | 7.150e-01 | 9.459e-01 | 7.150e-01 |
| IFPOA-X vs FPA | -0.90 | +0.82 | 4.113e-01 | 9.459e-01 | 4.611e-01 |
| IFPOA-X vs WOA | -1.70 | +1.55 | 1.207e-01 | 6.035e-01 | 2.593e-01 |

**Supplementary Table S8. CEC2017 independent-sample effect sizes (mean over functions).**

| Baseline | Vargha-Delaney A12 | Mean Cohen's d |
|---|---|---|
| FPA | 0.724 | -1.05 |
| PSO | 0.132 | +1.56 |
| DE | 0.556 | -0.27 |
| L-SHADE | 0.158 | +1.87 |
| GWO | 0.083 | +2.89 |
| WOA | 0.799 | -1.38 |
| TPE | 0.276 | +0.94 |

**Supplementary Table S9. Classical-suite mean Friedman ranks and 95% bootstrap confidence intervals (5000 resamples over functions).**

| Dimension | Algorithm | Mean rank | 95% CI |
|---|---|---|---|
| D=30 | IFPOA-X | 1.308 | [1.00, 1.92] |
| D=30 | GWO | 3.231 | [2.62, 4.15] |
| D=30 | WOA | 3.385 | [2.23, 4.69] |
| D=30 | PSO | 3.615 | [3.15, 4.08] |
| D=30 | FPA | 4.692 | [4.23, 5.23] |
| D=30 | L-SHADE | 6.000 | [5.77, 6.23] |
| D=30 | DE | 6.385 | [5.69, 6.92] |
| D=30 | TPE | 7.385 | [6.38, 8.00] |
| D=50 | IFPOA-X | 1.308 | [1.00, 1.92] |
| D=50 | WOA | 3.000 | [1.92, 4.31] |
| D=50 | PSO | 3.462 | [3.00, 3.85] |
| D=50 | GWO | 3.769 | [3.15, 4.62] |
| D=50 | FPA | 4.692 | [4.08, 5.31] |
| D=50 | L-SHADE | 5.923 | [5.77, 6.00] |
| D=50 | DE | 6.385 | [5.46, 7.00] |
| D=50 | TPE | 7.462 | [6.62, 8.00] |

**Supplementary Table S10. Classical-suite post-hoc comparisons against IFPOA-X.**

| Dimension | Comparison | Delta rank | z | p raw | p Holm | p Finner |
|---|---|---|---|---|---|---|
| D=30 | IFPOA-X vs GWO | -1.92 | +2.00 | 4.533e-02 | 6.128e-02 | 4.533e-02 |
| D=30 | IFPOA-X vs WOA | -2.08 | +2.16 | 3.064e-02 | 6.128e-02 | 3.565e-02 |
| D=30 | IFPOA-X vs PSO | -2.31 | +2.40 | 1.631e-02 | 4.893e-02 | 2.276e-02 |
| D=30 | IFPOA-X vs FPA | -3.38 | +3.52 | 4.270e-04 | 1.708e-03 | 7.471e-04 |
| D=30 | IFPOA-X vs L-SHADE | -4.69 | +4.88 | 1.040e-06 | 5.200e-06 | 2.427e-06 |
| D=30 | IFPOA-X vs DE | -5.08 | +5.28 | 1.262e-07 | 7.574e-07 | 4.418e-07 |
| D=30 | IFPOA-X vs TPE | -6.08 | +6.33 | 2.531e-10 | 1.772e-09 | 1.772e-09 |
| D=50 | IFPOA-X vs WOA | -1.69 | +1.76 | 7.817e-02 | 7.817e-02 | 7.817e-02 |
| D=50 | IFPOA-X vs PSO | -2.15 | +2.24 | 2.497e-02 | 4.995e-02 | 2.908e-02 |
| D=50 | IFPOA-X vs GWO | -2.46 | +2.56 | 1.041e-02 | 3.122e-02 | 1.454e-02 |
| D=50 | IFPOA-X vs FPA | -3.38 | +3.52 | 4.270e-04 | 1.708e-03 | 7.471e-04 |
| D=50 | IFPOA-X vs L-SHADE | -4.62 | +4.80 | 1.556e-06 | 7.782e-06 | 3.632e-06 |
| D=50 | IFPOA-X vs DE | -5.08 | +5.28 | 1.262e-07 | 7.574e-07 | 4.418e-07 |
| D=50 | IFPOA-X vs TPE | -6.15 | +6.41 | 1.502e-10 | 1.052e-09 | 1.052e-09 |

**Supplementary Table S11. Classical-suite independent-sample effect sizes (mean over functions).**

| Dimension | Baseline | Vargha-Delaney A12 | Mean Cohen's d |
|---|---|---|---|
| D=30 | FPA | 0.980 | -4.90 |
| D=30 | PSO | 0.946 | -5.12 |
| D=30 | DE | 0.925 | -7.76 |
| D=30 | L-SHADE | 0.979 | -8.27 |
| D=30 | GWO | 0.993 | -3.88 |
| D=30 | WOA | 0.877 | -2.10 |
| D=30 | TPE | 0.924 | -10.33 |
| D=50 | FPA | 0.983 | -6.73 |
| D=50 | PSO | 0.936 | -5.42 |
| D=50 | DE | 0.924 | -8.16 |
| D=50 | L-SHADE | 0.988 | -9.12 |
| D=50 | GWO | 0.983 | -4.46 |
| D=50 | WOA | 0.848 | -1.83 |
| D=50 | TPE | 0.924 | -11.66 |

<!-- GENERATED_STATS_END -->

## Supplementary Figures

**Supplementary Figure S1. Rank distribution per (function, run) for each algorithm (D=30).**

![Rank boxplot](figures/rank_boxplot_D30.png)

**Supplementary Figure S2. Mean rank (Friedman) per algorithm, D=30 vs D=50.**

![Scalability](figures/scalability_D30_D50.png)

## Implementation Details

### Computational complexity

Per iteration, IFPOA-X performs: one incumbent (re-)evaluation subject to $O(1)$ amortized cost via memoized caching on $(\theta, \text{rung})$; a JADE mutation in $O(D)$; an OBL trigger every 3 iterations costing $O(D)$ for the opposite computation plus $O(|\mathcal{F}_1|\log|\mathcal{F}_1|)$ for non-dominated sorting and crowding-distance ranking of the elite pool, where $|\mathcal{F}_1|$ is the size of the current Pareto front; a Pareto-archive update in $O(|\mathcal{A}|)$ (or $O(|\mathcal{A}|\log|\mathcal{A}|)$ when trimming by crowding distance once the archive exceeds `archive_max` $=64$); and an $O(1)$ bandit index update. When the optional $k$-NN screen is enabled (disabled in this paper's experiments, §3.4), each screened candidate adds $O(N \cdot D)$ for a brute-force nearest-neighbour query over $N$ stored surrogate points. Overall, the per-iteration overhead beyond the objective evaluation itself is dominated by $O(D + |\mathcal{A}|\log|\mathcal{A}|)$, which is negligible relative to the cost of a single real evaluation in the expensive-optimization regime this paper targets — precisely the assumption that justifies trading a modest bookkeeping overhead for improved sample efficiency.

### Full algorithm (pseudocode)

**Algorithm S1.** IFPOA-X (single-objective instantiation used in this paper)

```
Input: budget NFE_max, population size N, dimension D
Output: best solution found

1:  Initialize population {u_1, ..., u_N} via Latin Hypercube Sampling in [0,1]^D
2:  t <- 0;  archive <- empty;  bandit stats <- {N_global=0, N_local=0, R_global=0, R_local=0}
3:  while t < NFE_max do
4:      idx <- select an unevaluated (or stalest-evaluated) individual
5:      fit <- Evaluate(u_idx)                      // real evaluation (or cache hit)
6:      t <- t + 1
7:      Update Pareto archive and best-so-far with (u_idx, fit)
8:      if t mod obl_frequency == 0 then
9:          u_elite <- random draw from top-k elite pool (archive front-1, by crowding)
10:         u_opp <- 1 - u_elite                     // OBL opposite
11:         fit_opp <- Evaluate(u_opp);  t <- t + 1  // consumes 1 NFE
12:         if u_opp not dominated by cohort-worst then replace cohort-worst with u_opp
13:     end if
14:     a <- SelectArm_UCB1(bandit stats, c=1.4)      // "global" or "local"
15:     c_t <- CalibrateStepSize(t, accept_history)    // anneal + 1/5-rule
16:     if a == "global" then
17:         u_child <- clip(u_idx + c_t * LevyStep(beta=1.5), 0, 1)
18:     else
19:         F ~ Cauchy(0.5, 0.1);  CR ~ Normal(0.5, 0.1)
20:         u_pbest <- sample from top-20% of archive front-1
21:         u_r1, u_r2 <- sample distinct from population union external archive
22:         u_child <- CurrentToPBest1(u_idx, u_pbest, u_r1, u_r2, F, CR)   // JADE
23:     end if
24:     [optional: if surrogate screen enabled, discard u_child if predicted-unpromising]
25:     fit_child <- Evaluate(u_child);  t <- t + 1
26:     Update Pareto archive and best-so-far with (u_child, fit_child)
27:     reward <- clip((HV_after - HV_before) / A_ref, 0, 1)
28:     UpdateBandit(a, reward)
29: end while
30: return best-so-far
```
