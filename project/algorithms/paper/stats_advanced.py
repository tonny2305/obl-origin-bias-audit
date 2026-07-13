#!/usr/bin/env python3
"""
Analisis statistik lanjutan (kelas jurnal) untuk PAPER 1.
=========================================================
Melengkapi analyze.py dengan metodologi Derrac et al. (2011) lengkap:
  - Friedman chi-square  + koreksi Iman-Davenport (statistik F, p-value)
  - Kendall's W (effect size omnibus)
  - Post-hoc terkontrol (kontrol = IFPOA-X) berbasis selisih peringkat rata-rata:
      * adjusted p-values Holm (step-down)   [Derrac 2011, Sec. 4.2]
      * adjusted p-values Finner
  - Effect size independent-sample IFPOA-X vs tiap baseline:
      * Vargha-Delaney A12 (prob. IFPOA-X lebih baik; minimisasi)
      * Cohen's d (rata-rata lintas fungsi)
  - Bootstrap 95% CI untuk peringkat rata-rata tiap algoritma

Masukan : results{,_shifted,_cec}/raw_D{dim}.csv
Luaran  : <results>/analysis_D{dim}/stats_advanced.md
"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

PROPOSED = "IFPOA-X"


def _rank_matrix(df, algos, funcs, agg="median"):
    """Matriks nilai (funcs x algos) -> peringkat per baris (1=terbaik/terkecil)."""
    piv = df.groupby(["Function", "Algorithm"])["Best"].agg(agg).unstack()[algos].loc[funcs]
    ranks = piv.rank(axis=1, method="average")
    return piv, ranks


def _friedman_iman(ranks, k, N):
    avg = ranks.mean(axis=0).values
    chi2 = 12.0 * N / (k * (k + 1)) * (np.sum(avg ** 2) - k * (k + 1) ** 2 / 4.0)
    # Iman-Davenport F
    denom = (N * (k - 1) - chi2)
    F = ((N - 1) * chi2 / denom) if denom > 0 else np.inf
    df1, df2 = k - 1, (k - 1) * (N - 1)
    p_chi = stats.chi2.sf(chi2, k - 1)
    p_F = stats.f.sf(F, df1, df2) if np.isfinite(F) else 0.0
    W = chi2 / (N * (k - 1))          # Kendall's W in [0,1]
    return chi2, p_chi, F, (df1, df2), p_F, W


def _holm_finner(pvals, labels):
    """Kembalikan dict label -> (p_raw, p_holm, p_finner), monoton."""
    m = len(pvals)
    order = np.argsort(pvals)
    holm = np.empty(m); finner = np.empty(m)
    run_h = 0.0; run_f = 0.0
    for rank, idx in enumerate(order):          # rank = 0..m-1
        i = rank + 1
        h = (m - rank) * pvals[idx]
        f = 1.0 - (1.0 - pvals[idx]) ** (m / i)
        run_h = max(run_h, min(1.0, h))         # enforce monotonicity
        run_f = max(run_f, min(1.0, f))
        holm[idx] = run_h
        finner[idx] = run_f
    return {labels[i]: (float(pvals[i]), float(holm[i]), float(finner[i])) for i in range(m)}


def _posthoc_control(ranks, algos, control):
    """z-test selisih peringkat rata-rata vs kontrol + Holm/Finner adjusted p."""
    k, N = len(algos), ranks.shape[0]
    avg = ranks.mean(axis=0)
    se = np.sqrt(k * (k + 1) / (6.0 * N))
    others = [a for a in algos if a != control]
    z = {a: (avg[a] - avg[control]) / se for a in others}         # >0: kontrol lebih baik
    p = {a: 2.0 * stats.norm.sf(abs(z[a])) for a in others}
    adj = _holm_finner([p[a] for a in others], others)
    return avg, z, adj


def _a12(x, y):
    """Vargha-Delaney A12 = P(x<y)+0.5P(x=y) (minimisasi: prob. x lebih baik dari y)."""
    x = np.asarray(x); y = np.asarray(y)
    nx, ny = len(x), len(y)
    # rank-sum approach
    ranks = stats.rankdata(np.concatenate([x, y]))
    r1 = ranks[:nx].sum()
    a_gt = (r1 / nx - (nx + 1) / 2.0) / ny      # P(x>y)+0.5P(=)
    return 1.0 - a_gt                            # P(x<y)+0.5P(=)  (x lebih kecil = lebih baik)


def _pairwise_effect(df, funcs, baselines):
    """Per baseline: mean A12 & mean Cohen's d (IFPOA-X vs baseline) lintas fungsi."""
    out = {}
    for b in baselines:
        a12s, ds = [], []
        for f in funcs:
            x = df[(df.Function == f) & (df.Algorithm == PROPOSED)]["Best"].values
            y = df[(df.Function == f) & (df.Algorithm == b)]["Best"].values
            if len(x) < 2 or len(y) < 2:
                continue
            a12s.append(_a12(x, y))
            sp = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2.0)
            ds.append((x.mean() - y.mean()) / sp if sp > 0 else 0.0)
        out[b] = (float(np.mean(a12s)), float(np.mean(ds)))
    return out


def _bootstrap_rank_ci(ranks, algos, B=5000, seed=0):
    rng = np.random.default_rng(seed)
    N = ranks.shape[0]
    arr = ranks[algos].values                    # N x k
    boot = np.empty((B, len(algos)))
    for b in range(B):
        idx = rng.integers(0, N, N)
        boot[b] = arr[idx].mean(axis=0)
    lo = np.percentile(boot, 2.5, axis=0)
    hi = np.percentile(boot, 97.5, axis=0)
    return {a: (float(lo[i]), float(hi[i])) for i, a in enumerate(algos)}


def analyze(raw_csv, out_dir, suite_label):
    df = pd.read_csv(raw_csv)
    funcs = list(dict.fromkeys(df.Function))
    algos = list(dict.fromkeys(df.Algorithm))
    if PROPOSED in algos:
        algos = [PROPOSED] + [a for a in algos if a != PROPOSED]
    k, N = len(algos), len(funcs)

    piv, ranks = _rank_matrix(df, algos, funcs, agg="median")
    chi2, p_chi, F, (df1, df2), p_F, W = _friedman_iman(ranks, k, N)
    avg, z, adj = _posthoc_control(ranks, algos, PROPOSED)
    eff = _pairwise_effect(df, funcs, [a for a in algos if a != PROPOSED])
    ci = _bootstrap_rank_ci(ranks, algos)
    avg_sorted = avg.sort_values()

    L = [f"# Advanced Statistical Analysis — {suite_label}\n",
         f"Algorithms k = {k}; functions N = {N}; runs per cell = "
         f"{int(df.groupby(['Function','Algorithm']).size().median())}; "
         f"per-function aggregate = median.\n",
         "## Omnibus test\n",
         f"- Friedman χ² = {chi2:.3f}, df = {k-1}, p = {p_chi:.3e}",
         f"- Iman–Davenport F = {F:.3f}, df = ({df1}, {df2}), p = {p_F:.3e}",
         f"- Kendall's W (omnibus effect size) = {W:.3f} "
         f"({'small' if W<0.3 else 'moderate' if W<0.5 else 'large'} concordance)\n",
         "## Mean ranks with 95% bootstrap CI (5000 resamples over functions)\n",
         "| Algorithm | Mean rank | 95% CI |",
         "|---|---|---|"]
    for a in avg_sorted.index:
        L.append(f"| {a} | {avg[a]:.3f} | [{ci[a][0]:.2f}, {ci[a][1]:.2f}] |")

    L += ["\n## Post-hoc vs control (control = IFPOA-X), adjusted p-values\n",
          "z > 0 means the control (IFPOA-X) has the *better* (smaller) mean rank; "
          "z < 0 means the other algorithm is better. Significant (p < 0.05) after "
          "correction shown in **bold**.\n",
          "| Comparison | Δrank | z | p (raw) | p (Holm) | p (Finner) |",
          "|---|---|---|---|---|---|"]
    for a in [x for x in avg_sorted.index if x != PROPOSED]:
        p_raw, p_holm, p_finner = adj[a]
        star = "**" if p_holm < 0.05 else ""
        L.append(f"| IFPOA-X vs {a} | {avg[PROPOSED]-avg[a]:+.2f} | {z[a]:+.2f} | "
                 f"{p_raw:.3e} | {star}{p_holm:.3e}{star} | {p_finner:.3e} |")

    L += ["\n## Pairwise effect size (IFPOA-X vs each baseline, mean over functions)\n",
          "A12 = Vargha–Delaney probability that IFPOA-X yields the better (smaller) "
          "value; A12 > 0.5 favours IFPOA-X, < 0.5 favours the baseline. Cohen's d < 0 "
          "favours IFPOA-X (smaller mean).\n",
          "| Baseline | mean A12 | interpretation | mean Cohen's d |",
          "|---|---|---|---|"]
    for b in [a for a in algos if a != PROPOSED]:
        a12, d = eff[b]
        interp = ("IFPOA-X better" if a12 > 0.56 else
                  "baseline better" if a12 < 0.44 else "negligible")
        L.append(f"| {b} | {a12:.3f} | {interp} | {d:+.2f} |")

    (out_dir / "stats_advanced.md").write_text("\n".join(L), encoding="utf-8")
    print(f"  wrote {out_dir/'stats_advanced.md'}  "
          f"(Friedman p={p_chi:.1e}, ImanDav p={p_F:.1e}, W={W:.2f})")
    return {"chi2": chi2, "p_chi": p_chi, "F": F, "p_F": p_F, "W": W,
            "ranks": {a: float(avg[a]) for a in algos}, "ci": ci, "adj": adj, "eff": eff}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=str, required=True)
    ap.add_argument("--dims", type=int, nargs="+", default=[30])
    ap.add_argument("--label", type=str, default=None)
    args = ap.parse_args()
    rd = Path(args.results)
    for dim in args.dims:
        raw = rd / f"raw_D{dim}.csv"
        if not raw.exists():
            print(f"SKIP {raw} (missing)"); continue
        out = rd / f"analysis_D{dim}"; out.mkdir(parents=True, exist_ok=True)
        label = args.label or f"{rd.name} D={dim}"
        analyze(raw, out, f"{label} (D={dim})")


if __name__ == "__main__":
    main()
