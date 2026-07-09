# Minimal package init for this extracted repo.
#
# The original thesis project's algorithms/__init__.py eagerly imports a
# Bayesian-optimization module (bo_optuna.py) that is unrelated to this
# paper's TPE baseline (which uses optuna directly via paper/baselines.py).
# This repo intentionally does not include it, so this __init__.py stays
# minimal and does not re-export anything — every script in this repo
# imports ifpoax.py / fpa.py / pso.py / benchmark_tester.py as submodules
# directly (e.g. `import project.algorithms.ifpoax as ifpoax_mod`), never
# via a package-level shortcut.
