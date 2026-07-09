#!/usr/bin/env python3
"""
Statistical analysis & visualization, PAPER 1 (per dimension).
================================================================
Input  : results/raw_D{dim}.csv, results/curves_D{dim}.npz (from run_benchmark.py)
Output : results/analysis_D{dim}/
  - summary.md / summary.csv         : best/worst/mean/std/median per function x algorithm
  - stats.md                         : Wilcoxon (per function), Friedman, mean rank
  - convergence_grid.png/.pdf        : convergence curves, 13 functions (equal-NFE)
  - cd_diagram.png/.pdf              : Critical Difference diagram (Nemenyi, α=0.05)

Tests: Wilcoxon signed-rank (IFPOA-X vs each baseline), Friedman, mean rank,
Demšar (2006) methodology with Critical Difference (post-hoc Nemenyi).
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = Path(__file__).resolve().parent
PROPOSED = "IFPOA-X"
# Nilai kritis q_alpha (α=0.05) untuk uji Nemenyi (Demšar 2006, Tabel 5a)
_Q05 = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949,
        8: 3.031, 9: 3.102, 10: 3.164, 11: 3.219, 12: 3.268}


def summary_table(df):
    g = df.groupby(["Function", "Algorithm"])["Best"]
    s = g.agg(Best="min", Worst="max", Mean="mean", Std="std", Median="median").reset_index()
    return s


def _fmt(v):
    return f"{v:.3e}"


def write_summary(df, algos, funcs, out):
    s = summary_table(df)
    lines = ["# Summary Statistics of Final Fitness\n",
             "| Function | Algorithm | Best | Worst | Mean | Std | Median |",
             "|---|---|---|---|---|---|---|"]
    for f in funcs:
        # mark the winner (smallest mean) per function
        sub = s[s.Function == f]
        if sub.empty:
            continue
        win = sub.loc[sub.Mean.idxmin(), "Algorithm"]
        for a in algos:
            r = sub[sub.Algorithm == a]
            if r.empty:
                continue
            r = r.iloc[0]
            name = f"**{a}**" if a == win else a
            lines.append(f"| {f} | {name} | {_fmt(r.Best)} | {_fmt(r.Worst)} | "
                         f"{_fmt(r.Mean)} | {_fmt(r.Std)} | {_fmt(r.Median)} |")
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    s.to_csv(out / "summary.csv", index=False, float_format="%.6e")
    return s


def stats_analysis(df, algos, funcs, out):
    baselines = [a for a in algos if a != PROPOSED]
    L = ["# Statistical Significance Tests\n"]

    # --- Wilcoxon per function: IFPOA-X vs each baseline (20 paired runs) ---
    L.append("## Wilcoxon signed-rank: IFPOA-X vs baseline (per function)\n")
    L.append("Win/loss summary for IFPOA-X (α=0.05): '+' significantly better, '−' worse, '=' not significant.\n")
    header = "| Function | " + " | ".join(baselines) + " |"
    L.append(header); L.append("|" + "---|" * (len(baselines) + 1))
    win = {b: [0, 0, 0] for b in baselines}  # [win, loss, tie]
    for f in funcs:
        cells = []
        d1 = df[(df.Function == f) & (df.Algorithm == PROPOSED)].sort_values("Run")["Best"].values
        for b in baselines:
            d2 = df[(df.Function == f) & (df.Algorithm == b)].sort_values("Run")["Best"].values
            try:
                _, p = stats.wilcoxon(d1, d2)
            except Exception:
                p = 1.0
            better = np.median(d1) < np.median(d2)
            if p < 0.05 and better:
                cells.append("+"); win[b][0] += 1
            elif p < 0.05 and not better:
                cells.append("−"); win[b][1] += 1
            else:
                cells.append("="); win[b][2] += 1
        L.append(f"| {f} | " + " | ".join(cells) + " |")
    L.append("\n**Recap (win/loss/tie) IFPOA-X:**")
    for b in baselines:
        L.append(f"- vs {b}: {win[b][0]}/{win[b][1]}/{win[b][2]}")

    # --- Mean rank (median per function) + Friedman + Nemenyi CD ---
    med = df.groupby(["Function", "Algorithm"])["Best"].median().unstack()[algos]
    ranks = med.rank(axis=1, method="average")  # rank 1 = best (smallest value)
    avg_rank = ranks.mean(axis=0)
    k, N = len(algos), len(funcs)
    try:
        chi2, p_fried = stats.friedmanchisquare(*[med[a].values for a in algos])
    except Exception:
        chi2, p_fried = float("nan"), float("nan")
    q = _Q05.get(k, 3.3)
    CD = q * np.sqrt(k * (k + 1) / (6.0 * N))

    L.append("\n## Mean Rank (Friedman) & Critical Difference\n")
    L.append(f"Friedman: χ²={chi2:.3f}, p={p_fried:.3e} (k={k} algorithms, N={N} functions)")
    L.append(f"Critical Difference (Nemenyi, α=0.05): CD = {CD:.3f}\n")
    L.append("| Algorithm | Mean Rank |")
    L.append("|---|---|")
    for a in avg_rank.sort_values().index:
        L.append(f"| {a} | {avg_rank[a]:.3f} |")

    (out / "stats.md").write_text("\n".join(L), encoding="utf-8")
    return avg_rank.sort_values(), CD, (chi2, p_fried)


def cd_diagram(avg_rank, CD, out):
    """Critical Difference diagram gaya Demšar (2006) dengan clique bars."""
    order = avg_rank.sort_values()          # rank kecil (terbaik) dulu
    algos = list(order.index)
    ranks = order.values
    k = len(algos)
    lo, hi = int(np.floor(ranks.min())), int(np.ceil(ranks.max()))
    axis_y = 0.80
    fig, ax = plt.subplots(figsize=(10.5, 2.6 + 0.38 * k))
    ax.set_xlim(lo - 0.5, hi + 0.5); ax.set_ylim(0, 1); ax.axis("off")

    # rank axis + ticks
    ax.plot([lo, hi], [axis_y, axis_y], "k-", lw=1.8)
    for x in range(lo, hi + 1):
        ax.plot([x, x], [axis_y, axis_y + 0.025], "k-", lw=1.2)
        ax.text(x, axis_y + 0.05, str(x), ha="center", va="bottom", fontsize=12)

    # CD bar (above the axis, does not overlap the title)
    ax.plot([lo, lo + CD], [axis_y + 0.14, axis_y + 0.14], "k-", lw=3)
    ax.plot([lo, lo], [axis_y + 0.12, axis_y + 0.16], "k-", lw=1.2)
    ax.plot([lo + CD, lo + CD], [axis_y + 0.12, axis_y + 0.16], "k-", lw=1.2)
    ax.text(lo + CD / 2, axis_y + 0.17, f"CD = {CD:.2f}", ha="center", va="bottom", fontsize=12)

    # algorithm connectors: best half to the left, remainder to the right
    n_left = (k + 1) // 2
    label_y = []
    for i, (a, r) in enumerate(zip(algos, ranks)):
        left = i < n_left
        row = i if left else (k - 1 - i)
        yy = axis_y - 0.14 - 0.09 * row
        xtext = lo - 0.4 if left else hi + 0.4
        ha = "right" if left else "left"
        ax.plot([r, r], [axis_y, yy], "k-", lw=1.1)
        ax.plot([r, xtext], [yy, yy], "k-", lw=1.1)
        ax.text(xtext + (-0.05 if left else 0.05), yy,
                f"{a} ({r:.2f})", ha=ha, va="center", fontsize=12)
        label_y.append(yy)

    # clique bars: grup algoritma yang selisih rank-nya <= CD (tak beda signifikan)
    cliques = []
    i = 0
    while i < k:
        j = i
        while j + 1 < k and (ranks[j + 1] - ranks[i]) <= CD:
            j += 1
        if j > i:  # grup > 1 anggota
            cliques.append((i, j))
        i += 1
    # buang clique yang merupakan subset clique lain
    cliques = [c for idx, c in enumerate(cliques)
               if not any(o[0] <= c[0] and c[1] <= o[1] and o != c for o in cliques)]
    yb = axis_y - 0.06
    for (a, b) in cliques:
        ax.plot([ranks[a] - 0.03, ranks[b] + 0.03], [yb, yb], "k-", lw=4, solid_capstyle="round")
        yb -= 0.035

    ax.set_title("Critical Difference Diagram (Nemenyi, α=0.05)", fontsize=15, y=1.02)
    fig.tight_layout()
    fig.savefig(out / "cd_diagram.png", dpi=300, bbox_inches="tight")
    fig.savefig(out / "cd_diagram.pdf", bbox_inches="tight")
    plt.close(fig)


def convergence_grid(npz_path, funcs, algos, out):
    data = np.load(npz_path)
    cols = plt.cm.tab10(np.linspace(0, 1, len(algos)))
    ncol = 4; nrow = int(np.ceil(len(funcs) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.6 * ncol, 3.6 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for ax, f in zip(axes, funcs):
        for a, c in zip(algos, cols):
            key = f"{f}|{a}"
            if key not in data:
                continue
            arr = data[key]
            m = np.nanmean(arr, axis=0)
            x = np.arange(1, len(m) + 1)
            lw = 2.6 if a == PROPOSED else 1.5
            ax.plot(x, np.maximum(m, 1e-12), label=a, color=c, lw=lw)
        ax.set_yscale("log"); ax.set_title(f, fontsize=15, fontweight="bold")
        ax.set_xlabel("NFE", fontsize=13)
        ax.set_ylabel("Best fitness (log)", fontsize=12)
        ax.tick_params(axis="both", labelsize=11)
        ax.grid(True, alpha=0.3)
    for ax in axes[len(funcs):]:
        ax.axis("off")
    axes[0].legend(fontsize=12, loc="upper right", framealpha=0.9)
    fig.suptitle("Convergence Curves F1-F13 (mean, equal-NFE)", fontsize=18, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(out / "convergence_grid.png", dpi=300, bbox_inches="tight")
    fig.savefig(out / "convergence_grid.pdf", bbox_inches="tight")
    plt.close(fig)


def emit_markdown_tables(df, avg_rank, CD, fried, algos, funcs, dim, man_dir):
    """Write paste-ready Markdown tables + copy figures to the manuscript folder."""
    tdir = Path(man_dir) / "tables"; tdir.mkdir(parents=True, exist_ok=True)
    med = df.groupby(["Function", "Algorithm"])["Best"].mean().unstack()[algos]
    # --- summary: mean per function x algorithm, best in bold ---
    head = "| Func | " + " | ".join(algos) + " |"
    sep = "|" + "---|" * (len(algos) + 1)
    lines = [f"**Table: Mean final fitness (D={dim}, 500 NFE, 20 runs). Best in bold.**\n",
             head, sep]
    for f in funcs:
        row = med.loc[f]
        best_algo = row.idxmin()
        cells = [(f"**{row[a]:.2e}**" if a == best_algo else f"{row[a]:.2e}") for a in algos]
        lines.append(f"| {f} | " + " | ".join(cells) + " |")
    chi2, p = fried
    lines.append("| **Mean rank** | " +
                 " | ".join(f"{avg_rank[a]:.2f}" for a in algos) + " |")
    lines.append(f"\nFriedman: χ²={chi2:.3f}, p={p:.3e}; Nemenyi CD={CD:.3f} (α=0.05).")
    (tdir / f"summary_D{dim}.md").write_text("\n".join(lines), encoding="utf-8")

    # --- wilcoxon win/loss/tie IFPOA-X vs baseline ---
    baselines = [a for a in algos if a != PROPOSED]
    rec = {b: [0, 0, 0] for b in baselines}
    for f in funcs:
        d1 = df[(df.Function == f) & (df.Algorithm == PROPOSED)].sort_values("Run")["Best"].values
        for b in baselines:
            d2 = df[(df.Function == f) & (df.Algorithm == b)].sort_values("Run")["Best"].values
            try:
                _, pw = stats.wilcoxon(d1, d2)
            except Exception:
                pw = 1.0
            better = np.median(d1) < np.median(d2)
            rec[b][0 if (pw < 0.05 and better) else 1 if (pw < 0.05) else 2] += 1
    wl = [f"**Table: IFPOA-X vs baseline - win/loss/tie (Wilcoxon, α=0.05), D={dim}.**\n",
          "| Baseline | Win | Loss | Tie |", "|---|---|---|---|"]
    for b in baselines:
        wl.append(f"| {b} | {rec[b][0]} | {rec[b][1]} | {rec[b][2]} |")
    (tdir / f"wilcoxon_D{dim}.md").write_text("\n".join(wl), encoding="utf-8")

    # --- copy figures to manuscript/figures/ (PNG + vector PDF) ---
    fdir = Path(man_dir) / "figures"; fdir.mkdir(parents=True, exist_ok=True)
    import shutil
    for stem in ("convergence_grid", "cd_diagram"):
        for ext in ("png", "pdf"):
            cand = _HERE / "results" / f"analysis_D{dim}" / f"{stem}.{ext}"
            if cand.exists():
                shutil.copy(cand, fdir / f"{stem}_D{dim}.{ext}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dims", type=int, nargs="+", default=[30, 50])
    ap.add_argument("--results", type=str, default=str(_HERE / "results"))
    ap.add_argument("--manuscript", type=str, default=None,
                    help="Jika diisi, tulis tabel Markdown + salin figur ke folder manuscript ini.")
    args = ap.parse_args()
    rd = Path(args.results)

    for dim in args.dims:
        raw = rd / f"raw_D{dim}.csv"
        if not raw.exists():
            print(f"SKIP D{dim}: {raw} tidak ada"); continue
        df = pd.read_csv(raw)
        funcs = list(dict.fromkeys(df.Function))
        algos = list(dict.fromkeys(df.Algorithm))
        if PROPOSED in algos:  # taruh IFPOA-X pertama
            algos = [PROPOSED] + [a for a in algos if a != PROPOSED]
        out = rd / f"analysis_D{dim}"; out.mkdir(parents=True, exist_ok=True)

        write_summary(df, algos, funcs, out)
        avg_rank, CD, (chi2, p) = stats_analysis(df, algos, funcs, out)
        cd_diagram(avg_rank, CD, out)
        npz = rd / f"curves_D{dim}.npz"
        if npz.exists():
            convergence_grid(npz, funcs, algos, out)
        if args.manuscript:
            emit_markdown_tables(df, avg_rank, CD, (chi2, p), algos, funcs, dim, args.manuscript)
        print(f"D{dim}: Friedman chi2={chi2:.2f} p={p:.2e} | ranks: " +
              ", ".join(f"{a}={avg_rank[a]:.2f}" for a in avg_rank.index) +
              f" | CD={CD:.2f}  -> {out}")

    print("DONE analyze.")


if __name__ == "__main__":
    main()
