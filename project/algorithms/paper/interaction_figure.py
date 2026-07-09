#!/usr/bin/env python3
"""
Figure: the OBL x geometry interaction (difference-in-differences).
Per function, the marginal benefit of OBL = log10(median_noOBL / median_full),
on the centred vs the origin-shifted suite. Shows OBL's ~4-order benefit on
centred landscapes collapses to ~0 once the optimum is displaced off-centre.
"""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = Path(__file__).resolve().parent
FUNCS = [f"F{i}" for i in range(1, 14)]
EPS = 1e-12


def med(csv, col, val):
    return pd.read_csv(_HERE / csv)[lambda d: d[col] == val].groupby("Function")["Best"].median()


def main():
    c_full = med("results/raw_D30.csv", "Algorithm", "IFPOA-X")
    c_noobl = med("results/ablation_full_D30.csv", "Variant", "IFPOA-X (no OBL)")
    s_full = med("results_shifted/raw_D30.csv", "Algorithm", "IFPOA-X")
    s_noobl = med("results_shifted/ablation_shifted_D30.csv", "Variant", "IFPOA-X (no OBL)")

    ben_c = np.array([np.log10((c_noobl[f] + EPS) / (c_full[f] + EPS)) for f in FUNCS])
    ben_s = np.array([np.log10((s_noobl[f] + EPS) / (s_full[f] + EPS)) for f in FUNCS])

    fig, ax = plt.subplots(figsize=(10, 5.5))
    y = np.arange(len(FUNCS))[::-1]
    for yi, bc, bs in zip(y, ben_c, ben_s):
        ax.plot([bs, bc], [yi, yi], color="#BBBBBB", lw=2, zorder=1)
    ax.scatter(ben_s, y, s=90, color="#DD8452", zorder=3, label="shifted suite (optimum off-centre)")
    ax.scatter(ben_c, y, s=90, color="#4C72B0", zorder=3, label="centred suite (classical F1-F13)")
    ax.axvline(0, color="k", lw=1, ls="--", alpha=0.6)
    ax.set_yticks(y); ax.set_yticklabels(FUNCS, fontsize=12)
    ax.set_xlabel("Marginal benefit of OBL  =  $\\log_{10}$(median fitness without OBL / with OBL)", fontsize=13)
    ax.set_title("OBL's benefit is conditional on origin-centred geometry (D=30)", fontsize=15, fontweight="bold")
    ax.tick_params(axis="x", labelsize=12)
    ax.grid(True, axis="x", alpha=0.3)
    ax.legend(fontsize=11, loc="center", framealpha=0.95)
    ax.margins(x=0.08)
    fig.tight_layout()
    out = _HERE / "manuscript" / "figures" / "obl_geometry_interaction.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    fig.savefig(out.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")
    print(f"centred median benefit = {np.median(ben_c):.2f}, shifted median = {np.median(ben_s):.2f}")


if __name__ == "__main__":
    main()
