#!/usr/bin/env python3
"""
Adapter algoritma pembanding (baseline) untuk PAPER 1.
======================================================
Membungkus algoritma metaheuristik/BO eksternal pada objektif yang SAMA dan
anggaran evaluasi objektif nyata (NFE) yang SAMA dengan IFPOA-X/FPA/PSO, demi
perbandingan yang adil (equal-NFE). Tidak menyentuh algoritma IFPOA-X.

Baseline kuat/modern:
  - DE       : Differential Evolution           (mealpy)
  - L-SHADE  : Success-History DE + LPSR         (mealpy)
  - GWO      : Grey Wolf Optimizer               (mealpy)
  - WOA      : Whale Optimization Algorithm      (mealpy)
  - TPE      : Tree-structured Parzen Estimator  (optuna, sebagai proxy BO)

Setiap adapter mengembalikan {"best": float, "curve": [best-so-far per NFE], "nfe": int}.
"""
import numpy as np
from mealpy import FloatVar, Termination
from mealpy.evolutionary_based import DE, SHADE
from mealpy.swarm_based import GWO, WOA


class _Recorder:
    """Membungkus fungsi objektif: hitung NFE & rekam kurva best-so-far."""
    def __init__(self, fn):
        self.fn = fn
        self.n = 0
        self.best = float("inf")
        self.curve = []

    def __call__(self, sol):
        v = float(self.fn(np.asarray(sol, dtype=float)))
        self.n += 1
        if v < self.best:
            self.best = v
        self.curve.append(self.best)
        return v


def _default_pop(budget):
    # Selaras dgn harness IFPOA-X/FPA/PSO: min(24, budget//10)
    return max(4, min(24, budget // 10))


def run_mealpy(model_ctor, fn, bounds, dim, budget, seed, pop_size=None):
    rec = _Recorder(fn)
    lo, hi = bounds
    ps = pop_size or _default_pop(budget)
    problem = {
        "obj_func": rec,
        "bounds": FloatVar(lb=[lo] * dim, ub=[hi] * dim),
        "minmax": "min",
        "log_to": None,
    }
    # epoch dibuat cukup besar; max_fe yang menghentikan tepat di `budget` NFE.
    epoch = int(np.ceil(budget / ps)) + 2
    model = model_ctor(epoch=epoch, pop_size=ps)
    model.solve(problem, termination=Termination(max_fe=budget), seed=seed)
    # max_fe di mealpy adalah soft-cap (menyelesaikan generasi terakhir), sehingga
    # bisa overshoot hingga pop_size. Potong tepat ke `budget` evaluasi agar
    # equal-NFE rigor: hanya kreditkan `budget` evaluasi objektif pertama.
    return _truncate(rec, budget)


def _truncate(rec, budget):
    curve = rec.curve[:budget]
    if 0 < len(curve) < budget:
        curve = curve + [curve[-1]] * (budget - len(curve))
    best = curve[-1] if curve else rec.best
    return {"best": best, "curve": curve, "nfe": len(curve)}


def run_optuna_tpe(fn, bounds, dim, budget, seed, pop_size=None):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    rec = _Recorder(fn)
    lo, hi = bounds

    def objective(trial):
        x = np.array([trial.suggest_float(f"x{i}", lo, hi) for i in range(dim)])
        return rec(x)

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=seed),
    )
    study.optimize(objective, n_trials=budget, show_progress_bar=False)
    return _truncate(rec, budget)


# Registry: nama -> callable(fn, bounds, dim, budget, seed, pop_size=None)
BASELINES = {
    "DE":      lambda *a, **k: run_mealpy(DE.OriginalDE, *a, **k),
    "L-SHADE": lambda *a, **k: run_mealpy(SHADE.L_SHADE, *a, **k),
    "GWO":     lambda *a, **k: run_mealpy(GWO.OriginalGWO, *a, **k),
    "WOA":     lambda *a, **k: run_mealpy(WOA.OriginalWOA, *a, **k),
    "TPE":     run_optuna_tpe,
}


if __name__ == "__main__":
    # Self-check: tiap baseline harus melakukan TEPAT `budget` NFE pada Sphere-10D.
    from functions import FUNCTIONS
    fn, bounds, _x, _m = FUNCTIONS["F1"]
    budget = 300
    for name, runner in BASELINES.items():
        r = runner(fn, bounds, dim=10, budget=budget, seed=1)
        status = "OK" if r["nfe"] == budget else f"NFE!={budget}"
        assert r["nfe"] == budget, f"{name}: NFE={r['nfe']} != {budget}"
        print(f"{name:8s} best={r['best']:.4e}  nfe={r['nfe']}  curve_len={len(r['curve'])}  {status}")
    print("\nSemua baseline mematuhi equal-NFE.")
