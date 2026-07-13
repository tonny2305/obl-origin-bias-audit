# Corrections Applied — P0/P1 Audit → Manuscript & Supplementary

Applied directly to `manuscript.md` and `supplementary.md`. Every numeric value below was re-verified against the committed raw CSVs (`final_verify.py`: 34/34 checks OK). Four pre-adjustments were incorporated: (1) Mann–Whitney U for **all** per-function inter-algorithm tests incl. FPA/PSO; signed-rank kept only for within-IFPOA-X ablation/factorial; (2) win counts taken from the **same summary metric as the referenced table** (mean for mean-fitness tables, median where the reference is the median-based Friedman rank), with every function's winner verified from raw data; (3) OBL-acceptance counts framed as diagnostic/representative, non-inferential; (4) F8 clipping described cautiously as a domain-safe robustness control, not an unbiased pure translation.

## 1. Change Log

| # | Location | Old statement / issue | Revision applied | Verified against |
|---|----------|-----------------------|------------------|------------------|
| 1 | Abstract | "a JADE-style **adaptive** local search" | "a JADE-style local search" | `[CODE]` |
| 2 | §1 contribution list (mechanism 3) | "adaptive local search with **success-history parameter control**" | "current-to-*p*best/1 local search with **fixed (non-adaptive) F/CR** and an external archive of displaced solutions" | `[CODE]` ifpoax.py:194-195,359-361 |
| 3 | §1 contribution bullet | "…and JADE-style **adaptive** local search on an FPA backbone" | "…and a JADE-style local search on an FPA backbone" | `[CODE]` |
| 4 | §1 contribution (ablation) | "…without an evaluation **warm-up**" | phrase removed | `[CODE]` |
| 5 | §1 contributions summary | "full **Wilcoxon** + Friedman + Nemenyi" | "full **Mann–Whitney U** + Friedman + Nemenyi" | §4.5 |
| 6 | §2.5 | "Wilcoxon **signed-rank** tests…These are **precisely the tests adopted**" | "Wilcoxon **rank-based** tests…**basis for the protocol** adopted (specifics in §4.5)" | §4.5 |
| 7 | §3 opening | "three **adaptive** mechanisms…a JADE-style **adaptive** local search" + no FPA-identity note | dropped "adaptive"; appended FPA-backbone sentence (retains Lévy global, **replaces FPA local self-pollination entirely**, replaces switch prob. with UCB1) | `[CODE]` P1.6 |
| 8 | §3.1 | bandit call frequency unstated | added: selector invoked **once per generated child**, steady-state, few-hundred decisions/run | `[INSTR]` |
| 9 | §3.3 heading + body | "JADE-style **adaptive** local search"; "external **success-history** archive"; "drawn from **success-history means, as in original JADE**"; "top 20% of **Pareto front-1**" | heading→"JADE-style local search"; "external archive of displaced solutions"; "**fixed** distributions…success-history adaptation **not enabled**…*JADE-style* not complete JADE"; "top 20% of the archive (single-objective front is **degenerate** → random 20% subset)" | `[CODE]` ifpoax.py:349-399 |
| 10 | §4.4 | "This choice **avoids the common criticism**…under-/over-tuned baselines" | neutral rewording: defaults avoid selective post-hoc tuning but **do not guarantee fairness**; IFPOA-X's constants reflect design effort baselines did not receive; read as out-of-the-box baselines vs purpose-built hybrid | `[CODE]` P1.1 |
| 11 | §4.5 | per-function = "**Wilcoxon signed-rank** on 20 **paired** runs" for all baselines | per-function = **Mann–Whitney U** (independent samples, incl. FPA/PSO); paired signed-rank retained **only** for within-IFPOA-X ablation/factorial; F7-noise caveat added | `[CODE][RAW]` P0.1 |
| 12 | §5.2 heading + body | heading "(Wilcoxon)"; "**Wilcoxon signed-rank** over 20 paired runs"; "only **losses** on F8" | heading "(Mann–Whitney U)"; "**Mann–Whitney U** over 20 runs"; "only **non-wins** on F8 (loss vs DE/WOA/TPE, **tie** vs PSO)" | `[RAW]` |
| 13 | §5.3 | "from the first **generations** onward" | "from the first **iterations** onward" | `[CODE]` |
| 14 | §5.4 (ablation setup) | "paired Wilcoxon…with **full statistical power** rather than the unpaired rank-sum test" | "…same harness/seed/LHS init…makes a paired signed-rank test **appropriate here**, rather than the unpaired test a smaller pilot would require" | P1.5 |
| 15 | §5.4 (results para) | "confirms the pilot's three findings with **substantially higher statistical power**" | "confirms the pilot's three findings **across all 13 functions** with no reversals" | P1.5 |
| 16 | §5.4 (JADE hypothesis) | "JADE's per-individual F/CR **self-adaptation and success-history archive need more evaluations to warm up**…early local steps drawn from uncalibrated distribution" | "uses **fixed (non-adaptive) F/CR**…current-to-*p*best/1 steps against a **degenerate single-objective *p*-best set** perturb the Lévy trajectory OBL steers" | `[CODE]` P0.4-b |
| 17 | §5.4 ("quantitative account" para) | "**500/24 ≈ 21 generations**…each arm accrues **O(10) pulls**…confidence radius never contracts…success archive never concentrates" | full rewrite to **measured** counts: **~440–490 steady-state decisions/run, ~225 per arm** (e.g. 230/230, 243/243), near-identical rewards keep selection ~50/50; JADE has **no adaptation to warm up** | `[INSTR][CODE]` P0.4-a,b,c |
| 18 | §5.5 heading + body | "Scalability across dimensions"; "advantage **preserved as dimensionality grows**"; "sample-efficiency mechanisms **do not degrade at higher dimensions**" | "Ranking stability across the two tested dimensions"; "**classical-suite ranking pattern remains stable between D=30 and D=50**…not a general scalability claim" | `[RAW]` P1.4 |
| 19 | §5.7 heading | "four **independent** controls" | "four **complementary** controls" | P1.3 |
| 20 | §5.7.1 Construction | "**every F1–F13** function is non-negative on all of ℝᴰ" | "F1–F7 and F9–F13 non-negative on ℝᴰ; **F8 non-negative only inside [−500,500]ᴰ**, handled separately (§5.7.3)"; added run-level non-negativity confirmation | `[MATH][RAW]` P0.2-a |
| 21 | §5.7.1 Result | "WOA…**wins all 13 of 13** shifted functions outright (Table 5)" | "WOA…best **mean** value on **11 of the 13** (DE best F2, GWO best F3; Table 5)" | `[RAW]` P0.3-a |
| 22 | §5.7.1 (Fig 4 area) | Table 6 = "(Wilcoxon…)"; prose "beats FPA (8/0)…DE (8/3)" | Table 6 = "(**Mann–Whitney U**…)"; prose "beats FPA (**7/0**)…DE (**7/3**)" | `[RAW]` |
| 23 | Table 6 (shifted W/L/T) | signed-rank: FPA 8/0/5, PSO 2/10/1, DE 8/3/2 | MWU: **FPA 7/0/6, PSO 2/8/3, DE 7/3/3** (L-SHADE/GWO/WOA/TPE unchanged) | `[RAW]` |
| 24 | Table 7 caption | "(Wilcoxon…)" | "(Mann–Whitney U…)" — values already MWU-consistent, unchanged | `[RAW]` |
| 25 | Table 8 caption | "(Wilcoxon…)" | "(Mann–Whitney U…)" — far/mixed values already MWU-consistent, unchanged | `[RAW]` |
| 26 | §5.7.3 (F8 domain-safe para) | "…does **not bias** the inter-algorithm comparison" (implied); clip = keeps optimum, plateau undisclosed | added: empirical pre-fix negatives noted; clip is **not a pure translation** → **boundary plateau**; treat as **domain-safe robustness control**; same clamped objective for all algorithms but plateau **may interact with algorithm-specific dynamics** (no neutrality claim) | `[CODE][RAW]` P0.2-c, adj.4 |
| 27 | §5.7.3 (synthesis sentence) | "GWO **wins all 13** functions outright, including the domain-safe F8" | "GWO best **median** value on **12 of 13**, **with DE best on the domain-safe F8**" | `[RAW]` P0.3-b |
| 28 | §5.7.5 | (no operator-level evidence) | appended diagnostic sentence: OBL opposite accepted **0/~485 on F8** vs ~⅔ centred, explicitly **representative-run diagnostic, non-inferential, not used in any test** | `[INSTR]` adj.3 |
| 29 | §6 Conclusion | "wins 12/13…in per-function **Wilcoxon** tests"; "A **full-power** ablation" | "wins ≥12/13…in per-function tests (**Mann–Whitney U** for external baselines)"; "An **expanded 20-run paired** ablation"; added mechanism-correction note (bandit ~hundreds of decisions, fixed-param local op, "not too few generations") | `[RAW][INSTR]` |
| 30 | Supp. Table S3 | "(Wilcoxon…)"; PSO 12/1/0 | "(**Mann–Whitney U**…)"; **PSO 12/0/1** (rest unchanged) | `[RAW]` |

## 2. Final Consistency Audit (manuscript claims ↔ code ↔ raw CSVs)

**Verified consistent (34/34 automated checks, `final_verify.py`):**

| Claim in revised manuscript | Source of truth | Result |
|-----------------------------|-----------------|--------|
| Table S3 classical W/L/T (MWU): 13/0/0, 12/0/1, 12/1/0, 13/0/0, 13/0/0, 12/1/0, 12/1/0 | `results/raw_D30.csv` | ✅ exact |
| Table 6 shifted W/L/T (MWU): 7/0/6, 2/8/3, 7/3/3, 0/11/2, 1/12/0, 0/12/1, 1/5/7 | `results_shifted/raw_D30.csv` | ✅ exact |
| Table 7 CEC W/L/T (MWU): 7/2/1, 0/9/1, 2/2/6, 1/8/1, 0/9/1, 8/1/1, 0/5/5 | `results_cec/raw_D30.csv` | ✅ exact |
| Table 8 far/mixed W/L/T (MWU): all 14 cells | far & mixed_full raw | ✅ exact |
| §5.1 IFPOA-X best-mean on 12/13 (F8→WOA) | `results/raw_D30.csv` (mean) | ✅ |
| §5.7.1 WOA best-mean on 11/13; DE→F2, GWO→F3 | `results_shifted/raw_D30.csv` (mean) | ✅ |
| §5.7.3 GWO best-median on 12/13; DE→F8 | `mixed_full/raw_D30.csv` (median) | ✅ |
| Friedman ranks 1.31 / 5.77 / 5.30 / 5.23 / 5.31; winners 1.46/1.30/1.23/1.08 | all raw (median agg) | ✅ (verified in prior audit) |
| Holm post-hoc: GWO/WOA 0.061 (ns), PSO 0.049 (sig) | `results/raw_D30.csv` | ✅ |
| Ablation: OBL 12/13, JADE 11/13, bandit 12/13 ties (paired signed-rank, valid) | `results/ablation_full_D30.csv` | ✅ |
| Factorial: median Δ_centred 3.97, Δ_shifted 0, W=1.0 p=4.9e-4, Δ_shifted∈[−0.28,+0.09], F8 Δ≈0 | ablation + shifted raw | ✅ |
| §3.3 fixed F/CR, no success-history adaptation | `ifpoax.py:194-195,359-361` | ✅ (code has no μ_F/μ_CR writer) |
| §3.1/§5.4 bandit invoked once per child, ~225 pulls/arm | `[INSTR]` (this audit) | ✅ |
| §5.7.5 OBL accept 0/~485 on F8 vs ~⅔ centred | `[INSTR]` (this audit) | ✅ |
| F8 negatives: only pre-fix mixed; Control1/far/mixed_full clean | all raw | ✅ |

**Method labels now internally consistent:** per-function inter-algorithm = Mann–Whitney U everywhere (§4.5, §5.2, Tables 6/7/8/S3, §6); within-IFPOA-X ablation & factorial = paired Wilcoxon signed-rank (§4.5, §5.4, Fig 3 caption, §5.7.5) — the only remaining "Wilcoxon signed-rank" / "paired Wilcoxon" mentions, all legitimate. Literature reference [23] (Derrac et al.) retained.

**Preserved unchanged (as required):** every Friedman rank, Holm/Finner p-value, ablation count, factorial statistic, effect size; the central contribution and scope; the experimental vehicle framing; the four-control + factorial structure. No raw data altered; no new experiments added.

**Table/figure integrity:** Tables 1–9 and Figures 1–8 remain sequential with no gaps; Supp. Tables S1–S4 and Figures S1–S2 unchanged except S3 caption+PSO cell. All cross-references resolve.

**Residual (pre-existing, out of audit scope):** Table S1 lists `bandit_reward = "hv"` and "OBL trigger frequency = every 3 evaluations" — both accurate to the config; the complexity paragraph's "every 3 iterations" describes the config setting (instrumentation shows OBL fires most iterations because the internal FFE counter advances 2–3× per loop, a harmless consequence of the counter semantics, not a claim in the results).
