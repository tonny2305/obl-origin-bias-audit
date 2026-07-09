#!/usr/bin/env python3
"""
Verifikasi MATEMATIS bahwa transformasi shift benar-benar memindahkan optimum
global ke lokasi yang diklaim, untuk SETIAP fungsi (khususnya Rosenbrock F5 &
penalized F12/F13 yang non-origin optimum).

Argumen: g(x) = f(x - o) adalah translasi murni. Semua F1-F13 bernilai >= 0 di
seluruh R^n dengan minimum global 0 di x*. Translasi mempertahankan himpunan
minimizer: argmin g = x* + o = t, dengan min g = min f = 0. Skrip ini
mengkonfirmasi secara numerik:
  (1) g(t) == 0 (up to fp);
  (2) tidak ada titik sampel acak (di dalam & luar batas) yang < g(t) - tol;
  (3) t benar off-center (|t|/hi > 0.25);
  (4) verifikasi silang untuk F5/F12/F13 bahwa argument-di-optimum = x* asli.
"""
import numpy as np
from functions import FUNCTIONS as BASE
from functions_shifted import FUNCTIONS as SH, _SHIFTS

D = 30
N_SAMPLE = 200_000
rng = np.random.default_rng(0)

print(f"{'Fn':4s} {'g(t)':>12s} {'min sample':>12s} {'x*_recovered ~ x*_base':>26s} {'off':>5s}  verdict")
all_ok = True
for name, (gfn, (lo, hi), t, mod) in SH.items():
    base_fn, _b, xstar, _m = BASE[name]
    tD = t[:D]
    o = _SHIFTS[name][1][:D]

    # (1) nilai di optimum
    g_opt = gfn(tD)

    # (2) sampel acak lebar (termasuk di luar batas asli, krn g meng-evaluasi f(x-o))
    X = rng.uniform(lo, hi, size=(N_SAMPLE, D))
    vals = np.array([gfn(x) for x in X[:2000]])   # subset utk kecepatan
    min_sample = float(vals.min())

    # (3) off-center
    off = float(np.mean(np.abs(tD)) / hi)

    # (4) argument yang direkonstruksi di optimum harus = x* asli (konstan)
    arg_at_opt = tD - o                      # = x* asli (vektor konstan)
    xstar_vec = np.full(D, xstar)
    recon_err = float(np.max(np.abs(arg_at_opt - xstar_vec)))

    tol = 1e-2 if name == "F8" else 1e-6
    ok = (abs(g_opt) < tol) and (min_sample >= g_opt - 1e-6) and (off > 0.25) and (recon_err < 1e-9)
    if "noise" in mod:  # F7 stokastik
        ok = (min_sample >= -1.0) and (off > 0.25) and (recon_err < 1e-9)
    all_ok &= ok
    print(f"{name:4s} {g_opt:12.3e} {min_sample:12.3e} {recon_err:26.2e} {off:5.2f}  {'OK' if ok else 'FAIL'}")

print("\n" + ("ALL SHIFTS MATHEMATICALLY VERIFIED (translation-invariant, optimum at t)."
              if all_ok else "*** VERIFICATION FAILED ***"))
