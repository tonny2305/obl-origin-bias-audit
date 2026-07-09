#!/usr/bin/env python3
"""
Suite fungsi benchmark klasik F1-F13 (Yao, Liu & Lin, 1999) untuk PAPER 1.
=========================================================================
Set fungsi *scalable* standar yang lazim dipakai pada literatur metaheuristik:
- Unimodal      : F1-F7  (uji presisi eksploitasi / konvergensi)
- Multimodal    : F8-F13 (uji eksplorasi / lolos dari optimum lokal)

Semua fungsi didefinisikan sebagai minimisasi dengan minimum global f(x*) = 0
(F8 di-offset +418.9829*D agar konsisten bernilai 0 di optimum). Fungsi
didaftarkan ke harness benchmark_tester via register_all() sehingga IFPOA-X,
FPA, dan PSO dapat mengujinya TANPA modifikasi algoritma.

Referensi: Yao, X., Liu, Y., & Lin, G. (1999). Evolutionary programming made
faster. IEEE Trans. Evol. Comput., 3(2), 82-102.
"""
import numpy as np


# ----------------------------- Unimodal F1-F7 -----------------------------
def f1_sphere(x):
    x = np.asarray(x, float)
    return float(np.sum(x ** 2))


def f2_schwefel222(x):
    x = np.asarray(x, float)
    ax = np.abs(x)
    return float(np.sum(ax) + np.prod(ax))


def f3_schwefel12(x):
    x = np.asarray(x, float)
    return float(np.sum(np.cumsum(x) ** 2))


def f4_schwefel221(x):
    x = np.asarray(x, float)
    return float(np.max(np.abs(x)))


def f5_rosenbrock(x):
    x = np.asarray(x, float)
    return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (x[:-1] - 1.0) ** 2))


def f6_step(x):
    x = np.asarray(x, float)
    return float(np.sum(np.floor(x + 0.5) ** 2))


def f7_quartic(x):
    x = np.asarray(x, float)
    i = np.arange(1, x.size + 1)
    return float(np.sum(i * x ** 4) + np.random.uniform(0.0, 1.0))  # + noise (stokastik)


# ---------------------------- Multimodal F8-F13 ---------------------------
def f8_schwefel226(x):
    x = np.asarray(x, float)
    # di-offset agar minimum global = 0 (aslinya -418.9829*D)
    return float(418.9828872724338 * x.size - np.sum(x * np.sin(np.sqrt(np.abs(x)))))


def f9_rastrigin(x):
    x = np.asarray(x, float)
    return float(np.sum(x ** 2 - 10.0 * np.cos(2.0 * np.pi * x) + 10.0))


def f10_ackley(x):
    x = np.asarray(x, float)
    d = x.size
    s1 = np.sum(x ** 2)
    s2 = np.sum(np.cos(2.0 * np.pi * x))
    return float(-20.0 * np.exp(-0.2 * np.sqrt(s1 / d)) - np.exp(s2 / d) + 20.0 + np.e)


def f11_griewank(x):
    x = np.asarray(x, float)
    i = np.arange(1, x.size + 1)
    return float(np.sum(x ** 2) / 4000.0 - np.prod(np.cos(x / np.sqrt(i))) + 1.0)


def _u(x, a, k, m):
    return np.where(x > a, k * (x - a) ** m,
                    np.where(x < -a, k * (-x - a) ** m, 0.0))


def f12_penalized1(x):
    x = np.asarray(x, float)
    n = x.size
    y = 1.0 + (x + 1.0) / 4.0
    term = (np.pi / n) * (
        10.0 * np.sin(np.pi * y[0]) ** 2
        + np.sum((y[:-1] - 1.0) ** 2 * (1.0 + 10.0 * np.sin(np.pi * y[1:]) ** 2))
        + (y[-1] - 1.0) ** 2
    )
    return float(term + np.sum(_u(x, 10, 100, 4)))


def f13_penalized2(x):
    x = np.asarray(x, float)
    term = 0.1 * (
        np.sin(3.0 * np.pi * x[0]) ** 2
        + np.sum((x[:-1] - 1.0) ** 2 * (1.0 + np.sin(3.0 * np.pi * x[1:]) ** 2))
        + (x[-1] - 1.0) ** 2 * (1.0 + np.sin(2.0 * np.pi * x[-1]) ** 2)
    )
    return float(term + np.sum(_u(x, 5, 100, 4)))


# name -> (fungsi, (lo, hi), optimum x*, modality)
FUNCTIONS = {
    "F1":  (f1_sphere,      (-100.0, 100.0),  0.0,          "unimodal"),
    "F2":  (f2_schwefel222, (-10.0, 10.0),    0.0,          "unimodal"),
    "F3":  (f3_schwefel12,  (-100.0, 100.0),  0.0,          "unimodal"),
    "F4":  (f4_schwefel221, (-100.0, 100.0),  0.0,          "unimodal"),
    "F5":  (f5_rosenbrock,  (-30.0, 30.0),    1.0,          "unimodal"),
    "F6":  (f6_step,        (-100.0, 100.0),  0.0,          "unimodal"),
    "F7":  (f7_quartic,     (-1.28, 1.28),    0.0,          "unimodal(noise)"),
    "F8":  (f8_schwefel226, (-500.0, 500.0),  420.9687,     "multimodal"),
    "F9":  (f9_rastrigin,   (-5.12, 5.12),    0.0,          "multimodal"),
    "F10": (f10_ackley,     (-32.0, 32.0),    0.0,          "multimodal"),
    "F11": (f11_griewank,   (-600.0, 600.0),  0.0,          "multimodal"),
    "F12": (f12_penalized1, (-50.0, 50.0),   -1.0,          "multimodal"),
    "F13": (f13_penalized2, (-50.0, 50.0),    1.0,          "multimodal"),
}


def register_all(bt):
    """Daftarkan seluruh F1-F13 ke modul harness benchmark_tester (bt)."""
    for name, (fn, bounds, _xstar, _mod) in FUNCTIONS.items():
        bt.register_benchmark_function(name, fn, bounds)
    return list(FUNCTIONS.keys())


if __name__ == "__main__":
    # Self-check: f(x*) harus ~0 (F7 dilewati krn noise; toleransi longgar utk float)
    np.random.seed(0)
    D = 30
    for name, (fn, bounds, xstar, mod) in FUNCTIONS.items():
        xopt = np.full(D, xstar)
        val = fn(xopt)
        # F8 memakai konstanta offset Schwefel yang hanya presisi hingga ~1e-2
        tol = 1e-2 if name == "F8" else 1e-4
        ok = "noise" in mod or abs(val) < tol
        print(f"{name:4s} {mod:16s} f(x*)={val:+.3e}  {'OK' if ok else 'FAIL'}")
        assert ok, f"{name} minimum tidak nol: {val}"
    print("\nAll F1-F13 minima verified (kecuali F7 yang stokastik).")
