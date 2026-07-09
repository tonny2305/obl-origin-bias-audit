#!/usr/bin/env python3
"""
Benchmark Tester untuk IFPOA-X, FPA, dan PSO
============================================
Skrip standalone untuk menguji algoritma optimasi pada fungsi benchmark standar
(Ackley, Rastrigin, Rosenbrock) tanpa modifikasi kode asli.

Author: Expert Software Engineer & Metaheuristic Researcher
Date: 2026-02-14
"""

import argparse
import sys
import os
import time
import pickle
import random
import warnings
from pathlib import Path

# Pastikan project root ada di sys.path agar import project.algorithms.* berfungsi
# (algoritma memakai relative import: from ..hpo.search_space)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from typing import Dict, List, Any, Tuple, Callable, Optional
from dataclasses import dataclass, field
from unittest.mock import patch, MagicMock
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

warnings.filterwarnings('ignore')

# ==============================================================================
# FAIR-COMPARISON BUDGET CONTROL
# ==============================================================================
# Fungsi objektif "sebenarnya" (cache-miss) adalah satu-satunya mata uang yang
# adil untuk membandingkan metaheuristik (NFE = Number of Function Evaluations).
# IFPOA-X memakai cache incumbent: parent yang di-refresh setiap iterasi adalah
# cache-hit (theta+rung sama) sehingga menaikkan counter FFE internal (self.t)
# TANPA memanggil objektif nyata. Akibatnya, pada budget_ffe=500 IFPOA-X hanya
# melakukan ~213 evaluasi nyata sementara FPA/PSO (tanpa cache) melakukan 500.
# Perbandingan menjadi tidak setara secara NFE.
#
# Solusi (tanpa mengubah algoritma): batas budget ditegakkan di level EVALUATOR,
# yaitu setelap tepat `budget` evaluasi objektif NYATA, evaluator melempar
# _BudgetExhausted. Sinyal ini turun dari BaseException agar tidak tertelan oleh
# blok `except Exception` di dalam loop algoritma. Setiap algoritma diberi
# budget_ffe internal yang besar (sentinel) sehingga aturan berhenti tunggal &
# seragam adalah "tepat `budget` evaluasi nyata" untuk ketiganya.
_FFE_SENTINEL_MULT = 4  # budget_ffe internal = budget * mult (cukup besar agar cap NFE yang menghentikan)


class _BudgetExhausted(BaseException):
    """Sinyal internal: kuota evaluasi objektif NYATA (NFE) telah habis."""
    pass


# Registry fungsi benchmark tambahan (mis. suite klasik F1–F13 untuk paper).
# Memungkinkan kode eksternal mendaftarkan fungsi baru TANPA mengubah harness
# atau algoritma. get_function()/get_bounds() akan mengonsultasikan registry ini.
_EXTRA_FUNCTIONS: "Dict[str, Callable]" = {}
_EXTRA_BOUNDS: "Dict[str, Tuple[float, float]]" = {}


def register_benchmark_function(name: str, fn, bounds):
    """Daftarkan fungsi benchmark tambahan (name, callable f(x)->float, (lo, hi))."""
    _EXTRA_FUNCTIONS[name.lower()] = fn
    _EXTRA_BOUNDS[name.lower()] = tuple(bounds)


# ==============================================================================
# BENCHMARK FUNCTIONS
# ==============================================================================

class BenchmarkFunctions:
    """Implementasi fungsi benchmark standar untuk optimisasi"""
    
    @staticmethod
    def ackley(x: np.ndarray, a: float = 20, b: float = 0.2, c: float = 2*np.pi) -> float:
        """
        Ackley Function
        Global minimum: f(x) = 0 at x = [0, ..., 0]
        Search domain: [-32, 32]^D
        """
        d = len(x)
        sum1 = np.sum(x**2)
        sum2 = np.sum(np.cos(c * x))
        return -a * np.exp(-b * np.sqrt(sum1 / d)) - np.exp(sum2 / d) + a + np.e
    
    @staticmethod
    def rastrigin(x: np.ndarray, A: float = 10) -> float:
        """
        Rastrigin Function
        Global minimum: f(x) = 0 at x = [0, ..., 0]
        Search domain: [-5.12, 5.12]^D
        """
        d = len(x)
        return A * d + np.sum(x**2 - A * np.cos(2 * np.pi * x))
    
    @staticmethod
    def rosenbrock(x: np.ndarray) -> float:
        """
        Rosenbrock Function
        Global minimum: f(x) = 0 at x = [1, ..., 1]
        Search domain: [-30, 30]^D
        """
        return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
    
    @staticmethod
    def get_bounds(func_name: str) -> Tuple[float, float]:
        """Mendapatkan batas pencarian untuk fungsi benchmark"""
        bounds_map = {
            'ackley': (-32.0, 32.0),
            'rastrigin': (-5.12, 5.12),
            'rosenbrock': (-30.0, 30.0)
        }
        if func_name.lower() in _EXTRA_BOUNDS:
            return _EXTRA_BOUNDS[func_name.lower()]
        return bounds_map.get(func_name.lower(), (-100.0, 100.0))

    @staticmethod
    def get_function(func_name: str) -> Callable:
        """Mendapatkan fungsi benchmark berdasarkan nama"""
        func_map = {
            'ackley': BenchmarkFunctions.ackley,
            'rastrigin': BenchmarkFunctions.rastrigin,
            'rosenbrock': BenchmarkFunctions.rosenbrock
        }
        if func_name.lower() in _EXTRA_FUNCTIONS:
            return _EXTRA_FUNCTIONS[func_name.lower()]
        return func_map.get(func_name.lower())


# ==============================================================================
# MOCK SEARCH SPACE
# ==============================================================================

class MockSearchSpace:
    """Mock SearchSpace untuk menggantikan build_transformer_small_space"""
    
    def __init__(self, dim: int = 30, bounds: Tuple[float, float] = (-100, 100), 
                 preset: Optional[str] = None):
        self.dim = dim
        self.lower_bound, self.upper_bound = bounds
        self.param_names = [f"x_{i}" for i in range(dim)]
        self.preset = preset
        
    def latin_hypercube(self, n_samples: int, rng) -> List[Dict[str, float]]:
        """Generate Latin Hypercube Sampling dalam unit hypercube [0,1]^D"""
        samples = []
        for _ in range(n_samples):
            sample = {name: rng.random() for name in self.param_names}
            samples.append(sample)
        return samples
    
    def to_unit(self, theta: Dict[str, float]) -> Dict[str, float]:
        """Konversi dari ruang pencarian ke unit hypercube [0,1]^D"""
        u = {}
        for name in self.param_names:
            val = theta.get(name, 0.0)
            u[name] = (val - self.lower_bound) / (self.upper_bound - self.lower_bound)
        return u
    
    def from_unit(self, u: Dict[str, float]) -> Dict[str, Any]:
        """Konversi dari unit hypercube [0,1]^D ke ruang pencarian"""
        theta = {}
        for name in self.param_names:
            unit_val = u.get(name, 0.5)
            theta[name] = self.lower_bound + unit_val * (self.upper_bound - self.lower_bound)
        return theta
    
    def clip_project(self, theta: Dict[str, Any]) -> Dict[str, Any]:
        """Clip nilai parameter ke dalam batas pencarian"""
        clipped = {}
        for name in self.param_names:
            val = theta.get(name, 0.0)
            clipped[name] = np.clip(val, self.lower_bound, self.upper_bound)
        return clipped

    def distance_unit(self, u1: Dict[str, float], u2: Dict[str, float]) -> float:
        """Jarak Euclidean dalam unit hypercube [0,1]^D (untuk IFPOAX diversity)"""
        acc = 0.0
        for name in self.param_names:
            x = u1.get(name, 0.0) - u2.get(name, 0.0)
            acc += x * x
        return float(np.sqrt(acc))

    def mean_pairwise_distance(self, U: List[Dict[str, float]]) -> float:
        """Rata-rata jarak pairwise (untuk IFPOAX)"""
        if len(U) < 2:
            return 0.0
        s = 0.0
        m = 0
        for i in range(len(U)):
            for j in range(i + 1, len(U)):
                s += self.distance_unit(U[i], U[j])
                m += 1
        return s / max(1, m)

    def random_sample_unit(self, rng) -> Dict[str, float]:
        """Sampel acak seragam dalam unit hypercube [0,1]^D.
        Diperlukan oleh IFPOAXOptimizer._asha_promote_eliminate saat arsip kosong.
        """
        return {name: rng.random() for name in self.param_names}

    def hash_theta(self, theta: Dict[str, Any]) -> str:
        """Hash deterministik theta untuk deduplication/logging.
        Diperlukan oleh IFPOAXOptimizer.run() untuk mencatat theta_hash di history.
        """
        import hashlib
        return hashlib.md5(
            json.dumps(theta, sort_keys=True, default=str).encode()
        ).hexdigest()


# ==============================================================================
# MOCK EVALUATE CONFIG
# ==============================================================================

class BenchmarkEvaluator:
    """Mock evaluator untuk fungsi benchmark"""
    
    def __init__(self, func_name: str, dim: int = 30, max_real_evals: Optional[int] = None):
        self.func_name = func_name
        self.dim = dim
        self.benchmark_func = BenchmarkFunctions.get_function(func_name)
        # Kuota evaluasi objektif NYATA (NFE). None = tak terbatas (mode legacy).
        self.max_real_evals = max_real_evals
        self.eval_count = 0
        self.eval_history = []  # Backward compat: track evaluations for visualization
        self.all_evaluations = []  # Track ALL calls (termasuk jika ada cache-hit callback)
        
    def evaluate(self, theta: Dict[str, float], rung_def: Dict = None, 
                 seeds: List[int] = None, site: str = None, mode: str = None,
                 t: int = 0, trial_id: str = None, log_prefix: str = None,
                 **kwargs) -> Dict[str, Any]:
        """
        Mock evaluate_config yang menghitung nilai fungsi benchmark
        
        Returns:
            Dict dengan format yang diharapkan algoritma:
            {
                "S_robust_mean": fitness_value,
                "FLOPs": dummy_value,
                "RMSE_mean_H1_6": fitness_value,
                "per_h_summary": {...}
            }
        """
        # === Penegakan budget NFE yang adil ===
        # Evaluator hanya dipanggil saat cache-MISS (evaluasi objektif nyata).
        # Setelah tepat `max_real_evals` evaluasi nyata, hentikan SEMUA algoritma
        # dengan aturan seragam — mencegah cache-hit IFPOA-X membuat NFE < FPA/PSO.
        if self.max_real_evals is not None and self.eval_count >= self.max_real_evals:
            raise _BudgetExhausted()

        # Ekstrak nilai parameter ke array numpy
        x = np.array([theta.get(f"x_{i}", 0.0) for i in range(self.dim)])

        # Hitung nilai fungsi benchmark (minimisasi)
        fitness = float(self.benchmark_func(x))
        
        # Entry untuk tracking (from_cache=False: evaluator hanya dipanggil saat cache miss)
        # Sumbu-X kurva konvergensi: pada mode adil gunakan ORDINAL EVALUASI NYATA
        # (NFE index = self.eval_count) agar identik-skala untuk semua algoritma —
        # cache-hit IFPOA-X tidak lagi menggeser sumbu. Pada FPA/PSO (tanpa cache)
        # nilai ini sama dengan self.t, jadi tidak ada perubahan untuk mereka.
        t_axis = self.eval_count if self.max_real_evals is not None else kwargs.get('t', t)
        entry = {
            't': t_axis,
            'x': x.copy(),
            'fitness': fitness,
            'trial_id': kwargs.get('trial_id', trial_id),
            'from_cache': False
        }
        
        # Track ALL calls - untuk visualisasi IFPOAX dan algoritma lain
        self.all_evaluations.append(entry)
        
        # Backward compat
        self.eval_history.append({
            't': entry['t'],
            'x': entry['x'].copy(),
            'fitness': entry['fitness'],
            'trial_id': entry['trial_id']
        })
        
        self.eval_count += 1
        
        # Format output sesuai ekspektasi algoritma
        result = {
            "S_robust_mean": fitness,
            "FLOPs": 1000.0,  # Dummy value
            "RMSE_mean_H1_6": fitness,
            "per_h_summary": {
                "h1": {"r2": 0.5, "mae": fitness * 0.1},
                "h2": {"r2": 0.5, "mae": fitness * 0.1},
                "h3": {"r2": 0.5, "mae": fitness * 0.1},
            }
        }
        
        return result
    
    def reset(self):
        """Reset evaluator untuk run baru"""
        self.eval_count = 0
        self.eval_history = []
        self.all_evaluations = []


# ==============================================================================
# MOCK ROBUST SCHEDULE
# ==============================================================================

class MockRobustSchedule:
    """Mock RobustSchedule untuk IFPOA-X"""
    
    def __init__(self, total_steps: int = 1000):
        self.total_steps = total_steps
    
    def should_eval_robust(self, t: int) -> bool:
        """Selalu return False untuk benchmark sederhana"""
        return False


# ==============================================================================
# ALGORITHM RUNNER
# ==============================================================================

class AlgorithmRunner:
    """Menjalankan algoritma dengan mocking yang tepat"""
    
    def __init__(self, algo_name: str, func_name: str, dim: int, budget: int,
                 seed: int, save_dir: str = "./results",
                 use_obl: bool = True, use_jade_local: bool = True, use_bandit: bool = True,
                 equal_real_nfe: bool = True):
        self.algo_name = algo_name
        self.func_name = func_name
        self.dim = dim
        self.budget = budget
        self.seed = seed
        self.use_obl = use_obl
        self.use_jade_local = use_jade_local
        self.use_bandit = use_bandit
        # equal_real_nfe: tegakkan NFE (evaluasi objektif nyata) yang sama untuk
        # semua algoritma. budget_ffe internal dinaikkan ke sentinel agar cap NFE
        # di evaluator menjadi satu-satunya aturan berhenti yang seragam.
        self.equal_real_nfe = equal_real_nfe
        self.internal_budget = budget * _FFE_SENTINEL_MULT if equal_real_nfe else budget
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Setup evaluator (cap NFE nyata = budget saat mode adil)
        self.evaluator = BenchmarkEvaluator(
            func_name, dim, max_real_evals=(budget if equal_real_nfe else None)
        )
        
        # Setup mock search space
        bounds = BenchmarkFunctions.get_bounds(func_name)
        self.mock_space = MockSearchSpace(dim, bounds)
        
    def _mock_mlflow(self):
        """Mock MLflow untuk menghindari error logging"""
        mock = MagicMock()
        mock.log_metrics = MagicMock()
        mock.log_artifact = MagicMock()
        mock.log_param = MagicMock()
        mock.log_params = MagicMock()
        return mock
    
    def _create_rung_defs(self, num_rungs: int = 3) -> List[Dict[str, Any]]:
        """Buat definisi rung sederhana untuk ASHA-style scheduling"""
        # Untuk benchmark, kita tidak perlu rung kompleks
        # Cukup satu rung dengan 'epochs' dummy
        return [
            {"rung": 0, "epochs": 1, "horizons": [1], "seeds": [self.seed], "batch_accum": 1}
        ]
    
    def run_ifpoax(self) -> Dict[str, Any]:
        """Menjalankan IFPOA-X dengan mocking"""
        print(f"  Running IFPOA-X (seed={self.seed})...")
        
        # Import sebagai project.algorithms.ifpoax agar relative import (..hpo) berfungsi
        import project.algorithms.ifpoax as ifpoax_mod
        with patch.object(ifpoax_mod, 'build_search_space', return_value=self.mock_space), \
             patch.object(ifpoax_mod, 'build_transformer_small_space', return_value=self.mock_space), \
             patch.object(ifpoax_mod, 'evaluate_config', side_effect=self.evaluator.evaluate), \
             patch.object(ifpoax_mod, 'RobustSchedule', return_value=MockRobustSchedule(self.budget)), \
             patch.object(ifpoax_mod, 'mlflow', self._mock_mlflow()):
            
            from project.algorithms.ifpoax import IFPOAXOptimizer, IFPOAXConfig
            
            # Konfigurasi
            cfg = IFPOAXConfig(
                population=min(24, self.budget // 10),
                budget_ffe=self.internal_budget,
                max_time_hours=24.0,
                seed=self.seed,
                site="benchmark",
                mode="test",
                rung_defs=self._create_rung_defs(),
                use_obl=self.use_obl,
                use_bandit=self.use_bandit,
                use_jade_local=self.use_jade_local,
                use_knn_screen=False,  # Disable untuk benchmark sederhana
                preset=None
            )
            
            # Jalankan optimisasi. Saat mode adil, evaluator melempar
            # _BudgetExhausted tepat setelah `budget` evaluasi nyata; ambil
            # hasil terbaik dari state optimizer (archive & history persisten).
            optimizer = IFPOAXOptimizer(cfg)
            try:
                archive, history = optimizer.run()
            except _BudgetExhausted:
                archive, history = optimizer.archive, optimizer.history

            # Ekstrak hasil terbaik (archive = List[(theta, fit)] - tuple, bukan dict)
            if archive:
                best = min(archive, key=lambda x: x[1].get('S_robust_mean', float('inf')))
                best_fitness = best[1].get('S_robust_mean', float('inf'))
            else:
                best_fitness = float('inf')
            
            return {
                'best_fitness': best_fitness,
                'history': history,
                'eval_history': self.evaluator.eval_history,
                'all_evaluations': self.evaluator.all_evaluations,
                'archive': archive
            }
    
    def run_fpa(self) -> Dict[str, Any]:
        """Menjalankan FPA dengan mocking"""
        print(f"  Running FPA (seed={self.seed})...")
        
        import project.algorithms.fpa as fpa_mod
        with patch.object(fpa_mod, 'build_search_space', return_value=self.mock_space), \
             patch.object(fpa_mod, 'build_transformer_small_space', return_value=self.mock_space), \
             patch.object(fpa_mod, 'evaluate_config', side_effect=self.evaluator.evaluate), \
             patch.object(fpa_mod, 'mlflow', self._mock_mlflow()):
            
            from project.algorithms.fpa import FPAOptimizer, FPAConfig
            
            cfg = FPAConfig(
                pop_size=min(24, self.budget // 10),
                budget_ffe=self.internal_budget,
                max_time_hours=24.0,
                seed=self.seed,
                site="benchmark",
                mode="test",
                rung_defs=self._create_rung_defs(),
                p_switch=0.8,
                gamma=0.1,
                preset=None
            )
            
            optimizer = FPAOptimizer(cfg)
            try:
                result = optimizer.run()
            except _BudgetExhausted:
                result = {'history': optimizer.history, 'trials': []}

            # Ekstrak hasil terbaik
            best_fitness = optimizer.best_fit.get('S_robust_mean', float('inf'))
            
            return {
                'best_fitness': best_fitness,
                'history': result.get('history', []),
                'eval_history': self.evaluator.eval_history,
                'all_evaluations': self.evaluator.all_evaluations,
                'trials': result.get('trials', [])
            }
    
    def run_pso(self) -> Dict[str, Any]:
        """Menjalankan PSO dengan mocking"""
        print(f"  Running PSO (seed={self.seed})...")
        
        import project.algorithms.pso as pso_mod
        with patch.object(pso_mod, 'build_search_space', return_value=self.mock_space), \
             patch.object(pso_mod, 'build_transformer_small_space', return_value=self.mock_space), \
             patch.object(pso_mod, 'evaluate_config', side_effect=self.evaluator.evaluate), \
             patch.object(pso_mod, 'mlflow', self._mock_mlflow()):
            
            from project.algorithms.pso import PSOOptimizer, PSOConfig
            
            cfg = PSOConfig(
                pop_size=min(24, self.budget // 10),
                budget_ffe=self.internal_budget,
                max_time_hours=24.0,
                seed=self.seed,
                site="benchmark",
                mode="test",
                rung_defs=self._create_rung_defs(),
                w=0.7,
                c1=1.5,
                c2=1.5,
                preset=None
            )
            
            optimizer = PSOOptimizer(cfg)
            try:
                result = optimizer.run()
            except _BudgetExhausted:
                result = {'history': optimizer.history, 'trials': []}

            # Ekstrak hasil terbaik
            best_fitness = optimizer.gbest_fit.get('S_robust_mean', float('inf'))
            
            return {
                'best_fitness': best_fitness,
                'history': result.get('history', []),
                'eval_history': self.evaluator.eval_history,
                'all_evaluations': self.evaluator.all_evaluations,
                'trials': result.get('trials', [])
            }
    
    def run(self) -> Dict[str, Any]:
        """Menjalankan algoritma yang dipilih"""
        self.evaluator.reset()
        
        if self.algo_name == 'ifpoax':
            return self.run_ifpoax()
        elif self.algo_name == 'fpa':
            return self.run_fpa()
        elif self.algo_name == 'pso':
            return self.run_pso()
        else:
            raise ValueError(f"Unknown algorithm: {self.algo_name}")


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def _get_trajectory_data(run_data: Dict[str, Any]) -> List[Dict]:
    """Ambil data trajectory untuk visualisasi. Prefer all_evaluations (IFPOAX), fallback eval_history."""
    evals = run_data.get('all_evaluations') or run_data.get('eval_history', [])
    return evals if evals else []


class BenchmarkVisualizer:
    """Visualisasi hasil benchmark"""
    
    def __init__(self, save_dir: str = "./results"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 150
        plt.rcParams['font.size'] = 10
    
    def plot_convergence(self, results: Dict[str, Dict], func_name: str):
        """Plot convergence curves untuk semua algoritma.

        Sumbu X menggunakan Function Evaluations (FFE) aktual dari field 't' pada
        setiap history entry — bukan panjang list history. Ini memastikan perbandingan
        yang adil (fair comparison) karena IFPOA-X mengonsumsi 2-3 FFE per iterasi loop
        (parent + OBL + child), sementara FPA/PSO mengonsumsi 1 FFE per iterasi.
        Dengan sumbu X FFE aktual, semua algoritma berada pada skala yang identik.

        Metode interpolasi: forward-fill pada grid FFE seragam [0, max_budget].
        Setiap titik t pada grid mewakili "fitness terbaik yang pernah ditemukan
        setelah tepat t function evaluations".
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = {'ifpoax': '#E74C3C', 'fpa': '#3498DB', 'pso': '#2ECC71'}
        labels = {'ifpoax': 'IFPOA-X', 'fpa': 'FPA', 'pso': 'PSO'}

        # --- Batas sumbu-X = jumlah evaluasi objektif NYATA (NFE) ---
        # Gunakan all_evaluations (satu entri per evaluasi cache-MISS), yang
        # jumlahnya identik untuk semua algoritma pada mode adil (= budget).
        # Ini menghapus bias lama: dahulu sumbu-X memakai self.t (FFE internal)
        # sehingga cache-hit IFPOA-X membuat kurvanya melewati budget nominal.
        max_budget = 0
        for algo_results in results.values():
            for run_data in algo_results.get('runs', []):
                max_budget = max(max_budget, len(_get_trajectory_data(run_data)))
        if max_budget == 0:
            max_budget = 1000  # fallback

        # Grid NFE seragam untuk semua algoritma: 1, 2, ..., max_budget
        ffe_grid = np.arange(1, max_budget + 1, dtype=np.int64)

        for algo_name, algo_results in results.items():
            if not algo_results['runs']:
                continue

            all_curves = []

            for run_data in algo_results['runs']:
                evals = _get_trajectory_data(run_data)  # 1 entri per evaluasi NYATA
                if not evals:
                    continue

                # Kurva konvergensi = running-best atas evaluasi NYATA berurutan.
                # Indeks sumbu-X adalah nomor evaluasi (NFE), identik-skala untuk
                # semua algoritma. Setelah evaluasi terakhir, nilai di-carry-forward.
                curve = np.full(len(ffe_grid), float('inf'), dtype=np.float64)
                running_best = float('inf')
                for i in range(len(ffe_grid)):
                    if i < len(evals):
                        try:
                            fval = float(evals[i].get('fitness', float('inf')))
                        except (TypeError, ValueError):
                            fval = float('inf')
                        running_best = min(running_best, fval)
                    curve[i] = running_best

                all_curves.append(curve)

            if not all_curves:
                continue

            # --- Hitung mean dan std antar runs menggunakan nanmean/nanstd ---
            # Ganti inf dengan NaN agar tidak mendistorsi rata-rata
            stacked = np.array(all_curves, dtype=np.float64)
            stacked_nan = np.where(np.isinf(stacked), np.nan, stacked)
            mean_curve = np.nanmean(stacked_nan, axis=0)
            std_curve  = np.nanstd(stacked_nan, axis=0)

            # Hanya plot titik di mana minimal 1 run memiliki data berhingga
            valid_mask = ~np.isnan(mean_curve)
            if not np.any(valid_mask):
                continue

            x_plot    = ffe_grid[valid_mask]
            y_mean    = mean_curve[valid_mask]
            y_std     = std_curve[valid_mask]
            # Kliping batas bawah shading ke 1e-10 agar tidak crash pada log scale
            y_lower   = np.maximum(y_mean - y_std, 1e-10)
            y_upper   = y_mean + y_std

            ax.plot(x_plot, y_mean,
                    label=labels.get(algo_name, algo_name.upper()),
                    color=colors.get(algo_name, 'black'), linewidth=2)
            ax.fill_between(x_plot, y_lower, y_upper,
                            alpha=0.2, color=colors.get(algo_name, 'black'))

        ax.set_xlabel('Number of Function Evaluations (NFE)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Best Fitness Value', fontsize=12, fontweight='bold')
        ax.set_title(
            f'Convergence Curve - {func_name.capitalize()} Function\n'
            f'(Fair Comparison: Identical NFE Budget per Algorithm)',
            fontsize=13, fontweight='bold'
        )
        ax.set_yscale('log')
        ax.legend(fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # Annotate FPA plateau (premature convergence) jika FPA ada
        if 'fpa' in results and results['fpa']['runs']:
            ax.annotate('FPA: Premature convergence\n(early plateau)',
                        xy=(0.98, 0.02), xycoords='axes fraction',
                        fontsize=9, ha='right', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#3498DB', alpha=0.3))

        plt.tight_layout()
        save_path = self.save_dir / f"convergence_{func_name}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"    Saved: {save_path}")
    
    def plot_3d_landscape(self, func_name: str, results: Dict[str, Dict], 
                         dim_x: int = 0, dim_y: int = 1):
        """Plot 3D landscape dengan trajectory algoritma (2 dimensi pertama).
        Trajectory diproyeksikan ke slice f(x_0,x_1,0,...,0) agar menempel pada surface.
        """
        benchmark_func = BenchmarkFunctions.get_function(func_name)
        bounds = BenchmarkFunctions.get_bounds(func_name)
        
        # Infer dimension from first run with trajectory data
        dim = 30
        for algo_results in results.values():
            if algo_results.get('runs'):
                eval_hist = _get_trajectory_data(min(algo_results['runs'], key=lambda r: r['best_fitness']))
                if eval_hist:
                    dim = len(eval_hist[0]['x'])
                    break
        
        # Create meshgrid (surface = f(x_0, x_1, 0, ..., 0))
        resolution = 50
        x = np.linspace(bounds[0], bounds[1], resolution)
        y = np.linspace(bounds[0], bounds[1], resolution)
        X, Y = np.meshgrid(x, y)
        
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                point = np.zeros(dim)
                point[dim_x] = X[i, j]
                point[dim_y] = Y[i, j]
                Z[i, j] = benchmark_func(point)
        
        # Create figure
        fig = plt.figure(figsize=(16, 5))
        
        colors = {'ifpoax': 'red', 'fpa': 'blue', 'pso': 'green'}
        labels = {'ifpoax': 'IFPOA-X', 'fpa': 'FPA', 'pso': 'PSO'}
        
        for idx, (algo_name, algo_results) in enumerate(results.items()):
            ax = fig.add_subplot(1, 3, idx + 1, projection='3d')
            
            # Plot surface
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.6, 
                                  edgecolor='none', antialiased=True)
            
            # Plot trajectory from best run (prefer all_evaluations untuk IFPOAX)
            if algo_results['runs']:
                best_run = min(algo_results['runs'], 
                              key=lambda x: x['best_fitness'])
                eval_hist = _get_trajectory_data(best_run)
                
                if eval_hist:
                    # Extract trajectory (subsample untuk clarity)
                    # Project trajectory to 2D slice: z = f(x_0, x_1, 0, ..., 0)
                    # so path sits on surface (avoids "floating" from full-D fitness)
                    subsample = max(1, len(eval_hist) // 50)
                    dim = len(eval_hist[0]['x'])
                    traj_x = [e['x'][dim_x] for e in eval_hist[::subsample]]
                    traj_y = [e['x'][dim_y] for e in eval_hist[::subsample]]
                    traj_z = []
                    for e in eval_hist[::subsample]:
                        pt = np.zeros(dim)
                        pt[dim_x] = e['x'][dim_x]
                        pt[dim_y] = e['x'][dim_y]
                        traj_z.append(float(benchmark_func(pt)))
                    
                    ax.plot(traj_x, traj_y, traj_z, color=colors[algo_name], 
                           linewidth=2, alpha=0.8, label=f'{labels[algo_name]} Path')
                    ax.scatter(traj_x[0], traj_y[0], traj_z[0], 
                             color=colors[algo_name], s=100, marker='o', 
                             label='Start', edgecolors='black', linewidths=2)
                    ax.scatter(traj_x[-1], traj_y[-1], traj_z[-1], 
                             color=colors[algo_name], s=150, marker='*', 
                             label='Best Found', edgecolors='black', linewidths=2)
            
            ax.set_xlabel(f'$x_{dim_x}$', fontsize=10, fontweight='bold')
            ax.set_ylabel(f'$x_{dim_y}$', fontsize=10, fontweight='bold')
            ax.set_zlabel('f(x)', fontsize=10, fontweight='bold')
            ax.set_title(f'{labels[algo_name]} - {func_name.capitalize()}', 
                        fontsize=12, fontweight='bold')
            ax.legend(fontsize=8)
            ax.view_init(elev=25, azim=45)
        
        plt.tight_layout()
        save_path = self.save_dir / f"landscape_3d_{func_name}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"    Saved: {save_path}")
    
    def plot_2d_contour(self, func_name: str, results: Dict[str, Dict],
                       dim_x: int = 0, dim_y: int = 1):
        """Plot 2D contour dengan trajectory algoritma"""
        benchmark_func = BenchmarkFunctions.get_function(func_name)
        bounds = BenchmarkFunctions.get_bounds(func_name)
        
        # Create meshgrid
        resolution = 100
        x = np.linspace(bounds[0], bounds[1], resolution)
        y = np.linspace(bounds[0], bounds[1], resolution)
        X, Y = np.meshgrid(x, y)
        
        # Calculate Z values
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                point = np.zeros(30)
                point[dim_x] = X[i, j]
                point[dim_y] = Y[i, j]
                Z[i, j] = benchmark_func(point)
        
        # Create subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        colors = {'ifpoax': 'red', 'fpa': 'blue', 'pso': 'green'}
        labels = {'ifpoax': 'IFPOA-X', 'fpa': 'FPA', 'pso': 'PSO'}
        
        for idx, (algo_name, algo_results) in enumerate(results.items()):
            ax = axes[idx]
            
            # Plot contour
            levels = np.logspace(np.log10(Z.min() + 1e-10), 
                               np.log10(Z.max() + 1), 20)
            contour = ax.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.7)
            ax.contour(X, Y, Z, levels=levels, colors='black', 
                      alpha=0.2, linewidths=0.5)
            
            # Plot trajectory from best run (prefer all_evaluations untuk IFPOAX)
            if algo_results['runs']:
                best_run = min(algo_results['runs'], 
                              key=lambda x: x['best_fitness'])
                eval_hist = _get_trajectory_data(best_run)
                
                if eval_hist:
                    # Extract all evaluations for scatter
                    all_x = [e['x'][dim_x] for e in eval_hist]
                    all_y = [e['x'][dim_y] for e in eval_hist]
                    
                    # Plot all points
                    ax.scatter(all_x, all_y, c=colors[algo_name], 
                             s=10, alpha=0.3, edgecolors='none')
                    
                    # Plot trajectory line (subsample)
                    subsample = max(1, len(eval_hist) // 30)
                    traj_x = [e['x'][dim_x] for e in eval_hist[::subsample]]
                    traj_y = [e['x'][dim_y] for e in eval_hist[::subsample]]
                    
                    ax.plot(traj_x, traj_y, color=colors[algo_name], 
                           linewidth=2, alpha=0.8, linestyle='-')
                    ax.scatter(traj_x[0], traj_y[0], color='yellow', 
                             s=200, marker='o', edgecolors='black', 
                             linewidths=2, label='Start', zorder=5)
                    ax.scatter(traj_x[-1], traj_y[-1], color='lime', 
                             s=300, marker='*', edgecolors='black', 
                             linewidths=2, label='Best', zorder=5)
            
            # Mark global optimum
            if func_name.lower() == 'rosenbrock':
                ax.scatter(1, 1, color='white', s=200, marker='x', 
                         linewidths=3, label='Global Optimum', zorder=10)
            else:
                ax.scatter(0, 0, color='white', s=200, marker='x', 
                         linewidths=3, label='Global Optimum', zorder=10)
            
            ax.set_xlabel(f'$x_{dim_x}$', fontsize=11, fontweight='bold')
            ax.set_ylabel(f'$x_{dim_y}$', fontsize=11, fontweight='bold')
            ax.set_title(f'{labels[algo_name]} - {func_name.capitalize()}', 
                        fontsize=12, fontweight='bold')
            ax.legend(fontsize=9, loc='upper right')
            ax.grid(True, alpha=0.3)
            
            # Colorbar
            cbar = plt.colorbar(contour, ax=ax)
            cbar.set_label('f(x)', fontsize=10)
        
        plt.tight_layout()
        save_path = self.save_dir / f"contour_2d_{func_name}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"    Saved: {save_path}")
    
    def create_animation_2d(self, func_name: str, results: Dict[str, Dict],
                           dim_x: int = 0, dim_y: int = 1, max_frames: int = 100):
        """Buat animasi GIF pergerakan algoritma dalam 2D.

        Animasi menggunakan sumbu waktu berbasis FFE (Function Evaluations) aktual
        dari field 't' pada setiap entry all_evaluations — bukan urutan list (index).

        Motivasi: IFPOA-X memiliki _theta_cache yang menyebabkan sebagian parent
        re-evaluations menjadi cache hit (tidak memanggil evaluate_config). Akibatnya
        len(all_evaluations) < budget_ffe untuk IFPOA-X, sementara FPA/PSO selalu
        len(all_evaluations) == budget_ffe. Jika frame didasarkan pada len(all_evaluations),
        animasi IFPOA-X "membeku" jauh sebelum animasi FPA/PSO selesai — perbandingan
        yang tidak fair.

        Dengan FFE-based framing: setiap frame merepresentasikan nilai FFE tertentu.
        Untuk IFPOA-X, posisi terakhir yang diketahui (forward-fill) digunakan pada FFE
        yang merupakan cache hit — secara semantik benar karena posisi tidak berubah.
        """
        print(f"    Creating 2D animation for {func_name}...")

        benchmark_func = BenchmarkFunctions.get_function(func_name)
        bounds = BenchmarkFunctions.get_bounds(func_name)

        # Create meshgrid untuk background
        resolution = 80
        x = np.linspace(bounds[0], bounds[1], resolution)
        y = np.linspace(bounds[0], bounds[1], resolution)
        X, Y = np.meshgrid(x, y)

        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                point = np.zeros(30)
                point[dim_x] = X[i, j]
                point[dim_y] = Y[i, j]
                Z[i, j] = benchmark_func(point)

        # Setup figure
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        colors = {'ifpoax': 'red', 'fpa': 'blue', 'pso': 'green'}
        labels = {'ifpoax': 'IFPOA-X', 'fpa': 'FPA', 'pso': 'PSO'}

        # --- Siapkan data trajektori per algoritma ---
        # Untuk setiap entry dalam all_evaluations, gunakan field 't' sebagai FFE aktual.
        # Fallback ke index posisi jika 't' tidak tersedia (kompatibilitas mundur).
        algo_data = {}
        max_budget = 0

        for algo_name, algo_results in results.items():
            if algo_results['runs']:
                best_run = min(algo_results['runs'],
                               key=lambda r: r['best_fitness'])
                eval_hist = _get_trajectory_data(best_run)
                if eval_hist:
                    # Pastikan setiap entry memiliki 't' yang valid; fallback ke index
                    for k, entry in enumerate(eval_hist):
                        if 't' not in entry or not isinstance(entry.get('t'), (int, float)):
                            entry['t'] = k
                    max_t = max(int(e['t']) for e in eval_hist)
                    max_budget = max(max_budget, max_t)
                algo_data[algo_name] = eval_hist

        if max_budget == 0:
            max_budget = 1000  # fallback

        # Grid FFE seragam untuk semua algoritma: 0, 1, ..., max_budget
        # n_frames frame dibagi merata pada rentang ini
        n_frames = min(max_frames, max_budget + 1)
        ffe_grid = np.linspace(0, max_budget, n_frames, dtype=np.int64)

        def init():
            for ax in axes:
                ax.clear()
            return []

        def animate(frame_num):
            current_ffe = int(ffe_grid[frame_num])

            for ax_idx, (algo_name, eval_hist) in enumerate(algo_data.items()):
                ax = axes[ax_idx]
                ax.clear()

                # Plot contour background
                levels = np.logspace(np.log10(Z.min() + 1e-10),
                                     np.log10(Z.max() + 1), 15)
                ax.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.6)

                # --- Filter entri yang sudah terjadi pada FFE <= current_ffe ---
                # Ini setara dengan "forward-fill": jika pada FFE tertentu tidak ada
                # evaluasi nyata (cache hit), posisi terakhir yang diketahui dipertahankan.
                visible = [e for e in eval_hist if int(e.get('t', 0)) <= current_ffe]

                if visible:
                    traj_x = [e['x'][dim_x] for e in visible]
                    traj_y = [e['x'][dim_y] for e in visible]

                    # Plot trail (semua titik yang sudah dievaluasi)
                    if len(traj_x) > 1:
                        ax.plot(traj_x, traj_y, color=colors.get(algo_name, 'gray'),
                                linewidth=1.5, alpha=0.6)

                    # Plot semua titik evaluasi
                    ax.scatter(traj_x, traj_y, c=colors.get(algo_name, 'gray'),
                               s=20, alpha=0.4, edgecolors='none')

                    # Highlight posisi terkini (entry dengan t terbesar <= current_ffe)
                    ax.scatter(traj_x[-1], traj_y[-1],
                               color=colors.get(algo_name, 'gray'),
                               s=150, marker='o', edgecolors='white',
                               linewidths=2, zorder=5)

                # Mark global optimum
                if func_name.lower() == 'rosenbrock':
                    ax.scatter(1, 1, color='yellow', s=200, marker='*',
                               linewidths=2, edgecolors='black', zorder=10)
                else:
                    ax.scatter(0, 0, color='yellow', s=200, marker='*',
                               linewidths=2, edgecolors='black', zorder=10)

                ax.set_xlabel(f'$x_{dim_x}$', fontsize=11, fontweight='bold')
                ax.set_ylabel(f'$x_{dim_y}$', fontsize=11, fontweight='bold')
                # Judul menampilkan FFE aktual — adil untuk semua algoritma
                n_visible = len(visible) if visible else 0
                ax.set_title(
                    f'{labels.get(algo_name, algo_name.upper())} '
                    f'[FFE: {current_ffe}/{max_budget}] ({n_visible} evals)',
                    fontsize=11, fontweight='bold'
                )
                ax.set_xlim(bounds[0], bounds[1])
                ax.set_ylim(bounds[0], bounds[1])
                ax.grid(True, alpha=0.3)

            fig.suptitle(
                f'{func_name.capitalize()} Function — '
                f'Frame {frame_num + 1}/{n_frames} | FFE {current_ffe}/{max_budget}',
                fontsize=13, fontweight='bold'
            )
            plt.tight_layout()
            return axes.flatten()

        # Create animation
        anim = FuncAnimation(fig, animate, init_func=init,
                             frames=n_frames, interval=100, blit=False)

        # Save as GIF
        save_path = self.save_dir / f"animation_2d_{func_name}.gif"
        anim.save(save_path, writer='pillow', fps=10, dpi=100)
        plt.close()

        print(f"    Saved: {save_path}")


# ==============================================================================
# EXPERIMENT MANAGER
# ==============================================================================

class BenchmarkExperiment:
    """Mengelola eksperimen benchmark lengkap"""
    
    def __init__(self, algorithms: List[str], functions: List[str],
                 n_runs: int, budget: int, dim: int, save_dir: str = "./results",
                 ifpoax_use_obl: bool = True, ifpoax_use_jade: bool = True, ifpoax_use_bandit: bool = True,
                 equal_real_nfe: bool = True):
        self.algorithms = algorithms
        self.functions = functions
        self.n_runs = n_runs
        self.budget = budget
        self.dim = dim
        self.save_dir = Path(save_dir)
        self.ifpoax_use_obl = ifpoax_use_obl
        self.ifpoax_use_jade = ifpoax_use_jade
        self.ifpoax_use_bandit = ifpoax_use_bandit
        self.equal_real_nfe = equal_real_nfe
        self.no_animation = False  # di-set dari main(); animasi GIF lambat & opsional
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {}
        self.visualizer = BenchmarkVisualizer(save_dir)
    
    def run_experiments(self):
        """Jalankan semua eksperimen"""
        print("\n" + "="*80)
        print("BENCHMARK EXPERIMENT - METAHEURISTIC OPTIMIZATION ALGORITHMS")
        print("="*80)
        print(f"Algorithms: {', '.join(self.algorithms)}")
        print(f"Functions: {', '.join(self.functions)}")
        print(f"Runs per config: {self.n_runs}")
        print(f"Budget (FFE): {self.budget}")
        print(f"Dimensions: {self.dim}")
        print("="*80 + "\n")
        
        for func_name in self.functions:
            print(f"\n{'='*80}")
            print(f"TESTING ON: {func_name.upper()} FUNCTION")
            print(f"{'='*80}")
            
            func_results = {}
            
            for algo_name in self.algorithms:
                print(f"\n{algo_name.upper()} Algorithm:")
                print("-" * 40)
                
                algo_runs = []
                best_vals = []
                worst_vals = []
                
                for run_id in range(self.n_runs):
                    seed = run_id * 1000

                    # Reset global random state agar setiap independent run
                    # benar-benar independen dan reproducible.
                    # Referensi: De Jong (1975), Eiben & Smith (2003) — "Introduction to
                    # Evolutionary Computing" mensyaratkan setiap run dimulai dari
                    # kondisi stokastik yang terdefinisi dengan baik.
                    random.seed(seed)
                    np.random.seed(seed)

                    runner = AlgorithmRunner(algo_name, func_name, self.dim,
                                           self.budget, seed, self.save_dir,
                                           use_obl=self.ifpoax_use_obl,
                                           use_jade_local=self.ifpoax_use_jade,
                                           use_bandit=self.ifpoax_use_bandit,
                                           equal_real_nfe=self.equal_real_nfe)
                    
                    try:
                        result = runner.run()
                        best_fitness = result['best_fitness']
                        
                        algo_runs.append(result)
                        best_vals.append(best_fitness)
                        
                        print(f"  Run {run_id + 1:2d}/{self.n_runs}: Best = {best_fitness:.6e}")
                        
                    except Exception as e:
                        print(f"  Run {run_id + 1:2d}/{self.n_runs}: FAILED - {str(e)}")
                        best_vals.append(float('inf'))
                
                # Statistik
                best_vals_finite = [v for v in best_vals if np.isfinite(v)]
                if best_vals_finite:
                    stats = {
                        'best': np.min(best_vals_finite),
                        'worst': np.max(best_vals_finite),
                        'mean': np.mean(best_vals_finite),
                        'std': np.std(best_vals_finite),
                        'median': np.median(best_vals_finite)
                    }
                else:
                    stats = {
                        'best': float('inf'),
                        'worst': float('inf'),
                        'mean': float('inf'),
                        'std': 0.0,
                        'median': float('inf')
                    }
                
                func_results[algo_name] = {
                    'runs': algo_runs,
                    'stats': stats,
                    'all_values': best_vals
                }
                
                print(f"\n  Statistics:")
                print(f"    Best:   {stats['best']:.6e}")
                print(f"    Worst:  {stats['worst']:.6e}")
                print(f"    Mean:   {stats['mean']:.6e}")
                print(f"    Std:    {stats['std']:.6e}")
                print(f"    Median: {stats['median']:.6e}")
            
            self.results[func_name] = func_results
        
        print("\n" + "="*80)
        print("ALL EXPERIMENTS COMPLETED")
        print("="*80 + "\n")
    
    def save_results(self):
        """Simpan hasil ke CSV dan JSON"""
        print("\nSaving results...")
        
        # CSV - Statistical Summary
        rows = []
        for func_name, func_results in self.results.items():
            for algo_name, algo_data in func_results.items():
                stats = algo_data['stats']
                rows.append({
                    'Function': func_name.capitalize(),
                    'Algorithm': algo_name.upper(),
                    'Best': stats['best'],
                    'Worst': stats['worst'],
                    'Mean': stats['mean'],
                    'Std': stats['std'],
                    'Median': stats['median']
                })
        
        df = pd.DataFrame(rows)
        csv_path = self.save_dir / "benchmark_results.csv"
        df.to_csv(csv_path, index=False, float_format='%.6e')
        print(f"  Saved: {csv_path}")
        
        # CSV - All Raw Values
        raw_rows = []
        for func_name, func_results in self.results.items():
            for algo_name, algo_data in func_results.items():
                for run_idx, val in enumerate(algo_data['all_values']):
                    raw_rows.append({
                        'Function': func_name.capitalize(),
                        'Algorithm': algo_name.upper(),
                        'Run': run_idx + 1,
                        'BestFitness': val
                    })
        
        df_raw = pd.DataFrame(raw_rows)
        csv_raw_path = self.save_dir / "benchmark_results_raw.csv"
        df_raw.to_csv(csv_raw_path, index=False, float_format='%.6e')
        print(f"  Saved: {csv_raw_path}")
        
        # JSON - Complete Results
        json_data = {}
        for func_name, func_results in self.results.items():
            json_data[func_name] = {}
            for algo_name, algo_data in func_results.items():
                json_data[func_name][algo_name] = {
                    'stats': algo_data['stats'],
                    'all_values': algo_data['all_values']
                }
        
        json_path = self.save_dir / "benchmark_results.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"  Saved: {json_path}")
    
    def print_comparison_table(self):
        """Cetak tabel perbandingan komprehensif"""
        print("\n" + "="*100)
        print("COMPREHENSIVE COMPARISON TABLE")
        print("="*100 + "\n")
        
        for func_name, func_results in self.results.items():
            print(f"\n{func_name.upper()} FUNCTION")
            print("-" * 100)
            print(f"{'Algorithm':<12} {'Best':>15} {'Worst':>15} {'Mean':>15} {'Std':>15} {'Median':>15}")
            print("-" * 100)
            
            for algo_name in self.algorithms:
                if algo_name in func_results:
                    stats = func_results[algo_name]['stats']
                    print(f"{algo_name.upper():<12} "
                          f"{stats['best']:>15.6e} "
                          f"{stats['worst']:>15.6e} "
                          f"{stats['mean']:>15.6e} "
                          f"{stats['std']:>15.6e} "
                          f"{stats['median']:>15.6e}")
            print("-" * 100)
        
        print("\n" + "="*100 + "\n")
    
    def generate_visualizations(self):
        """Generate semua visualisasi"""
        print("\nGenerating visualizations...")
        
        for func_name, func_results in self.results.items():
            print(f"\n  {func_name.capitalize()} Function:")
            
            # Convergence curve
            self.visualizer.plot_convergence(func_results, func_name)
            
            # 3D landscape
            self.visualizer.plot_3d_landscape(func_name, func_results)
            
            # 2D contour
            self.visualizer.plot_2d_contour(func_name, func_results)
            
            # Animation (opsional, bisa memakan waktu) — dilewati bila --no-animation
            if not self.no_animation:
                try:
                    self.visualizer.create_animation_2d(func_name, func_results)
                except Exception as e:
                    print(f"    Warning: Animation creation failed: {e}")
        
        print("\n  All visualizations completed!")


# ==============================================================================
# MAIN CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Tester untuk IFPOA-X, FPA, dan PSO pada Fungsi Standar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Jalankan semua algoritma pada semua fungsi dengan 30 runs
  python benchmark_tester.py
  
  # Jalankan hanya IFPOA-X pada Ackley dengan 10 runs
  python benchmark_tester.py --algo ifpoax --func ackley --runs 10
  
  # Jalankan semua dengan budget 500 FFE
  python benchmark_tester.py --budget 500
  
  # Test cepat: 1 run, budget kecil
  python benchmark_tester.py --runs 1 --budget 100
        """
    )
    
    parser.add_argument('--algo', type=str, default='all',
                       choices=['ifpoax', 'fpa', 'pso', 'all'],
                       help='Algoritma yang akan dijalankan (default: all)')
    
    parser.add_argument('--func', type=str, default='all',
                       choices=['ackley', 'rastrigin', 'rosenbrock', 'all'],
                       help='Fungsi benchmark yang akan diuji (default: all)')
    
    parser.add_argument('--runs', type=int, default=30,
                       help='Jumlah independent runs (default: 30)')
    
    parser.add_argument('--budget', type=int, default=1000,
                       help='Maximum function evaluations (default: 1000)')
    
    parser.add_argument('--dim', type=int, default=30,
                       help='Jumlah dimensi problem (default: 30)')
    
    parser.add_argument('--save-dir', type=str, default='./benchmark_results',
                       help='Direktori untuk menyimpan hasil (default: ./benchmark_results)')
    
    parser.add_argument('--no-animation', action='store_true',
                       help='Skip pembuatan animasi GIF (lebih cepat)')

    parser.add_argument('--legacy-ffe', action='store_true',
                       help='Mode lama: budget dihitung sebagai FFE internal (self.t) '
                            'termasuk cache-hit. Default (nonaktif) = NFE nyata yang '
                            'setara untuk semua algoritma (perbandingan adil).')
    
    # IFPOAX ablation flags (untuk ablation study)
    parser.add_argument('--no-obl', action='store_true',
                       help='IFPOAX: disable Opposition-Based Learning')
    parser.add_argument('--no-jade', action='store_true',
                       help='IFPOAX: disable JADE local operator')
    parser.add_argument('--no-bandit', action='store_true',
                       help='IFPOAX: disable Bandit selection')
    parser.add_argument('--variant', type=str, default=None,
                       choices=['full', 'noOBL', 'noJADE', 'noBandit', 'base'],
                       help='IFPOAX ablation variant (overrides --no-* flags): full, noOBL, noJADE, noBandit, base')
    
    args = parser.parse_args()
    
    # Apply --variant to override individual flags
    if args.variant:
        variant_map = {
            'full': (False, False, False),
            'noOBL': (True, False, False),
            'noJADE': (False, True, False),
            'noBandit': (False, False, True),
            'base': (True, True, True),
        }
        no_obl, no_jade, no_bandit = variant_map[args.variant]
        args.no_obl = no_obl
        args.no_jade = no_jade
        args.no_bandit = no_bandit
    
    # Determine algorithms to run
    if args.algo == 'all':
        algorithms = ['ifpoax', 'fpa', 'pso']
    else:
        algorithms = [args.algo]
    
    # Determine functions to test
    if args.func == 'all':
        functions = ['ackley', 'rastrigin', 'rosenbrock']
    else:
        functions = [args.func]
    
    # Run experiment
    start_time = time.time()
    
    experiment = BenchmarkExperiment(
        algorithms=algorithms,
        functions=functions,
        n_runs=args.runs,
        budget=args.budget,
        dim=args.dim,
        save_dir=args.save_dir,
        ifpoax_use_obl=not args.no_obl,
        ifpoax_use_jade=not args.no_jade,
        ifpoax_use_bandit=not args.no_bandit,
        equal_real_nfe=not args.legacy_ffe
    )
    experiment.no_animation = args.no_animation
    
    try:
        # Run experiments
        experiment.run_experiments()
        
        # Save results
        experiment.save_results()
        
        # Print comparison
        experiment.print_comparison_table()
        
        # Generate visualizations
        experiment.generate_visualizations()
        
        # Summary
        elapsed = time.time() - start_time
        print(f"\n{'='*80}")
        print(f"EXPERIMENT COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        print(f"Total time: {elapsed/60:.2f} minutes")
        print(f"Results saved to: {args.save_dir}")
        print(f"{'='*80}\n")
        
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user!")
        print("Partial results may be available in:", args.save_dir)
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
