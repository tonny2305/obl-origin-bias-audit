#!/usr/bin/env python3
"""Regenerate promised supplementary statistics and verify submission claims."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from stats_advanced import PROPOSED, _bootstrap_rank_ci, _pairwise_effect, _posthoc_control, _rank_matrix

ROOT = Path(__file__).resolve().parent
SUPPLEMENT = ROOT / "manuscript" / "supplementary.md"
MAIN = ROOT.parents[2] / "Paper" / "SWEVO_submission_template" / "manuscript.tex"
START = "<!-- GENERATED_STATS_START -->"
END = "<!-- GENERATED_STATS_END -->"

DATA = {
    "classical_D30": (ROOT / "results/raw_D30.csv", 20),
    "classical_D50": (ROOT / "results/raw_D50.csv", 20),
    "shifted": (ROOT / "results_shifted/raw_D30.csv", 20),
    "cec2017": (ROOT / "results_cec/raw_D30.csv", 20),
    "far": (ROOT / "results_shift_multi/far/raw_D30.csv", 15),
    # mixed_full contains the domain-safe F8 rerun used in the manuscript.
    "mixed": (ROOT / "results_shift_multi/mixed_full/raw_D30.csv", 15),
}

RAW_HASHES = {
    "results/raw_D30.csv": "EB8C0CAA1C229664F4483B1B4614504A04C54A8491DD384D3FFB01563DB5C2A7",
    "results/raw_D50.csv": "D1519A63040427A06CEB01452907FB55FB00F7CF1A9CA2CF2AE9E104E1FE994D",
    "results_shifted/raw_D30.csv": "0C51789CE3F64ACF8D3307CD532DEF2DC1547FC411C5E91A852EE46D62BE86EE",
    "results_cec/raw_D30.csv": "F281A22D417C46BA79C7A90CCDBFFB627C4871A5AD94064FE3C0E05ACEB2B609",
    "results_shift_multi/far/raw_D30.csv": "CC027AB5853C66C2989C9BC7CB1719EE6767B64C5038123599703767127BE604",
    "results_shift_multi/mixed/raw_D30.csv": "F5A049CA888E31C7620533404FF0D61013C7C28A3F5E7D1D33C7221CF51FB9C8",
    "results_shift_multi/mixed_full/raw_D30.csv": "1BA57852AD8A0A6F28A7722C4A718E3DC906DFDEA88FE2C0650AA293B7C1FA20",
    "results/ablation_full_D30.csv": "4B89BE48247B070A3F4D40981A0010158F439EE8E33A75B31E50B9E452147688",
    "results_shifted/ablation_shifted_D30.csv": "F3867B17A14DA91BE9E0056E1355E1455DA4FC3CC0FD747C6763039A8772C714",
}

EXPECTED_WLT = {
    "classical_D30": {"FPA": (13, 0, 0), "PSO": (12, 0, 1), "DE": (12, 1, 0), "L-SHADE": (13, 0, 0), "GWO": (13, 0, 0), "WOA": (12, 1, 0), "TPE": (12, 1, 0)},
    "shifted": {"FPA": (7, 0, 6), "PSO": (2, 8, 3), "DE": (7, 3, 3), "L-SHADE": (0, 11, 2), "GWO": (1, 12, 0), "WOA": (0, 12, 1), "TPE": (1, 5, 7)},
    "cec2017": {"FPA": (7, 2, 1), "PSO": (0, 9, 1), "DE": (2, 2, 6), "L-SHADE": (1, 8, 1), "GWO": (0, 9, 1), "WOA": (8, 1, 1), "TPE": (0, 5, 5)},
    "far": {"FPA": (11, 0, 2), "PSO": (1, 6, 6), "DE": (7, 3, 3), "L-SHADE": (1, 10, 2), "GWO": (1, 10, 2), "WOA": (0, 12, 1), "TPE": (2, 5, 6)},
    "mixed": {"FPA": (6, 0, 7), "PSO": (0, 10, 3), "DE": (6, 3, 4), "L-SHADE": (0, 11, 2), "GWO": (0, 13, 0), "WOA": (11, 1, 1), "TPE": (0, 7, 6)},
}

EXPECTED_RANK = {"classical_D30": 1.31, "classical_D50": 1.31, "shifted": 5.77,
                 "cec2017": 5.30, "far": 5.23, "mixed": 5.31}


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA[name][0])


def algorithms_and_functions(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    algorithms = list(dict.fromkeys(df["Algorithm"]))
    algorithms = [PROPOSED] + [a for a in algorithms if a != PROPOSED]
    return algorithms, list(dict.fromkeys(df["Function"]))


def wlt(df: pd.DataFrame) -> dict[str, tuple[int, int, int]]:
    algorithms, functions = algorithms_and_functions(df)
    result = {}
    for baseline in [a for a in algorithms if a != PROPOSED]:
        counts = [0, 0, 0]
        for function in functions:
            x = df[(df.Function == function) & (df.Algorithm == PROPOSED)]["Best"].to_numpy()
            y = df[(df.Function == function) & (df.Algorithm == baseline)]["Best"].to_numpy()
            p = stats.mannwhitneyu(x, y, alternative="two-sided").pvalue
            index = 0 if p < 0.05 and np.median(x) < np.median(y) else 1 if p < 0.05 else 2
            counts[index] += 1
        result[baseline] = tuple(counts)
    return result


def advanced(df: pd.DataFrame):
    algorithms, functions = algorithms_and_functions(df)
    _, ranks = _rank_matrix(df, algorithms, functions)
    average, z, adjusted = _posthoc_control(ranks, algorithms, PROPOSED)
    effects = _pairwise_effect(df, functions, [a for a in algorithms if a != PROPOSED])
    ci = _bootstrap_rank_ci(ranks, algorithms)
    return algorithms, functions, average, z, adjusted, effects, ci


def fmt(value: float) -> str:
    return f"{value:.3e}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def generated_statistics() -> str:
    cec = load("cec2017")
    algorithms, functions, average, z, adjusted, effects, ci = advanced(cec)
    cec_rows = []
    for function in functions:
        row = [function]
        for algorithm in algorithms:
            values = cec[(cec.Function == function) & (cec.Algorithm == algorithm)]["Best"]
            row.append(f"{fmt(values.median())} [{fmt(values.quantile(.25))}, {fmt(values.quantile(.75))}]")
        cec_rows.append(row)

    parts = [
        "## Complete statistical results promised in the main manuscript", "",
        "All entries below are regenerated from the released raw CSV files. External inter-algorithm effects use independent run samples; ranks use the per-function medians.", "",
        "**Supplementary Table S5. CEC2017 final error: median [Q1, Q3] over 20 independent runs (D=30, 500 NFE).**",
        "", table(["Function", *algorithms], cec_rows), "",
        "**Supplementary Table S6. CEC2017 mean Friedman ranks and 95% bootstrap confidence intervals (5000 resamples over functions).**",
        "", table(["Algorithm", "Mean rank", "95% CI"], [[a, f"{average[a]:.3f}", f"[{ci[a][0]:.2f}, {ci[a][1]:.2f}]"] for a in average.sort_values().index]), "",
        "**Supplementary Table S7. CEC2017 post-hoc comparisons against IFPOA-X (two-sided normal approximation to mean-rank differences).**",
        "", table(["Comparison", "Delta rank", "z", "p raw", "p Holm", "p Finner"],
              [[f"IFPOA-X vs {a}", f"{average[PROPOSED]-average[a]:+.2f}", f"{z[a]:+.2f}", fmt(adjusted[a][0]), fmt(adjusted[a][1]), fmt(adjusted[a][2])]
               for a in average.sort_values().index if a != PROPOSED]), "",
        "**Supplementary Table S8. CEC2017 independent-sample effect sizes (mean over functions).**",
        "", table(["Baseline", "Vargha-Delaney A12", "Mean Cohen's d"], [[a, f"{effects[a][0]:.3f}", f"{effects[a][1]:+.2f}"] for a in algorithms if a != PROPOSED]),
    ]

    rank_rows, p_rows, effect_rows = [], [], []
    for dimension, name in (("D=30", "classical_D30"), ("D=50", "classical_D50")):
        algorithms, _, average, z, adjusted, effects, ci = advanced(load(name))
        rank_rows.extend([[dimension, a, f"{average[a]:.3f}", f"[{ci[a][0]:.2f}, {ci[a][1]:.2f}]"] for a in average.sort_values().index])
        p_rows.extend([[dimension, f"IFPOA-X vs {a}", f"{average[PROPOSED]-average[a]:+.2f}", f"{z[a]:+.2f}", fmt(adjusted[a][0]), fmt(adjusted[a][1]), fmt(adjusted[a][2])]
                       for a in average.sort_values().index if a != PROPOSED])
        effect_rows.extend([[dimension, a, f"{effects[a][0]:.3f}", f"{effects[a][1]:+.2f}"] for a in algorithms if a != PROPOSED])

    parts.extend(["",
        "**Supplementary Table S9. Classical-suite mean Friedman ranks and 95% bootstrap confidence intervals (5000 resamples over functions).**",
        "", table(["Dimension", "Algorithm", "Mean rank", "95% CI"], rank_rows), "",
        "**Supplementary Table S10. Classical-suite post-hoc comparisons against IFPOA-X.**",
        "", table(["Dimension", "Comparison", "Delta rank", "z", "p raw", "p Holm", "p Finner"], p_rows), "",
        "**Supplementary Table S11. Classical-suite independent-sample effect sizes (mean over functions).**",
        "", table(["Dimension", "Baseline", "Vargha-Delaney A12", "Mean Cohen's d"], effect_rows)])
    return "\n".join(parts)


def verify() -> None:
    checks = 0
    for relative, expected in RAW_HASHES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest().upper()
        assert actual == expected, f"raw-data hash changed: {relative}"
        checks += 1
    for name, (path, expected_runs) in DATA.items():
        df = pd.read_csv(path)
        cell_counts = df.groupby(["Function", "Algorithm"]).size()
        assert cell_counts.nunique() == 1 and int(cell_counts.iloc[0]) == expected_runs, name
        algorithms, functions = algorithms_and_functions(df)
        _, ranks = _rank_matrix(df, algorithms, functions)
        assert round(float(ranks[PROPOSED].mean()), 2) == EXPECTED_RANK[name], name
        checks += 2
    for name, expected in EXPECTED_WLT.items():
        assert wlt(load(name)) == expected, f"W/L/T mismatch: {name}"
        checks += 1

    supplement = SUPPLEMENT.read_text(encoding="utf-8")
    main = MAIN.read_text(encoding="utf-8")
    for baseline, counts in EXPECTED_WLT["classical_D30"].items():
        assert f"| {baseline} | {counts[0]} | {counts[1]} | {counts[2]} |" in supplement
    checks += 1
    for suite in ("shifted", "cec2017"):
        for baseline, counts in EXPECTED_WLT[suite].items():
            assert f"{baseline} & {counts[0]} & {counts[1]} & {counts[2]}" in main
        checks += 1
    for baseline in EXPECTED_WLT["far"]:
        far = "/".join(map(str, EXPECTED_WLT["far"][baseline]))
        mixed = "/".join(map(str, EXPECTED_WLT["mixed"][baseline]))
        assert f"{baseline} & {far} & {mixed}" in main
    checks += 1

    for label in ("tab:ablation", "tab:farmixedwlt", "tab:synthesis", "fig:ablation-bar",
                  "fig:cd-shifted", "fig:convergence-shifted", "fig:synthesis"):
        assert f"\\ref{{{label}}}" in main, f"missing explicit reference: {label}"
    assert "Supplementary Figure S2" in main
    checks += 1

    source = (ROOT / "analyze.py").read_text(encoding="utf-8")
    assert "stats.mannwhitneyu(d1, d2, alternative=\"two-sided\")" in source
    assert "stats.wilcoxon(d1, d2" not in source
    checks += 2
    print(f"Final verification: {checks}/{checks} checks OK")


def write_supplement() -> None:
    text = SUPPLEMENT.read_text(encoding="utf-8")
    assert text.count(START) == text.count(END) == 1, "supplement generation markers missing"
    before, remainder = text.split(START, 1)
    _, after = remainder.split(END, 1)
    SUPPLEMENT.write_text(before + START + "\n\n" + generated_statistics() + "\n\n" + END + after, encoding="utf-8")
    print(f"Updated {SUPPLEMENT}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-supplement", action="store_true")
    args = parser.parse_args()
    if args.write_supplement:
        write_supplement()
    verify()


if __name__ == "__main__":
    main()
