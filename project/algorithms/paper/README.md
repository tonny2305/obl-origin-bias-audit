# Reproduction Package — Origin-Bias Audit of Opposition-Based Learning (IFPOA-X)

This directory contains everything needed to reproduce the experiments in the
paper *"When Does Opposition-Based Learning Actually Help? An
Origin-Bias-Controlled Study of a Hybrid Flower Pollination Algorithm
(IFPOA-X) under Tight Evaluation Budgets."*

The study compares **IFPOA-X** against seven baselines (FPA, PSO, DE, L-SHADE,
GWO, WOA, TPE) under a strict **equal-NFE** protocol (500 real objective
evaluations, 20 independent runs) across three benchmark suites, and audits
whether IFPOA-X's advantage is genuine or an artifact of benchmark geometry.

> **Note on scope.** The IFPOA-X implementation (`../ifpoax.py`) also contains an
> optional k-NN surrogate screen, ASHA multi-fidelity pruning, and a
> multi-objective/hypervolume archive. These are **disabled** for every
> experiment in this paper (the benchmark objectives are cheap, so a surrogate
> adds net overhead). All results below use the single-objective,
> surrogate-off, ASHA-off configuration.

## 1. Environment

```
Python 3.11.9
numpy 1.26.0      scipy 1.16.3     pandas 2.3.3     matplotlib 3.10.8
mealpy 3.0.3      optuna 4.7.0     opfunu 1.0.4
```

`mealpy` provides the DE/L-SHADE/GWO/WOA baselines; `optuna` provides the TPE
(Bayesian-Optimization) baseline; `opfunu` provides the official CEC2017
shifted+rotated functions. Install with:

```
pip install numpy scipy pandas matplotlib mealpy==3.0.3 optuna opfunu
```

## 2. Determinism / seeds

Every run `r` (0-indexed) uses `seed = r * 1000` for both the Python `random`
module and NumPy, applied identically to all algorithms and all suites. Runs are
therefore **paired across algorithms and across ablation variants** (same seed →
same initial population and same objective-noise stream), which is what the
Wilcoxon signed-rank and paired-ablation analyses require. The equal-NFE cap is
enforced in the harness (`../benchmark_tester.py`, `max_real_evals=budget`), so
IFPOA-X's evaluation cache cannot consume budget without a real evaluation.

## 3. Benchmark suites

| Suite | Module | Optima | Purpose |
|---|---|---|---|
| Classical F1–F13 (Yao et al. 1999) | `functions.py` | at/near origin | main comparison (§5.1–§5.6) |
| Origin-shifted F1–F13 (Control 1) | `functions_shifted.py` | displaced 30–70% of radius, unsigned | origin-bias control (§5.7.1) |
| CEC2017, subset of 10 fns (Control 2) | `functions_cec.py` | shifted **and** rotated (official) | origin-bias control, community-standard (§5.7.2) |
| Shifted "far" (Control 3) | `functions_shifted.make_functions` | displaced 60–90%, unsigned | shift-magnitude robustness (§5.7.3) |
| Shifted "mixed" (Control 4) | `functions_shifted.make_functions` | displaced 30–70%, signed (±) | shift-direction robustness (§5.7.3); F8 excluded, see note in §4 |

The shift transform is a pure translation `g(x) = f(x - o)`; because every
F1–F13 function is non-negative on all of ℝⁿ with global minimum 0, translation
provably preserves the global minimizer at `x* + o` with value 0. This is
verified numerically per function by `verify_shift.py` (including the
non-origin-optimum Rosenbrock and penalized functions).

## 4. Reproducing each result

Run all commands from this directory. Each writes to its own `results*/` folder.

```bash
PY=../../../.venv/Scripts/python.exe    # or your interpreter

# --- verification (fast) ---
$PY verify_shift.py                     # proves shifts preserve optima
$PY functions.py                        # F1-F13 minima self-test
$PY functions_shifted.py                # shifted-suite self-test
$PY functions_cec.py                    # CEC2017 self-test
$PY baselines.py                        # equal-NFE compliance self-test

# --- main experiments (each: 8 algos x fns x 20 runs, ~hours) ---
$PY run_benchmark.py --dims 30 50 --budget 500 --runs 20    # -> results/
$PY run_shifted.py   --dims 30       --budget 500 --runs 20 # -> results_shifted/
$PY run_cec.py       --dims 30       --budget 500 --runs 20 # -> results_cec/
$PY run_multishift.py                --budget 500 --runs 15 # -> results_shift_multi/{far,mixed}/

# --- ablation (component contribution; reuses 'full' runs from results/) ---
$PY ablation.py --runs 20 --out results/ablation_full_D30.csv

# --- analysis: descriptive + Wilcoxon/Friedman/CD + convergence figures ---
$PY analyze.py --dims 30 50 --results results
$PY analyze.py --dims 30    --results results_shifted
$PY analyze.py --dims 30    --results results_cec

# --- advanced statistics (Iman-Davenport, Holm/Finner, A12, Cohen d, CI) ---
$PY stats_advanced.py --results results                    --dims 30 50
$PY stats_advanced.py --results results_shifted             --dims 30
$PY stats_advanced.py --results results_cec                 --dims 30
$PY stats_advanced.py --results results_shift_multi/far     --dims 30
$PY stats_advanced.py --results results_shift_multi/mixed_full --dims 30

# --- extra figures (rank boxplot, scalability), ablation figure, cross-suite synthesis ---
$PY extra_figures.py
$PY ablation_analyze.py --csv results/ablation_full_D30.csv
$PY synthesis_figure.py     # requires results{,_shifted,_cec,_shift_multi/{far,mixed_full}} to exist

# --- domain-safe F8 fix for the "mixed" (signed) multi-shift config ---
$PY rerun_f8_mixed.py       # re-evaluates F8 with a domain-clamped construction
$PY merge_f8_mixed.py       # merges the fix into results_shift_multi/mixed_full/
```

**Note on the "mixed" F8 fix:** the "mixed" multi-shift configuration (signed
displacement) can push F8's evaluation argument outside the domain in which
its closed-form global-minimum guarantee is proven, producing invalid
negative fitness values for that function only (the other 12 functions are
non-negative on all of R^D and are unaffected). `rerun_f8_mixed.py` gives F8
a domain-safe clamped construction (same off-centre optimum, no evaluation
leaves the valid domain) and `merge_f8_mixed.py` merges the result into
`results_shift_multi/mixed_full/raw_D30.csv` — the dataset actually used in
the final analysis, with **no function excluded**. Control 1 (`results_shifted/`)
and Control 3 ("far") do not exhibit this issue.

## 5. Output layout

```
results{,_shifted,_cec}/
  raw_D{dim}.csv                  # Function, Algorithm, Run, Best  (all raw values)
  curves_D{dim}.npz               # per (function,algorithm): runs x budget best-so-far
  analysis_D{dim}/
    summary.md / summary.csv      # best/worst/mean/std/median per function x algorithm
    stats.md                      # Wilcoxon per function + Friedman + mean ranks
    stats_advanced.md             # Iman-Davenport, Kendall W, Holm/Finner, A12, Cohen d, CI
    cd_diagram.png                # Nemenyi critical-difference diagram
    convergence_grid.png          # mean convergence, equal-NFE axis
results_shift_multi/
  far/                             # Control 3: shift 60-90%, unsigned
  mixed/                           # Control 4 raw data + the F8 domain-safe fix
  mixed_full/                      # Control 4 FINAL merged dataset (all 13 functions, used in analysis)
```

All figures are generated at **300 DPI PNG** plus a companion **vector PDF**
(same basename) for print-quality double-column typesetting; all figure text
(titles, axis labels, legends) is English-only, with larger fonts than
matplotlib defaults specifically so subplot titles/tick labels stay legible
after a double-column journal layout shrinks the figure.

## 6. Files

| File | Role |
|---|---|
| `../benchmark_tester.py` | equal-NFE harness for IFPOA-X/FPA/PSO (algorithms unchanged) |
| `../ifpoax.py`, `../fpa.py`, `../pso.py` | algorithm implementations (**never modified** for this study) |
| `functions.py` | classical F1–F13 |
| `functions_shifted.py` | origin-shifted F1–F13 (+ `make_functions` for multi-shift) |
| `functions_cec.py` | CEC2017 subset via opfunu (error-to-optimum) |
| `baselines.py` | DE/L-SHADE/GWO/WOA (mealpy) + TPE (optuna) equal-NFE adapters |
| `run_benchmark.py`, `run_shifted.py`, `run_cec.py`, `run_multishift.py` | experiment runners |
| `ablation.py`, `ablation_analyze.py` | component ablation (OBL / JADE / bandit), all 13 functions x 20 paired runs |
| `analyze.py`, `stats_advanced.py` | descriptive + Wilcoxon/Friedman/CD stats; advanced stats (Iman-Davenport, Holm/Finner, A12, Cohen d, bootstrap CI) |
| `extra_figures.py` | rank-distribution boxplot, D=30-vs-D=50 scalability figure |
| `synthesis_figure.py` | cross-suite summary figure (Figure 9): IFPOA-X rank under all 4 origin-bias controls |
| `verify_shift.py` | mathematical verification of the shift transform (translation-invariance) |
| `overnight_queue.sh` | orchestrator that chains the long runs sequentially |
