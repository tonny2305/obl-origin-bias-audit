# FILE: algorithms/fpa.py
import time
import random
import math
import os
import pickle
import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import mlflow
import torch

from ..hpo.search_space import build_transformer_small_space, build_search_space, SearchSpace
from ..hpo.objectives import evaluate_config


@dataclass
class FPAConfig:
    pop_size: int = 24
    budget_ffe: int = 80
    max_time_hours: float = 6.0
    seed: int = 0
    site: str = "bogor"
    mode: str = "build_windows"
    feature_scheme: str = "full"  # "full" untuk semua fitur, "mrmr" untuk fitur terpilih mRMR
    model_type: str = "transformer"  # "transformer", "gru", "lstm", "bilstm", "cnn_bilstm", "xgboost"
    rung_defs: List[Dict[str, Any]] = field(default_factory=list)
    p_switch: float = 0.8  # global pollination probability
    gamma: float = 0.1     # local scale
    levy_gamma: float = 0.25  # scaling for Lévy flight in unit space [0,1]^D
    preset: Optional[str] = None


class FPAOptimizer:
    def __init__(self, cfg: FPAConfig):
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)
        self.space: SearchSpace = build_search_space(cfg.model_type, preset=cfg.preset)
        self.pop_U: List[Dict[str, float]] = []
        self.pop_theta: List[Dict[str, Any]] = []
        self.fit: List[Dict[str, Any]] = []
        self.best_theta: Dict[str, Any] = {}
        self.best_fit: Dict[str, Any] = {"S_robust_mean": float("inf"), "FLOPs": float("inf")}
        self.history: List[Dict[str, Any]] = []
        self.t = 0

    def initialize(self):
        U = self.space.latin_hypercube(self.cfg.pop_size, self.rng)
        self.pop_U = U
        self.pop_theta = [self.space.from_unit(u) for u in U]
        # Satu dict per bunga — jangan pakai [{}]*n (alias bersama merusak trials.json / pickle).
        self.fit = [{"S_robust_mean": float("inf"), "FLOPs": float("inf")} for _ in range(self.cfg.pop_size)]
        self.best_theta = {}
        self.best_fit = {"S_robust_mean": float("inf"), "FLOPs": float("inf")}
        self.t = 0

    def _eval_idx(self, i: int, rung_id: int):
        rung_def = dict(self.cfg.rung_defs[min(rung_id, len(self.cfg.rung_defs) - 1)])
        rung_def["rung"] = rung_id
        theta = self.space.clip_project(self.pop_theta[i])
        seeds = rung_def.get("seeds", [self.cfg.seed])
        res = evaluate_config(theta, rung_def, seeds, self.cfg.site, self.cfg.mode, self.t, trial_id=f"fpa-{self.t}", log_prefix="fpa", model_type=self.cfg.model_type, feature_scheme=self.cfg.feature_scheme)
        res_owned = copy.deepcopy(res)
        self.fit[i] = res_owned
        if res_owned["S_robust_mean"] < self.best_fit["S_robust_mean"] - 1e-12:
            self.best_fit = copy.deepcopy(res_owned)
            self.best_theta = copy.deepcopy(theta)

    def _levy_step(self, dim: int):
        # Simplified Lévy for FPA baseline (Mantegna algorithm)
        # Menggunakan self.rng (seeded Random instance) untuk reproducibility
        # per-run, menghindari kontaminasi dari global np.random state.
        # Referensi: Mantegna (1994) "Fast, accurate algorithm for numerical
        # simulation of Lévy stable stochastic processes".
        beta = 1.5
        sigma_u = (math.gamma(1 + beta) * np.sin(np.pi * beta / 2) /
                   (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
        u = np.array([self.rng.gauss(0.0, sigma_u) for _ in range(dim)])
        v = np.array([self.rng.gauss(0.0, 1.0)     for _ in range(dim)])
        step = u / (np.abs(v) ** (1.0 / beta) + 1e-12)
        return step

    def save_checkpoint(self, path: str):
        """Simpan state FPA untuk resume."""
        state = {
            't': self.t,
            'pop_U': copy.deepcopy(self.pop_U),
            'pop_theta': copy.deepcopy(self.pop_theta),
            'fit': copy.deepcopy(self.fit),
            'best_theta': copy.deepcopy(self.best_theta),
            'best_fit': copy.deepcopy(self.best_fit),
            'history': copy.deepcopy(self.history),
            'rng_state': {
                'python': self.rng.getstate(),
                'numpy': np.random.get_state(),
                'torch': torch.get_rng_state(),
                'cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            },
            'cfg_dict': {
                'pop_size': self.cfg.pop_size,
                'budget_ffe': self.cfg.budget_ffe,
                'max_time_hours': self.cfg.max_time_hours,
                'seed': self.cfg.seed,
                'site': self.cfg.site,
                'mode': self.cfg.mode,
                'p_switch': self.cfg.p_switch,
                'gamma': self.cfg.gamma,
                'levy_gamma': self.cfg.levy_gamma,
            }
        }
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, 'wb') as f:
            pickle.dump(state, f)
        os.replace(tmp_path, path)
        print(f"[FPA Checkpoint] Saved state at t={self.t} -> {path}")
        try:
            mlflow.log_artifact(path)
        except Exception as e:
            print(f"[FPA Checkpoint] Warning: Failed to log checkpoint to MLflow: {e}")

    def load_checkpoint(self, path: str):
        """Muat state FPA dari checkpoint."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"FPA checkpoint not found: {path}")
        with open(path, 'rb') as f:
            state = pickle.load(f)
        self.t = state['t']
        self.pop_U = state['pop_U']
        self.pop_theta = state['pop_theta']
        self.fit = state['fit']
        self.best_theta = state['best_theta']
        self.best_fit = state['best_fit']
        self.history = state['history']
        if 'rng_state' in state:
            rng_state = state['rng_state']
            self.rng.setstate(rng_state['python'])
            np.random.set_state(rng_state['numpy'])
            torch.set_rng_state(rng_state['torch'])
            if torch.cuda.is_available() and rng_state.get('cuda') is not None:
                torch.cuda.set_rng_state_all(rng_state['cuda'])
        if 'cfg_dict' in state:
            cfg_dict = state['cfg_dict']
            if cfg_dict.get('site') != self.cfg.site or cfg_dict.get('mode') != self.cfg.mode:
                print(f"[FPA Checkpoint] Warning: Config mismatch detected. "
                      f"Checkpoint: site={cfg_dict.get('site')}, mode={cfg_dict.get('mode')}; "
                      f"Current: site={self.cfg.site}, mode={self.cfg.mode}")
        print(f"[FPA Checkpoint] Loaded state from t={self.t}, best_S={self.best_fit['S_robust_mean']:.4f}")

    def run(self, resume_from: Optional[str] = None, ckpt_dir: Optional[str] = None, save_every_n_ffe: int = 10):
        start = time.time()
        if resume_from and os.path.exists(resume_from):
            self.load_checkpoint(resume_from)
            print(f"[FPA Resume] Continuing optimization from t={self.t}")
            if self.t >= self.cfg.budget_ffe:
                print(
                    f"[FPA Resume] PERINGATAN: budget_ffe={self.cfg.budget_ffe} <= "
                    f"t_loaded={self.t}. Optimizer akan langsung selesai tanpa evaluasi baru. "
                    f"Pastikan budget_ffe = TOTAL target, bukan tambahan."
                )
        else:
            self.initialize()
        
        ckpt_path = None
        if ckpt_dir:
            ckpt_path = os.path.join(ckpt_dir, "checkpoint_fpa.pkl")

        while self.t < self.cfg.budget_ffe and (time.time() - start)/3600.0 < self.cfg.max_time_hours:
            # Rung assignment: proportional thirds of budget_ffe (same scheme as BO),
            # replacing the old "every pop_size/3 evals, then stick at last rung" rule
            # which forced ~(budget_ffe - 2*pop_size/3) evaluations onto the most
            # expensive rung regardless of budget size (see FFE_BUDGET_ANALYSIS.md).
            rung_id = min(
                self.t // max(1, self.cfg.budget_ffe // max(1, len(self.cfg.rung_defs))),
                len(self.cfg.rung_defs) - 1,
            )
            i = self.rng.randrange(self.cfg.pop_size)
            self._eval_idx(i, rung_id)

            # Global or local pollination
            u_i = self.space.to_unit(self.pop_theta[i])
            if self.rng.random() < self.cfg.p_switch and self.best_theta:
                # Global pollination: Lévy flight toward global best
                # Correct formula (Yang 2012): x_new = x + γ·L·(g* - x)
                u_best = self.space.to_unit(self.best_theta)
                step = self._levy_step(len(u_i))

                gamma = self.cfg.levy_gamma
                u_new = {}
                for k_idx, k in enumerate(u_i.keys()):
                    # Direction toward best
                    direction = u_best[k] - u_i[k]

                    # Lévy step magnitude (use absolute value)
                    L_magnitude = abs(step[k_idx])
                    L_magnitude = max(0.01, min(2.0, L_magnitude))  # Bound Lévy step

                    # Apply: x_new = x + γ·L·(g* - x)
                    u_new[k] = u_i[k] + gamma * L_magnitude * direction

                    # Clip to [0, 1]
                    u_new[k] = max(0.0, min(1.0, u_new[k]))
            else:
                # Local pollination: interact with two random peers
                r1, r2 = self.rng.sample(self.pop_theta, 2)
                u_r1 = self.space.to_unit(r1)
                u_r2 = self.space.to_unit(r2)

                # Local search: x_new = x + ε·(x_j - x_k)
                epsilon = self.rng.uniform(0, 1)
                u_new = {}
                for k in u_i.keys():
                    u_new[k] = u_i[k] + epsilon * self.cfg.gamma * (u_r1[k] - u_r2[k])
                    u_new[k] = max(0.0, min(1.0, u_new[k]))

            self.pop_theta[i] = self.space.from_unit(u_new)

            # History: save current evaluation and best so far (consistent with IFPOA-X format)
            current_fit = self.fit[i]

            # Hitung R2_mean dan MAE_mean lintas horizon jika tersedia (aman terhadap missing/NaN)
            per_h = current_fit.get("per_h_summary", {}) or {}
            r2_vals = []
            mae_vals = []
            for _h, _m in per_h.items():
                if not isinstance(_m, dict):
                    continue
                if "r2" in _m:
                    try:
                        v = float(_m["r2"])
                        if np.isfinite(v):
                            r2_vals.append(v)
                    except Exception:
                        pass
                if "mae" in _m:
                    try:
                        v = float(_m["mae"])
                        if np.isfinite(v):
                            mae_vals.append(v)
                    except Exception:
                        pass
            r2_mean = float(np.mean(r2_vals)) if r2_vals else float("nan")
            mae_mean = float(np.mean(mae_vals)) if mae_vals else float("nan")

            self.history.append({
                "t": self.t,
                "idx": i,
                "rung": rung_id,
                "S": float(current_fit["S_robust_mean"]),
                "RMSE_mean": float(current_fit.get("RMSE_mean_H1_6", float("inf"))),
                "FLOPs": float(current_fit.get("FLOPs", float("inf"))),
                "best_S": float(self.best_fit["S_robust_mean"]),
                "R2_mean": r2_mean,
                "MAE_mean": mae_mean,
            })
            if self.t % 5 == 0:
                mlflow.log_metrics({"fpa.best_S": float(self.best_fit["S_robust_mean"]), "fpa.rung": float(rung_id)})

            # Periodic checkpoint
            if ckpt_path and (self.t + 1) % save_every_n_ffe == 0:
                self.save_checkpoint(ckpt_path)

            self.t += 1
        
        # Final checkpoint
        if ckpt_path:
            self.save_checkpoint(ckpt_path)

        trials = []
        for i in range(self.cfg.pop_size):
            if self.fit[i]["S_robust_mean"] < float("inf"):
                trials.append({"theta": self.pop_theta[i], "fit": self.fit[i]})
        return {"trials": trials, "history": self.history}
