# FILE: algorithms/pso.py
import time
import random
import os
import pickle
import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
import mlflow
import torch

from ..hpo.search_space import build_transformer_small_space, build_search_space, SearchSpace
from ..hpo.objectives import evaluate_config


@dataclass
class PSOConfig:
    pop_size: int = 24
    budget_ffe: int = 80
    max_time_hours: float = 6.0
    seed: int = 0
    site: str = "bogor"
    mode: str = "build_windows"
    feature_scheme: str = "full"  # "full" untuk semua fitur, "mrmr" untuk fitur terpilih mRMR
    model_type: str = "transformer"  # "transformer", "gru", "lstm", "bilstm", "cnn_bilstm", "xgboost"
    rung_defs: List[Dict[str, Any]] = field(default_factory=list)
    w: float = 0.7
    c1: float = 1.5
    c2: float = 1.5
    v_max: float = 0.2  # maximum velocity in unit space [0,1]^D
    preset: Optional[str] = None


class PSOOptimizer:
    def __init__(self, cfg: PSOConfig):
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)
        self.space: SearchSpace = build_search_space(cfg.model_type, preset=cfg.preset)
        self.pop_U: List[Dict[str, float]] = []
        self.pop_theta: List[Dict[str, Any]] = []
        self.vel: List[Dict[str, float]] = []
        self.fit: List[Dict[str, Any]] = []
        self.pbest_theta: List[Dict[str, Any]] = []
        self.pbest_fit: List[Dict[str, Any]] = []
        self.gbest_theta: Dict[str, Any] = {}
        self.gbest_fit: Dict[str, Any] = {"S_robust_mean": float("inf"), "FLOPs": float("inf")}
        self.history: List[Dict[str, Any]] = []
        self.t = 0

    def _unit_add(self, a: Dict[str, float], b: Dict[str, float], scale: float = 1.0) -> Dict[str, float]:
        out = {}
        for k in a.keys():
            out[k] = max(0.0, min(1.0, a[k] + scale * b[k]))
        return out

    def _unit_sub(self, a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
        return {k: a[k] - b[k] for k in a.keys()}

    def _unit_scale(self, a: Dict[str, float], s: float) -> Dict[str, float]:
        return {k: a[k] * s for k in a.keys()}

    def initialize(self):
        U = self.space.latin_hypercube(self.cfg.pop_size, self.rng)
        self.pop_U = U
        self.vel = [{k: 0.0 for k in U[0].keys()} for _ in range(self.cfg.pop_size)]
        self.pop_theta = [self.space.from_unit(u) for u in U]
        # Satu dict per partikel — jangan pakai [{}]*n (semua indeks berbagi objek yang sama).
        self.fit = [{"S_robust_mean": float("inf"), "FLOPs": float("inf")} for _ in range(self.cfg.pop_size)]
        self.pbest_theta = list(self.pop_theta)
        self.pbest_fit = [{"S_robust_mean": float("inf"), "FLOPs": float("inf")} for _ in range(self.cfg.pop_size)]
        self.gbest_theta = {}
        self.gbest_fit = {"S_robust_mean": float("inf"), "FLOPs": float("inf")}
        self.t = 0

    def _eval_idx(self, i: int, rung_id: int):
        rung_def = dict(self.cfg.rung_defs[min(rung_id, len(self.cfg.rung_defs) - 1)])
        rung_def["rung"] = rung_id
        theta = self.space.clip_project(self.pop_theta[i])
        seeds = rung_def.get("seeds", [self.cfg.seed])
        res = evaluate_config(theta, rung_def, seeds, self.cfg.site, self.cfg.mode, self.t, trial_id=f"pso-{self.t}", log_prefix="pso", model_type=self.cfg.model_type, feature_scheme=self.cfg.feature_scheme)
        res_owned = copy.deepcopy(res)
        self.fit[i] = res_owned
        # personal best
        if res_owned["S_robust_mean"] < self.pbest_fit[i]["S_robust_mean"] - 1e-12:
            self.pbest_fit[i] = copy.deepcopy(res_owned)
            self.pbest_theta[i] = copy.deepcopy(theta)
        # global best
        if res_owned["S_robust_mean"] < self.gbest_fit["S_robust_mean"] - 1e-12:
            self.gbest_fit = copy.deepcopy(res_owned)
            self.gbest_theta = copy.deepcopy(theta)

    def save_checkpoint(self, path: str):
        """Simpan state PSO untuk resume."""
        state = {
            't': self.t,
            'pop_U': copy.deepcopy(self.pop_U),
            'pop_theta': copy.deepcopy(self.pop_theta),
            'vel': copy.deepcopy(self.vel),
            'fit': copy.deepcopy(self.fit),
            'pbest_theta': copy.deepcopy(self.pbest_theta),
            'pbest_fit': copy.deepcopy(self.pbest_fit),
            'gbest_theta': copy.deepcopy(self.gbest_theta),
            'gbest_fit': copy.deepcopy(self.gbest_fit),
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
                'w': self.cfg.w,
                'c1': self.cfg.c1,
                'c2': self.cfg.c2,
                'v_max': self.cfg.v_max,
            }
        }
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, 'wb') as f:
            pickle.dump(state, f)
        os.replace(tmp_path, path)
        print(f"[PSO Checkpoint] Saved state at t={self.t} -> {path}")
        try:
            mlflow.log_artifact(path)
        except Exception as e:
            print(f"[PSO Checkpoint] Warning: Failed to log checkpoint to MLflow: {e}")

    def load_checkpoint(self, path: str):
        """Muat state PSO dari checkpoint."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"PSO checkpoint not found: {path}")
        with open(path, 'rb') as f:
            state = pickle.load(f)
        self.t = state['t']
        self.pop_U = state['pop_U']
        self.pop_theta = state['pop_theta']
        self.vel = state['vel']
        self.fit = state['fit']
        self.pbest_theta = state['pbest_theta']
        self.pbest_fit = state['pbest_fit']
        self.gbest_theta = state['gbest_theta']
        self.gbest_fit = state['gbest_fit']
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
                print(f"[PSO Checkpoint] Warning: Config mismatch detected. "
                      f"Checkpoint: site={cfg_dict.get('site')}, mode={cfg_dict.get('mode')}; "
                      f"Current: site={self.cfg.site}, mode={self.cfg.mode}")
        print(f"[PSO Checkpoint] Loaded state from t={self.t}, best_S={self.gbest_fit['S_robust_mean']:.4f}")

    def run(self, resume_from: Optional[str] = None, ckpt_dir: Optional[str] = None, save_every_n_ffe: int = 10):
        start = time.time()
        if resume_from and os.path.exists(resume_from):
            self.load_checkpoint(resume_from)
            print(f"[PSO Resume] Continuing optimization from t={self.t}")
            if self.t >= self.cfg.budget_ffe:
                print(
                    f"[PSO Resume] PERINGATAN: budget_ffe={self.cfg.budget_ffe} <= "
                    f"t_loaded={self.t}. Optimizer akan langsung selesai tanpa evaluasi baru. "
                    f"Pastikan budget_ffe = TOTAL target, bukan tambahan."
                )
        else:
            self.initialize()
        
        ckpt_path = None
        if ckpt_dir:
            ckpt_path = os.path.join(ckpt_dir, "checkpoint_pso.pkl")

        while self.t < self.cfg.budget_ffe and (time.time() - start)/3600.0 < self.cfg.max_time_hours:
            # Rung assignment: proportional thirds of budget_ffe (same scheme as BO),
            # replacing the old "every pop_size/3 evals, then stick at last rung" rule
            # which forced ~(budget_ffe - 2*pop_size/3) evaluations onto the most
            # expensive rung regardless of budget size (see FFE_BUDGET_ANALYSIS.md).
            rung_id = min(
                self.t // max(1, self.cfg.budget_ffe // max(1, len(self.cfg.rung_defs))),
                len(self.cfg.rung_defs) - 1,
            )
            # evaluate a random particle on current rung (SH-like)
            i = self.rng.randrange(self.cfg.pop_size)
            self._eval_idx(i, rung_id)

            # Velocity update with clamping
            r1, r2 = self.rng.random(), self.rng.random()
            u_i = self.space.to_unit(self.pop_theta[i])
            pbest_u = self.space.to_unit(self.pbest_theta[i])
            gbest_u = self.space.to_unit(self.gbest_theta) if self.gbest_theta else u_i

            # Velocity limits for unit space [0,1]^D
            V_MAX = self.cfg.v_max
            V_MIN = -V_MAX

            v_new = {}
            for k in u_i.keys():
                # Standard PSO velocity update
                v_new[k] = (self.cfg.w * self.vel[i][k]
                            + self.cfg.c1 * r1 * (pbest_u[k] - u_i[k])
                            + self.cfg.c2 * r2 * (gbest_u[k] - u_i[k]))

                # Clamp velocity to prevent explosion
                v_new[k] = max(V_MIN, min(V_MAX, v_new[k]))

            # Update position
            u_new = self._unit_add(u_i, v_new, 1.0)
            self.vel[i] = v_new
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
                "best_S": float(self.gbest_fit["S_robust_mean"]),
                "R2_mean": r2_mean,
                "MAE_mean": mae_mean,
            })
            if self.t % 5 == 0:
                mlflow.log_metrics({"pso.best_S": float(self.gbest_fit["S_robust_mean"]), "pso.rung": float(rung_id)})

            # Periodic checkpoint
            if ckpt_path and (self.t + 1) % save_every_n_ffe == 0:
                self.save_checkpoint(ckpt_path)

            self.t += 1
        
        # Final checkpoint
        if ckpt_path:
            self.save_checkpoint(ckpt_path)

        # Trials summary
        trials = []
        for i in range(self.cfg.pop_size):
            if self.fit[i]["S_robust_mean"] < float("inf"):
                trials.append({"theta": self.pop_theta[i], "fit": self.fit[i]})
        return {"trials": trials, "history": self.history}
