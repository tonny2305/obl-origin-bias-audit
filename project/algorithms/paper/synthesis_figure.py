#!/usr/bin/env python3
"""
Figur sintesis: peringkat IFPOA-X di SELURUH kondisi origin-bias yang diuji.
Ini adalah bukti visual tunggal paling ringkas untuk tesis paper: keunggulan
IFPOA-X pada suite klasik tidak bertahan pada SATUPUN kontrol origin-bias,
terlepas dari geometri shift atau algoritma pembanding mana yang menang.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = Path(__file__).resolve().parent
PROPOSED = "IFPOA-X"

CONDITIONS = [
    ("Classical\n(origin-centred)", _HERE / "results" / "raw_D30.csv"),
    ("Shifted\n(30-70%, unsigned)", _HERE / "results_shifted" / "raw_D30.csv"),
    ("CEC2017\n(shifted+rotated)", _HERE / "results_cec" / "raw_D30.csv"),
    ("Multi-shift FAR\n(60-90%, unsigned)", _HERE / "results_shift_multi" / "far" / "raw_D30.csv"),
    ("Multi-shift MIXED\n(30-70%, signed)", _HERE / "results_shift_multi" / "mixed_full" / "raw_D30.csv"),
]


def mean_rank(csv):
    df = pd.read_csv(csv)
    algos = list(dict.fromkeys(df.Algorithm))
    med = df.groupby(["Function", "Algorithm"])["Best"].median().unstack()[algos]
    ranks = med.rank(axis=1, method="average")
    avg = ranks.mean(axis=0)
    return avg[PROPOSED], avg.idxmin(), avg.min(), len(algos)


def main():
    labels, ifpoax_ranks, winners, winner_ranks, ks = [], [], [], [], []
    for label, csv in CONDITIONS:
        if not csv.exists():
            print(f"SKIP {label}: {csv} missing"); continue
        r_ifpoax, winner, r_winner, k = mean_rank(csv)
        labels.append(label); ifpoax_ranks.append(r_ifpoax)
        winners.append(winner); winner_ranks.append(r_winner); ks.append(k)
        print(f"{label.splitlines()[0]:28s} IFPOA-X rank={r_ifpoax:.2f} of {k}  |  winner={winner} ({r_winner:.2f})")

    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(labels))
    colors = ["#2E7D32" if r <= 1.5 else "#C62828" for r in ifpoax_ranks]
    ax.bar(x, ifpoax_ranks, color=colors, edgecolor="black", alpha=0.85, width=0.55, zorder=3)
    for i, (r, w) in enumerate(zip(ifpoax_ranks, winners)):
        ax.text(i, r - 0.25, f"{r:.2f}", ha="center", fontsize=13, fontweight="bold", zorder=4)
        if w != PROPOSED:
            ax.text(i, 0.4, f"winner:\n{w}", ha="center", fontsize=10, color="#333", zorder=4)
    ax.axhline(1.0, color="#2E7D32", linestyle="--", lw=1.2, alpha=0.6, label="rank 1 (best possible)")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("IFPOA-X mean Friedman rank (of 8 algorithms)", fontsize=13)
    ax.set_title("IFPOA-X's Advantage Across Origin-Bias Conditions", fontsize=16, fontweight="bold")
    ax.tick_params(axis="y", labelsize=12)
    ax.set_ylim(6.5, -0.3)
    ax.grid(True, alpha=0.3, axis="y", zorder=0)
    ax.legend(loc="lower right", fontsize=11)
    fig.tight_layout()
    out = _HERE / "manuscript" / "figures" / "synthesis_rank_collapse.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
