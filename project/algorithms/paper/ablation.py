#!/usr/bin/env python3
"""
Ablation study PAPER 1 — kontribusi komponen IFPOA-X (OBL, JADE, Bandit).
==========================================================================
Menjalankan varian noOBL/noJADE/noBandit/base (via flag use_obl/use_jade_local/
use_bandit yang SUDAH ada di ifpoax.py/benchmark_tester.py — tidak mengubah
algoritma) pada subset fungsi representatif, equal-NFE, dimensi D=30.
Varian "full" DIPAKAI ULANG dari results/raw_D30.csv (studi utama) alih-alih
dijalankan lagi, untuk menghemat komputasi.

Subset fungsi (F1,F5,F8,F9,F10,F13) dipilih agar mencakup: unimodal mudah
(F1), unimodal berlembah (F5, Rosenbrock), pengecualian IFPOA-X (F8), dan
multimodal (F9,F10,F13) — selaras dengan klaim di §5.1-5.3.

Contoh:
  python ablation.py --runs 5
"""
import sys, io, time, contextlib, argparse
from pathlib import Path
import pandas as pd

_HERE = Path(__file__).resolve().parent
_ALGO_DIR = _HERE.parent
_PROJECT_ROOT = _ALGO_DIR.parent.parent
for p in (str(_ALGO_DIR), str(_PROJECT_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import benchmark_tester as bt
import functions as F

F.register_all(bt)

VARIANTS = {
    "IFPOA-X (full)":      dict(use_obl=True,  use_jade_local=True,  use_bandit=True),
    "IFPOA-X (no OBL)":    dict(use_obl=False, use_jade_local=True,  use_bandit=True),
    "IFPOA-X (no JADE)":   dict(use_obl=True,  use_jade_local=False, use_bandit=True),
    "IFPOA-X (no Bandit)": dict(use_obl=True,  use_jade_local=True,  use_bandit=False),
    "IFPOA-X (base/FPA)":  dict(use_obl=False, use_jade_local=False, use_bandit=False),
}
FUNCS_DEFAULT = [f"F{i}" for i in range(1, 14)]   # semua F1-F13


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def run_one(flags, func, dim, budget, seed, tmp_dir):
    r = bt.AlgorithmRunner("ifpoax", func, dim, budget, seed, save_dir=tmp_dir,
                            equal_real_nfe=True, **flags)
    with _quiet():
        out = r.run()
    return float(out["best_fitness"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dim", type=int, default=30)
    ap.add_argument("--budget", type=int, default=500)
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--funcs", type=str, nargs="+", default=FUNCS_DEFAULT)
    ap.add_argument("--out", type=str, default=str(_HERE / "results" / "ablation_D30.csv"))
    ap.add_argument("--reuse-full", type=str, default=str(_HERE / "results" / "raw_D30.csv"))
    args = ap.parse_args()

    FUNCS = args.funcs
    tmp_dir = str(_HERE / "results" / "_tmp")
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)
    rows = []

    reuse_path = Path(args.reuse_full)
    if reuse_path.exists():
        df_full = pd.read_csv(reuse_path)
        df_full = df_full[(df_full["Algorithm"] == "IFPOA-X") & (df_full["Function"].isin(FUNCS))]
        for _, row in df_full.iterrows():
            rows.append({"Function": row["Function"], "Variant": "IFPOA-X (full)",
                         "Run": int(row["Run"]), "Best": float(row["Best"])})
        print(f"Reused {len(df_full)} 'full' rows from {reuse_path}", flush=True)

    variants_to_run = {k: v for k, v in VARIANTS.items() if k != "IFPOA-X (full)"}
    t_start = time.time()
    total = len(FUNCS) * len(variants_to_run) * args.runs
    done = 0
    for func in FUNCS:
        for vname, flags in variants_to_run.items():
            for run_id in range(args.runs):
                seed = run_id * 1000
                t0 = time.time()
                best = run_one(flags, func, args.dim, args.budget, seed, tmp_dir)
                rows.append({"Function": func, "Variant": vname, "Run": run_id + 1, "Best": best})
                done += 1
                print(f"[{done}/{total}] {func} {vname} run{run_id + 1}: best={best:.4e} "
                      f"({time.time() - t0:.1f}s, elapsed {time.time() - t_start:.0f}s)", flush=True)

    df = pd.DataFrame(rows)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, float_format="%.6e")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
