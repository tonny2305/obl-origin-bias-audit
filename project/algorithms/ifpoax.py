# FILE: algorithms/ifpoax.py
import math
import time
import random
import pickle
import os
import json
import shutil
import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
import torch
import mlflow

try:
    from ..hpo.search_space import build_transformer_small_space, build_search_space, SearchSpace
    from ..hpo.objectives import evaluate_config, RobustSchedule
except ImportError:
    import sys
    from pathlib import Path
    _proj = Path(__file__).resolve().parent.parent
    if str(_proj) not in sys.path:
        sys.path.insert(0, str(_proj))
    from hpo.search_space import build_transformer_small_space, build_search_space, SearchSpace
    from hpo.objectives import evaluate_config, RobustSchedule


# =========================
# Pareto / NSGA-II helpers
# =========================

def dominates(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
    # Minimize both coordinates (generic 2D min-min)
    return (a[0] <= b[0] and a[1] <= b[1]) and (a[0] < b[0] or a[1] < b[1])


def nondominated_sort(points: List[Tuple[float, float]]) -> List[List[int]]:
    fronts: List[List[int]] = []
    S = [set() for _ in points]
    n = [0 for _ in points]
    rank = [0 for _ in points]
    for p in range(len(points)):
        for q in range(len(points)):
            if p == q:
                continue
            if dominates(points[p], points[q]):
                S[p].add(q)
            elif dominates(points[q], points[p]):
                n[p] += 1
        if n[p] == 0:
            rank[p] = 0
    front0 = [i for i in range(len(points)) if n[i] == 0]
    fronts.append(front0)
    i = 0
    while len(fronts[i]) > 0:
        Q = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    rank[q] = i + 1
                    Q.append(q)
        i += 1
        fronts.append(Q)
    if len(fronts[-1]) == 0:
        fronts.pop()
    return fronts


def crowding_distance(front: List[int], points: List[Tuple[float, float]]) -> Dict[int, float]:
    if len(front) == 0:
        return {}
    dist = {i: 0.0 for i in front}
    for m in range(2):  # two objectives
        front_sorted = sorted(front, key=lambda i: points[i][m])
        dist[front_sorted[0]] = float("inf")
        dist[front_sorted[-1]] = float("inf")
        vals = [points[i][m] for i in front_sorted]
        vmin, vmax = float(min(vals)), float(max(vals))
        denom = vmax - vmin + 1e-12
        for k in range(1, len(front_sorted) - 1):
            i_prev, i_next = front_sorted[k - 1], front_sorted[k + 1]
            dist[front_sorted[k]] += (points[i_next][m] - points[i_prev][m]) / denom
    return dist


# =========================
# Lévy Flight (Mantegna)
# =========================

def mantegna_levy_step(beta: float, dim: int, rng: random.Random) -> np.ndarray:
    # Mantegna algorithm
    sigma_u = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
               (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    sigma_v = 1.0
    u = np.array([rng.gauss(0, sigma_u) for _ in range(dim)], dtype=float)
    v = np.array([rng.gauss(0, sigma_v) for _ in range(dim)], dtype=float)
    step = u / (np.power(np.abs(v) + 1e-12, 1.0 / beta))
    return step


# =========================
# 2D Hypervolume (min-min)
# =========================

def hypervolume_2d_min(points: List[Tuple[float, float]],
                       ref: Tuple[float, float]) -> float:
    """
    Compute dominated HV for 2D minimization with rectangular reference ref=(S_max, F_max).
    Implementation: sort by S asc, sweep rectangles to ref; clip at ref.
    """
    if not points:
        return 0.0
    Sref, Fref = float(ref[0]), float(ref[1])
    # Filter dominated w.r.t. ref; clip
    pts = [(min(p[0], Sref), min(p[1], Fref)) for p in points]
    # Keep only non-dominated
    fronts = nondominated_sort(pts)
    if not fronts:
        return 0.0
    nd = [pts[i] for i in fronts[0]]
    nd = sorted(nd, key=lambda x: (x[0], x[1]))  # sort by S asc
    hv = 0.0
    prev_S = nd[0][0]
    prev_F = nd[0][1]
    # rectangle from (prev_S, prev_F) to (Sref, Fref)
    hv += max(0.0, (Sref - prev_S)) * max(0.0, (Fref - prev_F))
    for s, f in nd[1:]:
        # The new rectangle starts at S = s, height from f to previous f (take min to avoid overlap)
        hv += max(0.0, (Sref - s)) * max(0.0, (min(prev_F, Fref) - f))
        prev_F = min(prev_F, f)
    return max(0.0, hv)


# =========================
# IFPOA-X Config (Revisi)
# =========================

@dataclass
class IFPOAXConfig:
    # FINAL CONFIGURATION (Grand Consensus / Strict Mode)
    # Population 32 × "max iterations" 20 ≈ budget_ffe 640 (FFE-based loop)
    population: int = 32
    budget_ffe: int = 640
    max_time_hours: float = 6.0
    seed: int = 0
    site: str = "bogor"
    mode: str = "build_windows"  # or "use_indexed_windows"
    feature_scheme: str = "full"  # "full" untuk semua fitur, "mrmr" untuk fitur terpilih mRMR
    model_type: str = "transformer"  # "transformer", "gru", "lstm", "bilstm", "cnn_bilstm", "xgboost"
    archive_max: int = 64
    archive_trim: str = "crowding"
    preset: Optional[str] = None  # GPU preset: "6gb", "supergpu", or None for default
    parallel_trials: int = 1  # Jumlah trial paralel (default: 1)

    # ===== Opposition-Based Learning (OBL) =====
    use_obl: bool = True                 # aktif/nonaktif OBL
    obl_mode: str = "elite"              # "elite" (disarankan) atau "all"
    obl_frequency: int = 3               # jalankan OBL tiap N evaluasi (FFE)
    obl_top_k: int = 3                   # jumlah elit (dari arsip/front-1) untuk dibuat opositenya
    obl_replace_policy: str = "cohort_worst"  # "cohort_worst" atau "archive_worst_by_cd"
    obl_eval_same_rung: bool = True      # evaluasi opposite pada rung aktif kandidat berjalan

    # ASHA-style rungs (eta used for quotas)
    rung_defs: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"rung": 0, "epochs": 16,  "horizons": [1, 3, 5],        "seeds": [0],        "batch_accum": 1},
        {"rung": 1, "epochs": 60,  "horizons": [1, 2, 3, 4, 5, 6], "seeds": [0, 1],     "batch_accum": 1},
        {"rung": 2, "epochs": 120, "horizons": [1, 2, 3, 4, 5, 6], "seeds": [0, 1, 2], "batch_accum": 1},
    ])
    eta: int = 2  # used by ASHA quotas (reduction_factor=2)

    # ===== Adaptive control (replaces static kappa rules) =====
    use_bandit: bool = True
    bandit_c: float = 1.4           # exploration constant for UCB1
    bandit_reward: str = "hv"       # "hv" or "s_improve"
    hv_ref_margin_S: float = 0.05   # 5% margin on S for HV reference
    hv_ref_margin_F: float = 0.05   # 5% margin on F for HV reference

    # ===== Global step self-calibration (1/5 success rule + anneal) =====
    levy_beta: float = 1.5
    c0: float = 0.15
    eta_anneal: float = 1.5
    c_min: float = 0.01
    c_max: float = 0.5
    acc_target: float = 0.20        # 1/5 rule
    c_adapt_gamma: float = 0.85     # decrease factor if success < target
    c_adapt_delta: float = 1.15     # increase factor if success > target

    # ===== JADE-style local operator =====
    use_jade_local: bool = True
    jade_p: float = 0.20            # p-best (top 20%)
    jade_cmean: float = 0.5         # mean CR
    jade_fmean: float = 0.5         # mean F
    jade_arch_max: int = 128        # external archive for JADE mutation

    # ===== Cheap screen =====
    use_knn_screen: bool = True
    knn_k: int = 8
    knn_min_points: int = 12
    screen_quantile: float = 0.40   # require predicted child to beat parent by this quantile on S

    # archive_max sudah didefinisikan di atas (baris ~152); tidak perlu duplikat


# =========================
# IFPOA-X Optimizer (Revisi)
# =========================

class IFPOAXOptimizer:
    def __init__(self, cfg: IFPOAXConfig):
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)
        # Use model_type + preset from config to build search space
        self.space: SearchSpace = build_search_space(cfg.model_type, preset=cfg.preset)
        self.robust_sched = RobustSchedule(total_steps=cfg.budget_ffe)
        self.obl_applied: int = 0        # berapa kali OBL dijalankan
        self.obl_accepted: int = 0       # berapa kali solusi opposite diterima (menggantikan kandidat)

        # ----- state -----
        self.t = 0  # evaluation counter (trial-based)
        self.last_improve_t = 0
        self.best_S = float("inf")

        # Population & fitness
        self.population: List[Dict[str, Any]] = []
        self.population_U: List[Dict[str, float]] = []  # unit space
        self.fitness: List[Dict[str, Any]] = []         # dict with S_robust_mean, FLOPs, etc.
        self.rung_index: List[int] = []                 # rung per individual

        # Pareto archive
        self.archive: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []  # (theta, fit)
        self.history: List[Dict[str, Any]] = []

        # Acceptance tracking
        self.accept_hist: List[bool] = []

        # ASHA bookkeeping
        self.rung_promoted: Dict[int, int] = {}  # how many have been promoted from rung r

        # JADE external archive for differences
        self.jade_ext_archive_U: List[Dict[str, float]] = []

        # Bandit (GLOBAL vs LOCAL)
        self.bandit_N: Dict[str, int] = {"global": 1, "local": 1}
        self.bandit_sumR: Dict[str, float] = {"global": 0.0, "local": 0.0}

        # Surrogate data for cheap screen (unit -> (S,F))
        self._surrogate_X: List[Dict[str, float]] = []
        self._surrogate_Y: List[Tuple[float, float]] = []

        # **OPTIMIZATION: Theta cache & deduplication**
        self._theta_cache: Dict[str, Dict[str, Any]] = {}  # hash -> fit
        self._last_eval_time: List[float] = []  # time of last evaluation per idx

        # Adaptive step-scale c0: disimpan sebagai state optimizer, BUKAN dimutasi
        # langsung pada cfg. Ini mencegah kontaminasi config object antar run.
        # Referensi: 1/5-success-rule, Rechenberg (1973) "Evolutionsstrategie".
        self._c0: float = cfg.c0

    # ---------- Utility ----------

    def _diversity(self) -> float:
        return self.space.mean_pairwise_distance(self.population_U)

    def _hv_points(self) -> List[Tuple[float, float]]:
        # Quality-first hypervolume on (RMSE_mean_H1_6, S_robust_mean)
        return [
            (float(ft["RMSE_mean_H1_6"]), float(ft["S_robust_mean"]))
            for (_, ft) in self.archive
            if ("RMSE_mean_H1_6" in ft and "S_robust_mean" in ft)
        ]

    def _hv_reference(self) -> Tuple[float, float]:
        pts = self._hv_points()
        if not pts:
            # Fallback reference
            return (1.0, 1e12)
        Rmax = max(p[0] for p in pts)  # RMSE axis
        Smax = max(p[1] for p in pts)  # S_robust axis
        return (Rmax * (1.0 + self.cfg.hv_ref_margin_S),
                Smax * (1.0 + self.cfg.hv_ref_margin_F))

    def _hv(self) -> float:
        return hypervolume_2d_min(self._hv_points(), self._hv_reference())

    def _improvement_rate(self, w: int = 5) -> float:
        if len(self.history) < w + 1:
            return 0.0
        now = self.history[-1]["best_S"]
        past = self.history[-1 - w]["best_S"]
        if past <= 0:
            return 0.0
        return max(0.0, (past - now) / max(past, 1e-12))

    # ----- Bandit (UCB1) -----

    def _bandit_select(self) -> str:
        if not self.cfg.use_bandit:
            # default fallback: 50-50
            return "global" if self.rng.random() < 0.5 else "local"
        total = self.bandit_N["global"] + self.bandit_N["local"]
        means = {
            arm: (self.bandit_sumR[arm] / max(1, self.bandit_N[arm]))
            for arm in ["global", "local"]
        }
        ucb = {
            arm: means[arm] + self.cfg.bandit_c * math.sqrt(math.log(total + 1) / self.bandit_N[arm])
            for arm in ["global", "local"]
        }
        # Tie-breaking: jika UCB sama, prefer arm yang kurang dipilih (untuk exploration balance)
        if abs(ucb["global"] - ucb["local"]) < 1e-12:
            # Jika sama, pilih yang kurang dipilih untuk balance exploration
            if self.bandit_N["global"] < self.bandit_N["local"]:
                return "global"
            elif self.bandit_N["local"] < self.bandit_N["global"]:
                return "local"
            else:
                # Jika sama juga, random untuk initial exploration
                return "global" if self.rng.random() < 0.5 else "local"
        return "global" if ucb["global"] >= ucb["local"] else "local"

    def _bandit_update(self, arm: str, reward: float):
        if not self.cfg.use_bandit:
            return
        r = max(0.0, min(1.0, reward))
        self.bandit_sumR[arm] += r
        self.bandit_N[arm] += 1

    # ----- Global step scale (1/5 rule + anneal) -----

    def _calibrate_c(self) -> float:
        # anneal multiplier
        a_t = (1.0 - min(1.0, self.t / max(1, self.cfg.budget_ffe))) ** self.cfg.eta_anneal
        # adapt c0 via 1/5 rule on recent acceptances (Rechenberg 1973)
        # Menggunakan self._c0 (state optimizer) — TIDAK memodifikasi self.cfg.c0
        # agar objek konfigurasi tetap immutable dan aman di-share antar konteks.
        recent = self.accept_hist[-20:] if self.accept_hist else []
        acc_ratio = float(sum(1 for z in recent if z)) / max(1, len(recent))
        if acc_ratio > self.cfg.acc_target:
            self._c0 = min(self._c0 * self.cfg.c_adapt_delta, self.cfg.c_max)
        elif acc_ratio < self.cfg.acc_target:
            self._c0 = max(self._c0 * self.cfg.c_adapt_gamma, self.cfg.c_min)
        return float(max(self.cfg.c_min, min(self.cfg.c_max, self._c0 * a_t)))

    # ----- Local operator: JADE current-to-pbest/1 binomial -----

    def _jade_local_step(self, u_parent: Dict[str, float]) -> Dict[str, float]:
        U_all = list(self.population_U)
        # Add external archive for more diversity (JADE)
        U_all_ext = U_all + self.jade_ext_archive_U
        if len(U_all_ext) < 3:
            # fallback: gentle jitter
            out = {k: max(0.0, min(1.0, u_parent[k] + self.rng.uniform(-0.05, 0.05))) for k in u_parent.keys()}
            return out

        # --- sample F, CR from success-history means ---
        F = self._sample_cauchy(self.cfg.jade_fmean, 0.1)
        F = float(min(1.0, max(0.0, F)))
        CR = self._sample_normal(self.cfg.jade_cmean, 0.1)
        CR = float(min(1.0, max(0.0, CR)))

        # --- choose p-best from archive (or population) ---
        pts = [
            (a[1]["RMSE_mean_H1_6"], a[1]["S_robust_mean"]) for a in self.archive
            if ("RMSE_mean_H1_6" in a[1] and "S_robust_mean" in a[1])
        ]
        if pts:
            fronts = nondominated_sort(pts)
            top = [self.archive[i][0] for i in fronts[0]] if fronts else [th for (th, _) in self.archive]
            # take p-best subset — pakai self.rng untuk reproducibility per-run
            k = max(1, int(math.ceil(self.cfg.jade_p * len(top))))
            pset = self.rng.sample(top, k=min(k, len(top)))
            pbest_theta = self.rng.choice(pset)
            pbest = self.space.to_unit(pbest_theta)
        else:
            # fallback to population best S
            best_idx = int(np.argmin([ft["S_robust_mean"] for ft in self.fitness]))
            pbest = self.space.to_unit(self.population[best_idx])

        # --- choose r1, r2 from (population + ext archive) distinct from parent ---
        cand = [uu for uu in U_all_ext if uu is not u_parent]
        if len(cand) < 2:
            cand = U_all_ext
        r1, r2 = self.rng.sample(cand, 2)

        # current-to-pbest/1 mutation in unit space
        keys = list(u_parent.keys())
        u_mut = dict(u_parent)
        j_rand = self.rng.randrange(len(keys))
        for j, k in enumerate(keys):
            if self.rng.random() < CR or j == j_rand:
                u_mut[k] = u_parent[k] + F * (pbest[k] - u_parent[k]) + F * (r1[k] - r2[k])
                u_mut[k] = float(max(0.0, min(1.0, u_mut[k])))

        return u_mut
    
    # ---------- OBL utilities ----------
    def _opposite_unit(self, u: Dict[str, float]) -> Dict[str, float]:
        """Opposition di ruang unit: u_opp = 1 - u."""
        return {k: 1.0 - float(v) for k, v in u.items()}

    def _elite_unit_pool(self) -> List[Dict[str, float]]:
        """
        Pilih pool elit untuk OBL.
        Prioritas: non-dominated front pertama pada arsip.
        Fallback: top-k terbaik S di populasi bila arsip kosong.
        """
        pool: List[Dict[str, float]] = []
        if len(self.archive) > 0:
            pts = [(a[1]["S_robust_mean"], a[1]["FLOPs"]) for a in self.archive]
            fronts = nondominated_sort(pts)
            if fronts:
                first = fronts[0]
                # urutkan by crowding distance desc agar area jarang lebih prior
                cd = crowding_distance(first, pts)
                first_sorted = sorted(first, key=lambda i: cd.get(i, 0.0), reverse=True)
                for i in first_sorted[: max(1, self.cfg.obl_top_k)]:
                    pool.append(self.space.to_unit(self.archive[i][0]))
        if not pool:
            # fallback: populasi, ambil top-k terbaik S_robust_mean
            if self.fitness:
                order = np.argsort([ft["S_robust_mean"] for ft in self.fitness])
                for i in list(order)[: max(1, self.cfg.obl_top_k)]:
                    pool.append(self.space.to_unit(self.population[i]))
        return pool

    def _cohort_indices(self, rung_id: int) -> List[int]:
        return [i for i, r in enumerate(self.rung_index) if r == rung_id and self.fitness[i]["S_robust_mean"] < float("inf")]

    def _worst_in_cohort(self, cohort: List[int]) -> Optional[int]:
        if not cohort:
            return None
        # Worst = Pareto seleksi buruk: ambil yang rank paling jelek, tie by S dan FLOPs
        pts = [
            (self.fitness[i]["RMSE_mean_H1_6"], self.fitness[i]["S_robust_mean"]) for i in cohort
            if ("RMSE_mean_H1_6" in self.fitness[i] and "S_robust_mean" in self.fitness[i])
        ]
        fronts = nondominated_sort(pts)
        worst_set = fronts[-1] if fronts else list(range(len(cohort)))
        # worst by higher RMSE, tie by higher S_robust
        worst_idx_local = max(worst_set, key=lambda j: (pts[j][0], pts[j][1]))
        return cohort[worst_idx_local]

    def _apply_obl_once(self, rung_id: int) -> bool:
        """
        Jalankan satu aksi OBL:
          - pilih 1 elit (unit) dari pool
          - hitung opposite di unit
          - evaluasi opposite pada rung_id (fidelity sesuai kebijakan)
          - bandingkan vs kandidat terburuk di cohort rung_id
          - jika lebih baik (Pareto), ganti kandidat itu.
        Mengonsumsi 1 FFE. Return True jika accepted.
        """
        pool = self._elite_unit_pool()
        if not pool:
            return False

        # ambil satu elit acak dari pool — pakai self.rng untuk reproducibility per-run
        u_elite = self.rng.choice(pool)
        u_opp = self._opposite_unit(u_elite)
        theta_opp = self.space.from_unit(u_opp)

        # siapkan rung fidelity
        rung_def = dict(self.cfg.rung_defs[min(rung_id, len(self.cfg.rung_defs) - 1)])
        rung_def["rung"] = rung_id

        # cek budget/time sebelum evaluasi
        # (kita akan menaikkan self.t setelah evaluasi, menjaga fairness FFE)
        fit_opp = self._evaluate_and_log(theta_opp, rung_def)

        # pilih target penggantian
        if self.cfg.obl_replace_policy == "cohort_worst":
            cohort = self._cohort_indices(rung_id)
            worst_idx = self._worst_in_cohort(cohort)
        else:
            # "archive_worst_by_cd" — ganti yang paling crowded di arsip (jarang dipakai untuk populasi)
            # fallback ke cohort worst jika arsip belum penuh
            cohort = self._cohort_indices(rung_id)
            worst_idx = self._worst_in_cohort(cohort)

        if worst_idx is None:
            return False

        # keputusan Pareto: (fit_opp) vs (fitness[worst_idx])
        a = (float(fit_opp["RMSE_mean_H1_6"]), float(fit_opp["S_robust_mean"]))
        b = (
            float(self.fitness[worst_idx]["RMSE_mean_H1_6"]),
            float(self.fitness[worst_idx]["S_robust_mean"]),
        )
        accept = False
        if dominates(a, b):
            accept = True
        elif not dominates(b, a):
            # non-dominated → tie-break by RMSE then S_robust
            if (a[0] < b[0] - 1e-12) or (abs(a[0] - b[0]) < 1e-12 and a[1] < b[1] - 1e-12):
                accept = True

        if accept:
            self.population[worst_idx] = theta_opp
            self.population_U[worst_idx] = u_opp
            self.fitness[worst_idx] = fit_opp
            self._pareto_update(theta_opp, fit_opp)
            return True
        return False

    def _maybe_apply_obl(self, current_rung: int) -> bool:
        """
        Dipanggil dari loop utama secara periodik berdasarkan obl_frequency.
        Mengonsumsi <= 1 FFE (satu evaluasi) untuk menjaga fairness & kontrol beban.
        Return:
            True  -> ada 1 evaluasi OBL yang dieksekusi (harus +1 FFE)
            False -> tidak ada evaluasi OBL (jangan tambah FFE)
        """
        if not self.cfg.use_obl:
            return False
        if self.t % max(1, self.cfg.obl_frequency) != 0:
            return False
        if len(self.population) == 0:
            return False

        # lakukan satu kali OBL
        self.obl_applied += 1
        accepted = self._apply_obl_once(current_rung)
        if accepted:
            self.obl_accepted += 1

        # logging ringan (best effort)
        try:
            mlflow.log_metrics({
                "ifpoax.obl_applied": float(self.obl_applied),
                "ifpoax.obl_accepted": float(self.obl_accepted),
            })
        except Exception:
            pass

        # Penting: fungsi ini selalu melakukan 1 evaluasi saat masuk (apply_once),
        # sehingga kita return True agar loop utama menambah FFE 1x.
        return True


    def _sample_cauchy(self, x0: float, gamma: float) -> float:
        # Inverse CDF method untuk Cauchy(x0, gamma).
        # Menggunakan self.rng untuk reproducibility per-run.
        # Referensi: Press et al. "Numerical Recipes" — quantile transform Cauchy.
        u = self.rng.random()
        z = math.tan(math.pi * (u - 0.5))
        return x0 + gamma * z

    def _sample_normal(self, mu: float, sigma: float) -> float:
        # Menggunakan self.rng.gauss (Box-Muller via CPython random module)
        # untuk reproducibility per-run, menghindari global random state.
        return self.rng.gauss(mu, sigma)

    # ----- Global Lévy step -----

    def _levy_global_step(self, u: Dict[str, float], c_scale: float) -> Dict[str, float]:
        step = mantegna_levy_step(self.cfg.levy_beta, len(u), self.rng)
        keys = list(u.keys())
        out = {}
        for i, k in enumerate(keys):
            val = u[k] + c_scale * float(step[i])
            out[k] = max(0.0, min(1.0, val))
        return out

    # ----- Evaluation & archive -----

    @staticmethod
    def _theta_hash(theta: Dict[str, Any], rung_def: Optional[Dict[str, Any]] = None) -> str:
        """Hash (theta, rung) untuk cache — rung berbeda menghasilkan key berbeda.
        Jika rung_def=None, hash hanya theta (untuk deduplication populasi)."""
        import hashlib
        if rung_def is not None:
            cache_key = {
                "theta": theta,
                "rung": rung_def.get("rung", -1),
                "epochs": rung_def.get("epochs", -1),
                "seeds": sorted(rung_def.get("seeds", [])),
            }
        else:
            cache_key = {"theta": theta}
        key_json = json.dumps(cache_key, sort_keys=True, default=str)
        return hashlib.md5(key_json.encode()).hexdigest()

    def _evaluate_and_log(self, theta: Dict[str, Any], rung_def: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = self._theta_hash(theta, rung_def)

        # Check cache (keyed by theta + rung, bukan theta saja)
        if cache_key in self._theta_cache:
            return copy.deepcopy(self._theta_cache[cache_key])
        
        seeds = list(rung_def.get("seeds", [self.cfg.seed]))
        trial_id = f"t{self.t}"
        try:
            theta_str = json.dumps(theta, sort_keys=True)
            print(f"[IFPOAX][{trial_id}] rung={rung_def.get('rung', '?')} theta={theta_str}")
        except Exception:
            pass
        res = evaluate_config(theta, rung_def, seeds, self.cfg.site, self.cfg.mode, self.t, trial_id, log_prefix="ifpoax", model_type=self.cfg.model_type, feature_scheme=self.cfg.feature_scheme)
        
        # Cache result (keyed by theta + rung) — salinan terpisah agar tidak ada alias dengan populasi/trial.
        res_owned = copy.deepcopy(res)
        self._theta_cache[cache_key] = res_owned
        return res_owned

    def _pareto_update(self, theta: Dict[str, Any], fit: Dict[str, Any]):
        pt = (float(fit["RMSE_mean_H1_6"]), float(fit["S_robust_mean"]))
        # early discard if dominated by any in archive
        for _, ft in self.archive:
            if dominates((float(ft["RMSE_mean_H1_6"]), float(ft["S_robust_mean"])), pt):
                return
        # keep non-dominated
        new_arch: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
        for th, ft in self.archive:
            if dominates(pt, (float(ft["RMSE_mean_H1_6"]), float(ft["S_robust_mean"]))):
                # move dominated to JADE ext archive (unit)
                self._try_push_jade_ext(th)
                continue
            new_arch.append((th, ft))
        new_arch.append((copy.deepcopy(theta), copy.deepcopy(fit)))
        self.archive = new_arch

        # trim by crowding distance if too many
        if len(self.archive) > self.cfg.archive_max:
            pts = [(a[1]["RMSE_mean_H1_6"], a[1]["S_robust_mean"]) for a in self.archive]
            fronts = nondominated_sort(pts)
            new_idx: List[int] = []
            for fr in fronts:
                if len(new_idx) + len(fr) <= self.cfg.archive_max:
                    new_idx += fr
                else:
                    cd = crowding_distance(fr, pts)
                    fr_sorted = sorted(fr, key=lambda i: cd.get(i, 0.0), reverse=True)
                    need = self.cfg.archive_max - len(new_idx)
                    new_idx += fr_sorted[:need]
                    break
            self.archive = [self.archive[i] for i in new_idx]

    def _try_push_jade_ext(self, theta: Dict[str, Any]):
        if not self.cfg.use_jade_local:
            return
        if len(self.jade_ext_archive_U) >= self.cfg.jade_arch_max:
            # drop random
            self.jade_ext_archive_U.pop(self.rng.randrange(len(self.jade_ext_archive_U)))
        self.jade_ext_archive_U.append(self.space.to_unit(theta))

    # ----- Cheap screen (k-NN surrogate) -----

    def _surrogate_add(self, u: Dict[str, float], fit: Dict[str, Any]):
        self._surrogate_X.append(dict(u))
        self._surrogate_Y.append((float(fit["S_robust_mean"]), float(fit["FLOPs"])))

    def _knn_predict(self, u: Dict[str, float], k: int) -> Tuple[float, float]:
        if len(self._surrogate_X) < max(k, self.cfg.knn_min_points):
            return (float("inf"), float("inf"))
        # compute distances
        dists = []
        for i, uu in enumerate(self._surrogate_X):
            d = 0.0
            for name in uu.keys():
                x = uu[name] - u[name]
                d += x * x
            d = math.sqrt(d)
            dists.append((d, i))
        dists.sort(key=lambda t: t[0])
        top = dists[:k]
        wsum = 0.0
        S_ = 0.0
        F_ = 0.0
        for d, i in top:
            w = 1.0 / (d + 1e-6)
            Ss, Fs = self._surrogate_Y[i]
            S_ += w * Ss
            F_ += w * Fs
            wsum += w
        if wsum <= 0:
            return (float("inf"), float("inf"))
        return (S_ / wsum, F_ / wsum)

    # ---------- Main public API ----------

    def initialize(self):
        U = self.space.latin_hypercube(self.cfg.population, self.rng)
        self.population_U = U
        self.population = [self.space.from_unit(u) for u in U]
        
        # **AGGRESSIVE DEDUPLICATION**: Check for duplicate theta and regenerate with more retries
        seen_hashes: Dict[str, int] = {}
        num_duplicates = 0
        for i, theta in enumerate(self.population):
            theta_hash = self._theta_hash(theta)
            if theta_hash in seen_hashes:
                num_duplicates += 1
                # Duplicate found, regenerate with up to 100 retries to find unique
                attempts = 0
                max_attempts = 100
                while attempts < max_attempts and theta_hash in seen_hashes:
                    u_new = self.space.random_sample_unit(self.rng)
                    self.population_U[i] = u_new
                    self.population[i] = self.space.from_unit(u_new)
                    theta_hash = self._theta_hash(self.population[i])
                    attempts += 1
                # If still duplicate after 100 attempts, accept it (space may be limited)
            seen_hashes[theta_hash] = i
        
        # Log deduplication result
        if num_duplicates > 0:
            print(f"[Initialize] Found and regenerated {num_duplicates} duplicate theta in initial population")

        self.fitness = [
            {"S_robust_mean": float("inf"), "FLOPs": float("inf"), "RMSE_mean_H1_6": float("inf")}
            for _ in range(self.cfg.population)
        ]
        self.rung_index = [0] * self.cfg.population

        # reset counters/states
        self.t = 0
        self.last_improve_t = 0
        self.best_S = float("inf")
        self.accept_hist = []
        self.archive = []
        self.history = []
        self.rung_promoted = {}
        self._last_eval_time = [float("-inf")] * self.cfg.population

        # clear bandit and surrogate
        self.bandit_N = {"global": 1, "local": 1}
        self.bandit_sumR = {"global": 0.0, "local": 0.0}
        self._surrogate_X = []
        self._surrogate_Y = []
        self.jade_ext_archive_U = []

        # Fix #4: Reset theta cache agar hasil run sebelumnya tidak bocor ke run baru.
        # Penting saat initialize() dipanggil ulang pada objek yang sama (misal resume).
        self._theta_cache = {}

        # Fix #5: Reset adaptive c0 ke nilai awal dari config agar setiap run
        # memulai dari kondisi step-scale yang sama (tidak terpengaruh run sebelumnya).
        self._c0 = self.cfg.c0

    def _asha_promote_eliminate(self, rung: int):
        """
        True ASHA-style: do not wait for cohorts.
        At rung r, allow at most floor(n_r / eta) promotions to rung r+1,
        where n_r is #evaluated (finite fitness) at rung r. Others are stopped & respawn.
        """
        if rung >= len(self.cfg.rung_defs) - 1:
            return  # final rung, nothing to promote

        # candidates that have finite fitness at this rung
        cohort = [i for i, r in enumerate(self.rung_index)
                  if r == rung and np.isfinite(self.fitness[i]["S_robust_mean"])]

        if not cohort:
            return

        n_r = len(cohort)
        quota = max(1, n_r // self.cfg.eta)
        already = self.rung_promoted.get(rung, 0)
        to_promote = max(0, quota - already)
        if to_promote <= 0:
            return

        # rank cohort via NSGA-II (S, FLOPs) and promote best 'to_promote'
        pts = [(self.fitness[i]["RMSE_mean_H1_6"], self.fitness[i]["S_robust_mean"]) for i in cohort]
        fronts = nondominated_sort(pts)
        selected: List[int] = []
        for fr in fronts:
            cand_idx = [cohort[i] for i in fr]
            if len(selected) + len(cand_idx) <= to_promote:
                selected += cand_idx
            else:
                cd = crowding_distance(fr, pts)
                fr_sorted = sorted(cand_idx, key=lambda k: cd.get(cohort.index(k), 0.0), reverse=True)
                need = to_promote - len(selected)
                selected += fr_sorted[:need]
                break

        # promote selected
        for j in selected:
            self.rung_index[j] = min(self.rung_index[j] + 1, len(self.cfg.rung_defs) - 1)

        self.rung_promoted[rung] = already + len(selected)

        # eliminate the worst 'quota' (approx.) and respawn globally
        eliminated = [i for i in cohort if i not in selected]
        # keep population size stable by respawn
        for j in eliminated:
            # respawn around good archive or random
            if len(self.archive) > 0:
                a_idx = self.rng.randrange(len(self.archive))
                u_base = self.space.to_unit(self.archive[a_idx][0])
            else:
                u_base = self.space.random_sample_unit(self.rng)
            c = self._calibrate_c()
            u_new = self._levy_global_step(u_base, c)
            self.population[j] = self.space.from_unit(u_new)
            self.population_U[j] = u_new
            self.fitness[j] = {"S_robust_mean": float("inf"), "FLOPs": float("inf"), "RMSE_mean_H1_6": float("inf")}
            self.rung_index[j] = 0

    def run(self, resume_from: Optional[str] = None, ckpt_dir: Optional[str] = None,
            save_every_n_ffe: int = 10, heartbeat_interval: int = 60,
            no_progressbar: bool = False) -> Tuple[List[Tuple[Dict[str, Any], Dict[str, Any]]], List[Dict[str, Any]]]:
        """
        Jalankan optimasi IFPOA-X dengan dukungan checkpoint/resume, heartbeat, dan progress bar.
        
        Args:
            resume_from: Path ke checkpoint untuk resume (opsional)
            ckpt_dir: Directory untuk menyimpan checkpoint (default: artifacts_ifpoax/)
            save_every_n_ffe: Simpan checkpoint setiap N FFE (default: 10)
            heartbeat_interval: Interval heartbeat dalam detik (default: 60)
            no_progressbar: Nonaktifkan progress bar (default: False)
        """
        try:
            from tqdm import tqdm
            _HAS_TQDM = True
        except ImportError:
            _HAS_TQDM = False
            def tqdm(iterable, *args, **kwargs):
                return iterable
        
        from ..utils import mlflow_utils as MU
        start_time = time.time()
        last_heartbeat_time = time.time()
        
        # Setup checkpoint directory
        if ckpt_dir is None:
            ckpt_dir = os.path.join("project", "artifacts_ifpoax")
        os.makedirs(ckpt_dir, exist_ok=True)
        
        # Generate checkpoint filename — harus cocok dengan pola di run_hpo_ifpoax.py:
        # checkpoint_ifpoax_{site_group}_{model_type}_{feature_scheme_suffix}.pkl
        site_group = "multisite" if self.cfg.site == "combined" else "singlesite"
        feature_scheme_suffix = self.cfg.feature_scheme.replace("mrmr_", "")
        model_slug = self.cfg.model_type
        ckpt_filename = f"checkpoint_ifpoax_{site_group}_{model_slug}_{feature_scheme_suffix}.pkl"
        ckpt_path = os.path.join(ckpt_dir, ckpt_filename)
        
        # Resume dari checkpoint jika diberikan; handle corrupt/empty files gracefully
        if resume_from and os.path.exists(resume_from):
            try:
                self.load_checkpoint(resume_from)
                print(f"[IFPOAX Resume] Continuing optimization from t={self.t}")
                # Validasi: budget_ffe harus >= t yang sudah berjalan.
                # budget_ffe = TOTAL target, bukan tambahan. Jika user salah set budget < t,
                # beri peringatan keras agar tidak bingung "run2_evals=0".
                if self.t >= self.cfg.budget_ffe:
                    print(
                        f"[IFPOAX Resume] PERINGATAN: budget_ffe={self.cfg.budget_ffe} <= "
                        f"t_loaded={self.t}. Optimizer akan langsung selesai tanpa evaluasi baru. "
                        f"Pastikan budget_ffe diset ke TOTAL target (misal 200), bukan tambahan."
                    )
                # **ENSURE _last_eval_time is initialized after checkpoint load**
                if not self._last_eval_time or len(self._last_eval_time) != self.cfg.population:
                    self._last_eval_time = [float("-inf")] * self.cfg.population
            except (EOFError, pickle.UnpicklingError, Exception) as e:
                print(f"[IFPOAX Resume] Warning: Failed to load checkpoint '{resume_from}': {e}")
                print("[IFPOAX Resume] Starting from scratch and backing up the bad checkpoint.")
                # Back up the problematic checkpoint to .bad timestamp
                try:
                    bad_path = resume_from + f".bad_{int(time.time())}"
                    shutil.move(resume_from, bad_path)
                    print(f"[IFPOAX Resume] Backed up bad checkpoint to {bad_path}")
                except Exception:
                    # If backup fails, continue without interrupting run
                    pass
                self.initialize()
        else:
            self.initialize()
        
        # Setup progress bar
        if not no_progressbar and _HAS_TQDM:
            pbar = tqdm(total=self.cfg.budget_ffe, desc="IFPOA-X HPO", unit="FFE", initial=self.t)
        else:
            pbar = None

        while self.t < self.cfg.budget_ffe and (time.time() - start_time) / 3600.0 < self.cfg.max_time_hours:
            # ===== Pick a candidate to (re-)evaluate at its current rung =====
            # **OPTIMIZATION: Select candidate smartly**
            # Prioritize: 1) unevaluated (inf), 2) oldest last_eval_time, 3) random
            unevaluated = [i for i in range(self.cfg.population) if self.fitness[i]["S_robust_mean"] == float("inf")]
            if unevaluated:
                idx = self.rng.choice(unevaluated)
            else:
                # All evaluated: pick oldest by last_eval_time (to refresh stale entries)
                # **SAFETY: Ensure _last_eval_time has correct length**
                if not self._last_eval_time or len(self._last_eval_time) != self.cfg.population:
                    self._last_eval_time = [float("-inf")] * self.cfg.population
                idx = int(np.argmin(self._last_eval_time))

            curr_rung = self.rung_index[idx]
            rung_def = dict(self.cfg.rung_defs[min(curr_rung, len(self.cfg.rung_defs) - 1)])
            rung_def["rung"] = curr_rung

            # Evaluate/refresh parent's fitness at its rung
            theta = self.space.clip_project(self.population[idx])
            fit = self._evaluate_and_log(theta, rung_def)  # **Uses cache**
            self.t += 1  # FFE++ untuk evaluasi parent
            self.fitness[idx] = fit
            self._last_eval_time[idx] = time.time()  # **Track last eval time**
            self._pareto_update(theta, fit)
            self._surrogate_add(self.space.to_unit(theta), fit)

            # Update best S
            improved = False
            if fit["S_robust_mean"] < self.best_S - 1e-9:
                self.best_S = float(fit["S_robust_mean"])
                self.last_improve_t = self.t
                improved = True

            # Safely compute mean R2 dan MAE lintas horizon (jika tersedia)
            per_h = fit.get("per_h_summary", {}) or {}
            r2_vals: List[float] = []
            mae_vals: List[float] = []
            for _h, _m in per_h.items():
                if not isinstance(_m, dict):
                    continue
                r2_val = _m.get("r2", None)
                mae_val = _m.get("mae", None)
                try:
                    if r2_val is not None and np.isfinite(float(r2_val)):
                        r2_vals.append(float(r2_val))
                except Exception:
                    pass
                try:
                    if mae_val is not None and np.isfinite(float(mae_val)):
                        mae_vals.append(float(mae_val))
                except Exception:
                    pass
            r2_mean = float(np.mean(r2_vals)) if r2_vals else float("nan")
            mae_mean = float(np.mean(mae_vals)) if mae_vals else float("nan")

            # History (after parent eval) – tambahkan R2_mean dan MAE_mean untuk monitoring
            # Tambahan debug-signal: simpan theta + hash agar mudah mendeteksi
            # apakah evaluasi berulang terjadi pada konfigurasi yang sama.
            try:
                theta_hash = self.space.hash_theta(theta)
            except Exception:
                theta_hash = ""
            self.history.append({
                "t": self.t,
                "idx": idx,
                "rung": curr_rung,
                "S": float(fit["S_robust_mean"]),
                "RMSE_mean": float(fit["RMSE_mean_H1_6"]),
                "FLOPs": float(fit["FLOPs"]),
                "best_S": float(self.best_S),
                "diversity": float(self._diversity()),
                "R2_mean": r2_mean,
                "MAE_mean": mae_mean,
                "theta": dict(theta),
                "theta_hash": theta_hash,
                "phase": "parent_eval",
                "cache_hit": False,
                "improved": improved,
            })
             # ... di dalam while-loop utama, setelah self.history.append({...}) dan logging berkala ...

                # === (NEW) OBL trigger (maks 1 evaluasi OBL per iterasi) ===
            #if self.cfg.use_obl:
                    # Pastikan tidak melewati budget/time; OBL juga konsumsi FFE bila benar-benar evaluasi.
                  # if (self.t + 1) < self.cfg.budget_ffe and (time.time() - start_time) / 3600.0 < self.cfg.max_time_hours:
                        # Terapkan OBL pada rung aktif kandidat yang baru diproses (current_rung)
                        #self._maybe_apply_obl(curr_rung)
                        # Catatan penting:
                        # _maybe_apply_obl() di atas memanggil _apply_obl_once(), yang melakukan 1 evaluasi config opposite.
                        # Untuk menjaga counting FFE adil, tambahkan 1 ke self.t DI SINI jika dan hanya jika OBL benar-benar melakukan evaluasi.
                        # Kita cek via delta pada counter 'obl_applied' (atau pakai flag return).
                        # Sederhana: selalu tambah FFE 1 saat OBL window aktif.
                        #self.t += 1
            # === OBL trigger (maks 1 evaluasi OBL per iterasi) ===
            if self.cfg.use_obl:
                if (self.t < self.cfg.budget_ffe) and ((time.time() - start_time) / 3600.0 < self.cfg.max_time_hours):
                    did_eval_obl = self._maybe_apply_obl(curr_rung)  # return bool
                    if did_eval_obl:
                        self.t += 1  # FFE++ hanya jika _really_ ada 1 evaluasi OBL

                # inkremen FFE untuk evaluasi utama iterasi ini
            #self.t += 1
            
            # ===== OBL Flags =====
            self.history[-1]["obl_next_due"] = (self.t % max(1, self.cfg.obl_frequency) == 0)
            self.history[-1]["obl_applied"] = int(self.obl_applied)
            self.history[-1]["obl_accepted"] = int(self.obl_accepted)

            # ===== ASHA promotion/elimination (asynchronous) =====
            self._asha_promote_eliminate(curr_rung)

            # ===== Choose operator by bandit (UCB1) =====
            arm = self._bandit_select()
            c_scale = self._calibrate_c()
            u_parent = self.space.to_unit(self.population[idx])
            try:
                mlflow.log_metrics({
                    "ifpoax.c_scale": float(c_scale),
                    "ifpoax.arm_global_prob": float(self.bandit_N["global"] / max(1, (self.bandit_N["global"] + self.bandit_N["local"]))),
                })
            except Exception:
                pass


            if arm == "global":
                u_child = self._levy_global_step(u_parent, c_scale)
            else:
                u_child = self._jade_local_step(u_parent)

            theta_child = self.space.from_unit(u_child)

            # ===== Cheap screen via k-NN surrogate =====
            do_eval_child = True
            if self.cfg.use_knn_screen:
                pred_S, _pred_F = self._knn_predict(u_child, self.cfg.knn_k)
                # only proceed if predicted S is promising vs parent's last S (quantile gate)
                parent_S = float(self.fitness[idx]["S_robust_mean"])
                do_eval_child = (pred_S < parent_S * (1.0 - self.cfg.screen_quantile * 0.1))  # moderate gate

            hv_before = self._hv()


            if do_eval_child:
                child_fit = self._evaluate_and_log(
                    theta_child, {"rung": self.rung_index[idx], **self.cfg.rung_defs[self.rung_index[idx]]}
                )
                self.t += 1  # FFE++ untuk evaluasi child
                self._surrogate_add(u_child, child_fit)
                try:
                    child_theta_hash = self.space.hash_theta(theta_child)
                except Exception:
                    child_theta_hash = ""
                self.history.append({
                    "t": self.t,
                    "idx": idx,
                    "rung": curr_rung,
                    "S": float(child_fit["S_robust_mean"]),
                    "RMSE_mean": float(child_fit["RMSE_mean_H1_6"]),
                    "FLOPs": float(child_fit["FLOPs"]),
                    "best_S": float(self.best_S),
                    "diversity": float(self._diversity()),
                    "phase": "child_eval",
                    "cache_hit": False,
                    "accepted": False,
                    "theta_hash": child_theta_hash,
                    "operator": arm,
                })
            else:
                child_fit = None
                self.history.append({
                    "t": self.t,
                    "idx": idx,
                    "rung": curr_rung,
                    "S": float(self.fitness[idx]["S_robust_mean"]),
                    "RMSE_mean": float(self.fitness[idx]["RMSE_mean_H1_6"]),
                    "FLOPs": float(self.fitness[idx]["FLOPs"]),
                    "best_S": float(self.best_S),
                    "diversity": float(self._diversity()),
                    "phase": "cheap_screen_skip",
                    "cache_hit": False,
                    "accepted": False,
                    "reason": "predicted_s_not_promising",
                })

            accept = False
            if child_fit is not None:
                # Parent-child selection by Pareto rank -> crowding -> S then FLOPs
                pts_pair = [
                    (self.fitness[idx]["RMSE_mean_H1_6"], self.fitness[idx]["S_robust_mean"]),
                    (child_fit["RMSE_mean_H1_6"], child_fit["S_robust_mean"])
                ]
                fronts_pair = nondominated_sort(pts_pair)
                if len(fronts_pair) > 0:
                    if 1 in fronts_pair[0]:  # child in best front
                        if 0 not in fronts_pair[0]:
                            accept = True
                        else:
                            # both non-dominated: tie-break by RMSE then S_robust
                            cond_rmse = (pts_pair[1][0] < pts_pair[0][0] - 1e-12)
                            cond_srob = (abs(pts_pair[1][0] - pts_pair[0][0]) < 1e-12 and pts_pair[1][1] < pts_pair[0][1] - 1e-12)
                            accept = (cond_rmse or cond_srob)

            if accept:
                self.population[idx] = theta_child
                self.population_U[idx] = u_child
                self.fitness[idx] = child_fit  # type: ignore
                self._last_eval_time[idx] = time.time()  # **Track last eval time**
                self._pareto_update(theta_child, child_fit)  # type: ignore
                if child_fit["S_robust_mean"] < self.best_S - 1e-9:  # type: ignore
                    self.best_S = float(child_fit["S_robust_mean"])  # type: ignore
                    self.last_improve_t = self.t
                self.accept_hist.append(True)
                # **Mark child as accepted in history**
                if child_fit is not None and self.history and self.history[-1].get("phase") == "child_eval":
                    self.history[-1]["accepted"] = True
            else:
                self.accept_hist.append(False)

            # ===== Bandit reward from HV gain =====
            hv_after = self._hv()
            ref = self._hv_reference()
            ref_area = max(1e-12, (ref[0]) * (ref[1]))
            reward = max(0.0, (hv_after - hv_before) / ref_area)
            self._bandit_update(arm, reward)

            # ===== HPO Metrics Logging (sesuai spec) =====
            # Log hpo.ffe, hpo.best_rmse, hpo.nondom_size setiap FFE
            best_rmse = min([f[1]["RMSE_mean_H1_6"] for f in self.archive]) if self.archive else float('inf')
            mlflow.log_metrics({
                "hpo.ffe": float(self.t),
                "hpo.best_rmse": float(best_rmse),
                "hpo.nondom_size": float(len(self.archive)),
            }, step=self.t)
            
            # ===== Periodic detailed logging =====
            if self.t % 5 == 0:
                mlflow.log_metrics({
                    "ifpoax.diversity": float(self._diversity()),
                    "ifpoax.acc_ratio": float(np.mean(self.accept_hist[-20:]) if self.accept_hist else 0.0),
                    "ifpoax.best_S": float(self.best_S),
                    "ifpoax.archive_size": float(len(self.archive)),
                    "ifpoax.hv": float(hv_after),
                    "ifpoax.bandit.global.meanR": float(self.bandit_sumR["global"] / max(1, self.bandit_N["global"])),
                    "ifpoax.bandit.local.meanR": float(self.bandit_sumR["local"] / max(1, self.bandit_N["local"])),
                }, step=self.t)
            
            # ===== Heartbeat logging =====
            current_time = time.time()
            if current_time - last_heartbeat_time >= heartbeat_interval:
                progress = self.t / self.cfg.budget_ffe
                MU.heartbeat(heartbeat_interval, progress=progress, step=self.t)
                last_heartbeat_time = current_time
            
            # Update progress bar
            if pbar is not None:
                pbar.update(1)
                pbar.set_postfix({
                    "best_rmse": f"{best_rmse:.4f}",
                    "nondom": len(self.archive),
                    "best_S": f"{self.best_S:.4f}"
                })
            
            # Simpan checkpoint berkala dan log ke MLflow
            if self.t % save_every_n_ffe == 0:
                self.save_checkpoint(ckpt_path)
                MU.log_checkpoint(ckpt_path, artifact_path="checkpoints/hpo")
        
        # Close progress bar
        if pbar is not None:
            pbar.close()
        
        # Simpan checkpoint final dan log ke MLflow
        self.save_checkpoint(ckpt_path)
        MU.log_checkpoint(ckpt_path, artifact_path="checkpoints/hpo")
        
        # Final heartbeat
        MU.heartbeat(heartbeat_interval, progress=1.0, step=self.t)
        
        print(f"[IFPOAX] Optimization completed. Final t={self.t}, archive_size={len(self.archive)}")

        return self.archive, self.history

    def save_checkpoint(self, path: str):
        """
        Simpan state lengkap IFPOAXOptimizer untuk resume.
        
        Args:
            path: Path untuk menyimpan checkpoint (akan disimpan sebagai pickle)
        """
        import random
        state = {
            # Counter & tracking
            't': self.t,
            'last_improve_t': self.last_improve_t,
            'best_S': self.best_S,
            
            # Population & fitness
            'population': copy.deepcopy(self.population),
            'population_U': copy.deepcopy(self.population_U),
            'fitness': copy.deepcopy(self.fitness),
            'rung_index': copy.deepcopy(self.rung_index),
            
            # Archive & history
            'archive': copy.deepcopy(self.archive),
            'history': copy.deepcopy(self.history),
            
            # ASHA tracking
            'rung_promoted': copy.deepcopy(self.rung_promoted),
            
            # Bandit state
            'bandit_N': copy.deepcopy(self.bandit_N),
            'bandit_sumR': copy.deepcopy(self.bandit_sumR),
            
            # JADE archive
            'jade_ext_archive_U': copy.deepcopy(self.jade_ext_archive_U),
            
            # Surrogate data
            '_surrogate_X': copy.deepcopy(self._surrogate_X),
            '_surrogate_Y': copy.deepcopy(self._surrogate_Y),
            
            # OBL tracking
            'obl_applied': self.obl_applied,
            'obl_accepted': self.obl_accepted,
            
            # Acceptance history
            'accept_hist': copy.deepcopy(self.accept_hist),

            # Adaptive step-scale state (terpisah dari cfg agar cfg tetap immutable)
            '_c0': self._c0,

            # RNG states
            'rng_state': {
                'python': self.rng.getstate(),
                'numpy': np.random.get_state(),
                'torch': torch.get_rng_state(),
                'cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            },
            
            # Config (untuk validasi)
            'cfg_dict': {
                'population': self.cfg.population,
                'budget_ffe': self.cfg.budget_ffe,
                'max_time_hours': self.cfg.max_time_hours,
                'seed': self.cfg.seed,
                'site': self.cfg.site,
                'mode': self.cfg.mode,
                'preset': self.cfg.preset,  # Save preset untuk validasi
            }
        }
        
        # Buat directory jika belum ada
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)

        # Simpan secara atomik: tulis ke file sementara lalu ganti
        tmp_path = path + ".tmp"
        try:
            with open(tmp_path, 'wb') as f:
                pickle.dump(state, f)
            # atomic replace
            shutil.move(tmp_path, path)
            print(f"[IFPOAX Checkpoint] Saved state at t={self.t} -> {path}")
        finally:
            # clean tmp if exists
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
        
        # Log ke MLflow sebagai artifact
        try:
            mlflow.log_artifact(path)
        except Exception as e:
            print(f"[IFPOAX Checkpoint] Warning: Failed to log checkpoint to MLflow: {e}")

    def load_checkpoint(self, path: str):
        """
        Muat state IFPOAXOptimizer dari checkpoint.
        
        Args:
            path: Path ke checkpoint file
        """
        import random
        if not os.path.exists(path):
            raise FileNotFoundError(f"IFPOAX checkpoint not found: {path}")
        
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        # Restore counter & tracking
        self.t = state['t']
        self.last_improve_t = state.get('last_improve_t', 0)
        self.best_S = state.get('best_S', float('inf'))
        
        # Restore population & fitness
        self.population = state['population']
        self.population_U = state['population_U']
        self.fitness = state['fitness']
        self.rung_index = state['rung_index']
        
        # Restore archive & history
        self.archive = state['archive']
        self.history = state['history']
        
        # Restore ASHA tracking
        self.rung_promoted = state.get('rung_promoted', {})
        
        # Restore bandit state
        self.bandit_N = state.get('bandit_N', {"global": 1, "local": 1})
        self.bandit_sumR = state.get('bandit_sumR', {"global": 0.0, "local": 0.0})
        
        # Restore JADE archive
        self.jade_ext_archive_U = state.get('jade_ext_archive_U', [])
        
        # Restore surrogate data
        self._surrogate_X = state.get('_surrogate_X', [])
        self._surrogate_Y = state.get('_surrogate_Y', [])
        
        # Restore OBL tracking
        self.obl_applied = state.get('obl_applied', 0)
        self.obl_accepted = state.get('obl_accepted', 0)
        
        # Restore acceptance history
        self.accept_hist = state.get('accept_hist', [])

        # Restore adaptive step-scale state
        # Fallback ke self.cfg.c0 untuk kompatibilitas dengan checkpoint lama
        self._c0 = state.get('_c0', self.cfg.c0)

        # Restore RNG states
        if 'rng_state' in state:
            rng_state = state['rng_state']
            self.rng.setstate(rng_state['python'])
            np.random.set_state(rng_state['numpy'])
            torch.set_rng_state(rng_state['torch'])
            if torch.cuda.is_available() and rng_state.get('cuda') is not None:
                torch.cuda.set_rng_state_all(rng_state['cuda'])
        
        # Validasi config (opsional, hanya warning jika berbeda)
        if 'cfg_dict' in state:
            cfg_dict = state['cfg_dict']
            mismatches = []
            if cfg_dict.get('site') != self.cfg.site:
                mismatches.append(f"site: {cfg_dict.get('site')} != {self.cfg.site}")
            if cfg_dict.get('mode') != self.cfg.mode:
                mismatches.append(f"mode: {cfg_dict.get('mode')} != {self.cfg.mode}")
            if cfg_dict.get('preset') != self.cfg.preset:
                mismatches.append(f"preset: {cfg_dict.get('preset')} != {self.cfg.preset}")
                print(f"[IFPOAX Checkpoint] WARNING: Preset mismatch! "
                      f"Checkpoint was created with preset={cfg_dict.get('preset')}, "
                      f"but current preset={self.cfg.preset}. "
                      f"This may cause search space mismatch (e.g., batch_size choices).")
            if mismatches:
                print(f"[IFPOAX Checkpoint] Warning: Config mismatch detected: {', '.join(mismatches)}")
        
        print(f"[IFPOAX Checkpoint] Loaded state from t={self.t}, archive_size={len(self.archive)}, "
              f"best_S={self.best_S:.4f}")
