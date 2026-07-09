#!/usr/bin/env python3
"""
Analisis hasil ablation.py -> results/analysis_ablation/ (tabel + Figure 4).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = Path(__file__).resolve().parent
FULL = "IFPOA-X (full)"
ORDER = [FULL, "IFPOA-X (no OBL)", "IFPOA-X (no JADE)", "IFPOA-X (no Bandit)", "IFPOA-X (base/FPA)"]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default=str(_HERE / "results" / "ablation_full_D30.csv"))
    ap.add_argument("--out", type=str, default=str(_HERE / "results" / "analysis_ablation_full"))
    ap.add_argument("--fig", type=str, default=str(_HERE / "manuscript" / "figures" / "ablation_bar_full.png"))
    args = ap.parse_args()
    csv = Path(args.csv)
    df = pd.read_csv(csv)
    funcs = sorted(df.Function.unique(), key=lambda f: int(f[1:]))
    variants = [v for v in ORDER if v in df.Variant.unique()]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # --- mean/std per (Function, Variant) + Wilcoxon full vs each variant ---
    lines = ["# Ablation — Mean Best Fitness per Function x Variant (D=30, 500 NFE, 20 paired seeds)\n",
              "| Func | " + " | ".join(variants) + " |",
              "|" + "---|" * (len(variants) + 1)]
    full_d = {f: df[(df.Function == f) & (df.Variant == FULL)]["Best"].values for f in funcs}
    for f in funcs:
        cells = []
        for v in variants:
            d = df[(df.Function == f) & (df.Variant == v)]["Best"].values
            cells.append(f"{d.mean():.3e}" if len(d) else "-")
        lines.append(f"| {f} | " + " | ".join(cells) + " |")

    lines.append("\n## Wilcoxon signed-rank: full vs each ablated variant (per function, α=0.05, paired by seed)\n")
    lines.append("| Func | " + " | ".join(variants[1:]) + " |")
    lines.append("|" + "---|" * len(variants))
    win = {v: [0, 0, 0] for v in variants[1:]}
    for f in funcs:
        cells = []
        d1 = full_d[f]
        for v in variants[1:]:
            d2 = df[(df.Function == f) & (df.Variant == v)]["Best"].values
            # paired by seed (run_id*1000 identical scheme in run_benchmark.py & ablation.py)
            try:
                if len(d1) == len(d2) and len(d1) >= 6:
                    _, p = stats.wilcoxon(d1, d2)
                else:
                    _, p = stats.ranksums(d1, d2)
            except Exception:
                p = 1.0
            better = np.median(d1) < np.median(d2)
            if p < 0.05 and better:
                cells.append("full better (+)"); win[v][0] += 1
            elif p < 0.05 and not better:
                cells.append("variant better (−)"); win[v][1] += 1
            else:
                cells.append("= (n.s.)"); win[v][2] += 1
        lines.append(f"| {f} | " + " | ".join(cells) + " |")
    lines.append("\n**Recap (full wins / ablated-variant wins / ties):**")
    for v in variants[1:]:
        lines.append(f"- {v}: {win[v][0]}/{win[v][1]}/{win[v][2]}")

    (out / "ablation_stats.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {out / 'ablation_stats.md'}")

    # --- win/loss/tie counts (robust to the extreme magnitude skew seen on
    # F1/F9/F10, where a component's removal can swing fitness by >1e7x;
    # a geometric-mean ratio would be dominated by those outliers and mislead) ---
    ablated = variants[1:]
    win_counts = [win[v][0] for v in ablated]   # full significantly better
    loss_counts = [win[v][1] for v in ablated]  # ablated variant significantly better
    tie_counts = [win[v][2] for v in ablated]   # not significant

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    labels = [v.replace("IFPOA-X ", "") for v in ablated]
    x = np.arange(len(ablated))
    ax.bar(x, win_counts, label="full significantly better", color="#4C72B0")
    ax.bar(x, tie_counts, bottom=win_counts, label="not significant (tie)", color="#B0B0B0")
    bottom2 = [w + t for w, t in zip(win_counts, tie_counts)]
    ax.bar(x, loss_counts, bottom=bottom2, label="ablated variant significantly better", color="#C44E52")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylabel(f"# functions (of {len(funcs)}), Wilcoxon α=0.05", fontsize=13)
    ax.set_title("Ablation Study - Component Contribution vs Full IFPOA-X (D=30)",
                 fontsize=15, fontweight="bold")
    ax.tick_params(axis="y", labelsize=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=1, fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig_path = Path(args.fig); fig_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    fig.savefig(fig_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {fig_path}")

    print("\nWin(full)/Loss(variant)/Tie recap:")
    for v in ablated:
        print(f"  {v:24s} {win[v][0]}/{win[v][1]}/{win[v][2]}")


if __name__ == "__main__":
    main()
