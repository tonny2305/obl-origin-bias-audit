#!/usr/bin/env python3
"""
Adapter suite CEC2017 (shifted + rotated) untuk PAPER 1 via opfunu.
===================================================================
Benchmark STANDAR ter-geser & ter-rotasi: optimum global sengaja digeser
(x_global jauh dari titik asal) dan lanskap dirotasi (non-separable). Ini
adalah kontrol origin-bias yang jauh lebih kuat & diterima komunitas daripada
shift buatan sendiri — data shift/rotasi berasal dari spesifikasi CEC2017 resmi
(via pustaka opfunu), bukan dipilih penulis.

Objektif dilaporkan sebagai ERROR-ke-optimum: h(x) = f(x) - f_global, sehingga
minimum global = 0 (praktik pelaporan CEC standar). Batas domain [-100,100]^D.

Algoritma IFPOA-X/FPA/PSO TIDAK dimodifikasi — hanya objektif yang diganti.
"""
import numpy as np
from opfunu.cec_based import cec2017

# Subset representatif lintas kategori CEC2017 (F2 dikecualikan — tidak stabil):
#   unimodal (F1,F3), simple multimodal (F4-F10), hybrid (F11,F14), komposisi (F21,F23)
_SUBSET = ["F1", "F3", "F4", "F5", "F7", "F9", "F10", "F11", "F14", "F21"]
_DIM = 30

_OBJ = {}          # name -> opfunu object (ndim=_DIM)
FUNCTIONS = {}     # name -> (fn_error, (lo,hi), x_global, "cec2017")


def _make(name):
    cls = getattr(cec2017, f"{name}2017")
    obj = cls(ndim=_DIM)
    fg = float(obj.f_global)

    def fn(x, _obj=obj, _fg=fg):
        v = float(_obj.evaluate(np.asarray(x, dtype=float)))
        return max(0.0, v - _fg)          # error-ke-optimum, >= 0

    lo = float(obj.bounds[0][0]); hi = float(obj.bounds[0][1])
    return obj, fn, (lo, hi), np.asarray(obj.x_global, dtype=float)


for _n in _SUBSET:
    try:
        _o, _fn, _b, _xg = _make(_n)
        _OBJ[_n] = _o
        FUNCTIONS[_n] = (_fn, _b, _xg, "cec2017")
    except Exception as e:                # lewati fungsi yang gagal dibuat
        print(f"[functions_cec] SKIP {_n}: {type(e).__name__}: {e}")


def register_all(bt):
    """Daftarkan subset CEC2017 ke harness benchmark_tester (bt)."""
    for name, (fn, bounds, _xg, _m) in FUNCTIONS.items():
        bt.register_benchmark_function(name, fn, bounds)
    return list(FUNCTIONS.keys())


if __name__ == "__main__":
    # Self-check: h(x_global) ~= 0 dan h(random) > 0 utk tiap fungsi.
    rng = np.random.default_rng(0)
    print(f"{'Fn':4s} {'h(x*)':>12s} {'h(random)':>12s}  |x*|_mean  verdict")
    for name, (fn, (lo, hi), xg, _m) in FUNCTIONS.items():
        h_opt = fn(xg[:_DIM])
        h_rand = fn(rng.uniform(lo, hi, _DIM))
        offc = float(np.abs(xg[:_DIM]).mean())
        ok = (h_opt < 1e-2) and (h_rand > h_opt) and (offc > 1.0)
        print(f"{name:4s} {h_opt:12.3e} {h_rand:12.3e}  {offc:8.2f}  {'OK' if ok else 'FAIL'}")
    print(f"\n{len(FUNCTIONS)} CEC2017 functions ready (shifted+rotated, error-to-optimum).")
