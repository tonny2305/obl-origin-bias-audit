# OBL Origin-Bias Audit

Code and results for a study asking a simple question about a hybrid,
opposition-based Flower Pollination Algorithm (**IFPOA-X**) benchmarked under
a strict 500-evaluation budget: **is its apparent low-budget advantage a
genuine algorithmic property, or an artifact of where the benchmark suite
places its optima relative to Opposition-Based Learning's reflection centre?**

IFPOA-X attains the best mean rank on the classical F1–F13 suite — but a
20-run component ablation shows the advantage is driven almost entirely by
Opposition-Based Learning, and four independent origin-bias controls (a
hand-built shift, a CEC2017 shifted-and-rotated subset, and two further
shifts) show that advantage **collapses** once the benchmark's optima are
displaced off-centre. A direct within-algorithm factorial (OBL on/off ×
centred/shifted) isolates the mechanism: removing OBL costs ~4 orders of
magnitude on the centred suite and ~0 once the optimum is displaced.

This repository contains everything needed to reproduce that audit:
benchmark suites, baseline adapters, the equal-NFE fairness harness, every
analysis/figure script, the raw results, and the final SWEVO manuscript
submission package.

## Repository layout

```
project/
  algorithms/
    ifpoax.py, fpa.py, pso.py        # algorithm implementations (unmodified
                                      # throughout this study — see below)
    benchmark_tester.py              # equal-NFE fairness harness
    paper/                           # everything specific to this audit
      functions.py                  # classical F1-F13
      functions_shifted.py          # origin-shifted F1-F13 (+ multi-shift configs)
      functions_cec.py              # CEC2017 subset via opfunu
      baselines.py                  # DE/L-SHADE/GWO/WOA (mealpy) + TPE (optuna)
      run_*.py                      # experiment runners (one per suite/control)
      ablation*.py                  # component ablation (OBL / JADE / bandit)
      rerun_f8_mixed.py             # domain-safe F8 re-run (see Known issues below)
      merge_f8_mixed.py             # merges the domain-safe fix into the dataset
      analyze.py, stats_advanced.py # descriptive + Mann-Whitney U/Friedman/Iman-Davenport/
                                      # Holm/Finner/Vargha-Delaney/bootstrap-CI stats
      extra_figures.py, synthesis_figure.py, interaction_figure.py  # figures
      verify_shift.py               # mathematical verification of the shift transform
      results*/                     # curated raw results for every suite/control
      README.md                     # detailed usage instructions and reproduction commands
Paper/
  SWEVO_submission_template/         # final LaTeX manuscript, figures, PDF, compile log
  hpo/, utils/                       # minimal compatibility stubs (see below)
```

## Algorithms are unmodified

`ifpoax.py`, `fpa.py`, `pso.py`, and `benchmark_tester.py` are copied
byte-for-byte from the source thesis project and were **never edited** for
this audit — every experiment reported changes only the benchmark objective
functions the harness evaluates them against, never the algorithms
themselves. This is a hard invariant of the study design.

## Why `project/hpo/` and `project/utils/` exist

The three algorithm files above were originally written as part of a larger
private project (transformer hyperparameter optimization for a separate
rainfall-forecasting task) and import a `build_search_space` /
`build_transformer_small_space` / `evaluate_config` / `RobustSchedule`
interface from that project's `hpo` package. **None of that project's code
is needed here** — every experiment in this repo runs through
`benchmark_tester.AlgorithmRunner`, which monkey-patches all of those names
with the real benchmark objective (F1–F13 / CEC2017 / shifted variants)
before the optimizer runs. `project/hpo/` and `project/utils/` in this repo
are minimal stand-in modules that satisfy the import, not the original
implementation; each file documents this in its own docstring.

## Quick start

```bash
pip install -r requirements.txt
cd project/algorithms/paper
python verify_shift.py            # sanity-check the shift transforms (fast)
python analyze.py --dims 30 50 --results results   # regenerate stats/figures
                                                      # from the included raw results
```

See `project/algorithms/paper/README.md` for the full set of experiment
commands (each suite/control can be re-run from scratch; this takes hours in
total, so the raw results are included directly).

## Known issues (disclosed, not hidden)

- **F8 (Schwefel 2.26) domain-safety.** F8 is the only benchmark function
  with a bounded validity domain; an early "mixed" (signed) shift
  configuration could push its evaluation argument outside that domain,
  producing invalid negative fitness. `rerun_f8_mixed.py` fixes this with a
  domain-safe clamped construction, and `merge_f8_mixed.py` merges the fix
  into the final dataset (`results_shift_multi/mixed_full/`) — no function
  is excluded from the final analysis.
- **Checkpoint side effect.** `ifpoax.py`'s `run()` method writes an
  optimizer checkpoint to a `project/artifacts_ifpoax/` directory relative
  to the current working directory (a behavior from the source thesis
  project, not altered here). This is harmless but will create that
  directory when you run experiments locally; it is gitignored.

## License

MIT — see `LICENSE`.
