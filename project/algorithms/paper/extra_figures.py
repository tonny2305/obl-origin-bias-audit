#!/usr/bin/env python3
"""
Figur tambahan PAPER 1 (dari data yang sudah ada — tidak menjalankan ulang
eksperimen). Menjawab kebutuhan >2 figur untuk kelayakan publikasi:
  - rank_boxplot_D{dim}.png     : sebaran peringkat per-fungsi tiap algoritma
                                   (melengkapi Tabel 3/4 — satu angka rata-rata
                                   saja tidak menunjukkan variabilitas).
  - scalability_D30_D50.png     : perbandingan peringkat rata-rata D=30 vs D=50
                                   (bukti visual untuk klaim §5.5).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = Path(__file__).resolve().parent
PROPOSED = "IFPOA-X"


def rank_boxplot(raw_csv, dim, out_dir):
    df = pd.read_csv(raw_csv)
    algos = list(dict.fromkeys(df.Algorithm))
    if PROPOSED in algos:
        algos = [PROPOSED] + [a for a in algos if a != PROPOSED]
    # rank per (Function, Run): 1 = terbaik (Best terkecil) di antara algoritma
    ranks = (df.groupby(["Function", "Run"])
               .apply(lambda g: g.set_index("Algorithm")["Best"].rank(method="average"))
               .reset_index())
    fig, ax = plt.subplots(figsize=(10, 5))
    data = [ranks[a].dropna().values for a in algos]
    bp = ax.boxplot(data, tick_labels=algos, patch_artist=True, showmeans=True)
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor("#4C72B0" if algos[i] == PROPOSED else "#B0B0B0")
        box.set_alpha(0.75)
    ax.set_ylabel("Rank per (function, run) - 1 = best", fontsize=13)
    ax.set_title(f"Rank Distribution Across Algorithms (D={dim}, 13 functions x 20 runs)",
                 fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", labelsize=12)
    ax.grid(True, alpha=0.3, axis="y")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(out_dir / f"rank_boxplot_D{dim}.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / f"rank_boxplot_D{dim}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_dir / f'rank_boxplot_D{dim}.png'}")


def scalability_plot(raw_csv_30, raw_csv_50, out_dir):
    def avg_rank(path):
        df = pd.read_csv(path)
        med = df.groupby(["Function", "Algorithm"])["Best"].median().unstack()
        return med.rank(axis=1, method="average").mean(axis=0)

    r30, r50 = avg_rank(raw_csv_30), avg_rank(raw_csv_50)
    algos = sorted(r30.index, key=lambda a: r30[a])
    x = np.arange(len(algos))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w / 2, [r30[a] for a in algos], width=w, label="D = 30", color="#4C72B0")
    ax.bar(x + w / 2, [r50[a] for a in algos], width=w, label="D = 50", color="#DD8452")
    ax.set_xticks(x); ax.set_xticklabels(algos, rotation=20, ha="right", fontsize=12)
    ax.set_ylabel("Mean rank (Friedman)", fontsize=13)
    ax.set_title("Rank Stability Across Dimensions (D=30 vs D=50)",
                 fontsize=15, fontweight="bold")
    ax.tick_params(axis="y", labelsize=12)
    ax.legend(fontsize=12); ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(out_dir / "scalability_D30_D50.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "scalability_D30_D50.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_dir / 'scalability_D30_D50.png'}")


def main():
    results = _HERE / "results"
    fig_dir = _HERE / "manuscript" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    rank_boxplot(results / "raw_D30.csv", 30, fig_dir)
    rank_boxplot(results / "raw_D50.csv", 50, fig_dir)
    scalability_plot(results / "raw_D30.csv", results / "raw_D50.csv", fig_dir)


if __name__ == "__main__":
    main()
