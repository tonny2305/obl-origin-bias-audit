#!/usr/bin/env python3
"""
Suite benchmark F1-F13 versi TER-GESER (shifted) untuk PAPER 1.
================================================================
Menjawab objeksi *origin bias*: pada suite klasik F1-F13, mayoritas optimum
global berada di (atau dekat) pusat domain (titik asal). Opposition-Based
Learning (OBL) menghasilkan kandidat lawan dengan me-refleksikan titik melalui
PUSAT domain, sehingga OBL secara sistematis menyampel MENUJU optimum ketika
optimum berada di pusat — keuntungan yang bisa jadi artefak geometri suite,
bukan keunggulan umum algoritma.

Untuk menguji apakah keunggulan IFPOA-X bertahan tanpa bias ini, kita GESER
optimum tiap fungsi ke lokasi acak (deterministik, per-dimensi) yang jauh dari
pusat: g(x) = f(x - o), dengan o dipilih agar optimum baru berada di
t ∈ [0.30, 0.70]·hi per dimensi (jelas menjauh dari pusat 0, tetap di dalam
batas). Nilai optimum tetap f(x*) ≈ 0. Batas domain TIDAK diubah, sehingga
protokol equal-NFE & pembanding identik dengan studi utama.

Catatan: ini adalah kontrol *shift* (lokasi optimum). Rotasi (menguji
non-separabilitas) adalah perluasan lanjutan dan tidak diterapkan di sini.

Algoritma IFPOA-X/FPA/PSO TIDAK dimodifikasi — hanya fungsi objektif yang diganti.
"""
import numpy as np
from functions import FUNCTIONS as _BASE   # {name: (fn, (lo,hi), xstar, modality)}

_SHIFT_SEED = 20240707
_DIM_MAX = 64


def _target_and_shift(idx, bounds, xstar):
    """Optimum-target t (per-dim, off-center) & shift o=t-x* deterministik."""
    lo, hi = bounds
    rng = np.random.default_rng(_SHIFT_SEED + idx)
    # target optimum di [0.30,0.70]*hi (positif, jauh dari pusat 0)
    t = rng.uniform(0.30, 0.70, size=_DIM_MAX) * hi
    xs = np.full(_DIM_MAX, xstar, dtype=float)
    o = t - xs                              # g(x)=f(x-o) -> optimum di x=t
    return t, o


def _shifted(base_fn, o):
    def g(x):
        x = np.asarray(x, dtype=float)
        return base_fn(x - o[:x.size])
    return g


# name -> (fungsi_shifted, (lo,hi), target_optimum_vector, modality)
FUNCTIONS = {}
_SHIFTS = {}
for _i, (_name, (_fn, _bounds, _xstar, _mod)) in enumerate(_BASE.items()):
    _t, _o = _target_and_shift(_i, _bounds, _xstar)
    _SHIFTS[_name] = (_t, _o)
    FUNCTIONS[_name] = (_shifted(_fn, _o), _bounds, _t, _mod)


def make_functions(seed, lo_frac, hi_frac, signed):
    """Bangun dict fungsi shifted dengan konfigurasi shift berbeda (utk uji
    robustness lintas beberapa vektor pergeseran). Kembalikan {name: (g, bounds,
    t, mod)}. `signed=True` mengizinkan target di sisi negatif (arah beragam)."""
    out = {}
    for idx, (name, (fn, bounds, xstar, mod)) in enumerate(_BASE.items()):
        lo, hi = bounds
        rng = np.random.default_rng(seed + idx)
        mag = rng.uniform(lo_frac, hi_frac, size=_DIM_MAX) * hi
        if signed:
            mag *= rng.choice([-1.0, 1.0], size=_DIM_MAX)
        # jaga target di dalam batas dengan margin 2%
        t = np.clip(mag, lo * 0.98, hi * 0.98)
        o = t - np.full(_DIM_MAX, xstar, dtype=float)
        out[name] = (_shifted(fn, o), bounds, t, mod)
    return out


def register_all(bt):
    """Daftarkan seluruh F1-F13 SHIFTED ke harness benchmark_tester (bt)."""
    for name, (fn, bounds, _t, _mod) in FUNCTIONS.items():
        bt.register_benchmark_function(name, fn, bounds)
    return list(FUNCTIONS.keys())


if __name__ == "__main__":
    # Self-check: (1) g(target) ≈ 0 (optimum terjaga); (2) target di dalam batas
    # dan jauh dari pusat; (3) g(pusat) jelas > 0 (OBL center-reflection kini
    # TIDAK lagi mengarah ke optimum).
    D = 30
    for name, (fn, bounds, t, mod) in FUNCTIONS.items():
        lo, hi = bounds
        tD = t[:D]
        val_opt = fn(tD)
        val_center = fn(np.zeros(D))
        in_bounds = bool(np.all((tD >= lo) & (tD <= hi)))
        off_center = float(np.mean(np.abs(tD)) / hi)   # fraksi jarak dari pusat
        tol = 1e-2 if name == "F8" else 1e-4
        ok = ("noise" in mod or abs(val_opt) < tol) and in_bounds and off_center > 0.25
        print(f"{name:4s} {mod:16s} f(t)={val_opt:+.2e}  f(0)={val_center:+.2e}  "
              f"off_center={off_center:.2f}  in_bounds={in_bounds}  {'OK' if ok else 'FAIL'}")
        assert ok, f"{name}: shift invalid (f(t)={val_opt}, in_bounds={in_bounds}, off={off_center})"
    print("\nSemua F1-F13 SHIFTED valid: optimum terjaga, off-center, dalam batas.")
