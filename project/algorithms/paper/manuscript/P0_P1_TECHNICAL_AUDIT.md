# P0/P1 Technical Audit — IFPOA-X Origin-Bias Manuscript

**Scope:** Every claim below was cross-checked against **source code**, **raw result CSVs**, and **statistical scripts** — not against the manuscript text. All recomputations were run with the project venv (`scipy 1.16.3`, `numpy 1.26`, `pandas 2.3.3`) directly on the committed raw data. Live instrumentation of `ifpoax.py` was performed for P0.4. Where a number is quoted as "verified", it was regenerated from raw data and matched the manuscript; where "FALSE/overclaim", the raw data contradicts the text.

**Evidence provenance tags:** `[CODE]` read from source; `[RAW]` recomputed from result CSVs; `[INSTR]` measured by live instrumentation; `[MATH]` analytic.

---

## 1. EXECUTIVE VERDICT

**No fatal flaw was found. No experimental rerun is required. The central conclusions are intact.** The audit did, however, find **two Major issues that are code-vs-manuscript contradictions** (both in the *mechanistic explanation*, not in the results), **one Major methodological-description issue** (paired-test validity), and **four Moderate issues** (two numerical overclaims, one false blanket math statement, one undisclosed landscape distortion). All are fixable by **textual correction + statistical recomputation from existing raw data**. None touch the paper's spine.

**What survives, verified exactly against raw data:**
- IFPOA-X classical mean Friedman rank **1.31** (D=30 and D=50); all eight per-algorithm ranks match. `[RAW]`
- Holm-corrected post-hoc: GWO and WOA **p = 0.0613** (ns), PSO **p = 0.0489** (sig), others sig. Exactly as stated. `[RAW]`
- Ablation: removing OBL hurts on **12/13**; JADE counter-productive on **11/13**; bandit **12/13 ties**. Exactly as stated. `[RAW]`
- The §5.7.5 factorial — the paper's strongest claim — reproduces **exactly**: median Δ_centred = 3.97, median Δ_shifted = 0.00, paired **W = 1.0, p = 4.88×10⁻⁴**, Δ_shifted ∈ [−0.28, +0.09], F8 Δ_centred ≈ 0. `[RAW]`
- Rank collapse under all four controls (5.23–5.77) verified. `[RAW]`
- Domain-safe F8 fix works: **0 negative values** post-fix; negatives occurred **only** in the pre-fix "mixed" config (49/120), never in Control 1 or "far". `[RAW]`

**What must change (none alters a conclusion):**
1. **P0.4 / P1.2 (Major, code contradiction).** JADE's F and CR are drawn from **fixed constant means (0.5)** with **no success-history adaptation anywhere in the code**. The §3.3 phrase "success-history parameter control" and the §5.4 explanation that JADE fails because "F/CR self-adaptation needs to warm up" are **contradicted by the code** — there is no adaptation to warm up. The *ablation result* (JADE hurts) is real and unchanged; only the *reason* is wrong.
2. **P0.4 (Major, code contradiction).** The "budget arithmetic" (~21 generations, ~10 bandit pulls per arm) does not match the code. The loop is **steady-state, not generational**; instrumentation shows **~450–486 iterations and ~225 pulls per arm** per run. The correct evidence for "bandit ≈ uniform" is the measured **~50/50 arm split**, not a shortage of pulls.
3. **P0.1 (Major, methodology description).** The per-function Wilcoxon **signed-rank** test pairs 20 runs by seed. Pairing is valid only for IFPOA-X vs FPA/PSO (common random numbers) and for the within-IFPOA-X ablation/factorial; it is **not valid for the five external baselines** (independent RNG, uniform vs LHS init). Switching to Mann-Whitney U changes **no conclusion** (a handful of tie-boundary cells shift by 1).
4. **P0.3 (Moderate).** "WOA wins **all 13**" (§5.7.1) → actually **11/13**; "GWO wins **all 13**" (§5.7.3) → actually **12/13**. Both contradict their own stated Friedman ranks (1.46, 1.08).
5. **P0.2 (Moderate).** §5.7.1's blanket "every F1–F13 is non-negative on all of ℝᴰ" is **mathematically false for F8** and contradicts §5.7.3. The domain-safe F8 is a **clipped** landscape (boundary plateau), which should be disclosed.

**Bonus finding that STRENGTHENS the paper:** instrumentation shows the OBL opposite is accepted **0 / 485 times on F8** (off-centre optimum) versus ~300/450 on the centred functions — direct mechanistic corroboration of the origin-geometry thesis, currently unreported.

**SWEVO suitability:** unchanged and still appropriate after corrections. The audit actually improves defensibility, because the two Major fixes replace an incorrect mechanistic story with the true one, and the true one is *equally* consistent with the paper's thesis.

**Final decision: (1) Safe after textual/statistical corrections.** The required P0.4 diagnostic instrumentation is already complete (this report); everything else is recomputation from committed raw data.

---

## 2. P0 FINDINGS TABLE

| ID | Finding | Severity | Evidence | Required action | New experiment? |
|----|---------|----------|----------|-----------------|-----------------|
| P0.1-a | Per-function Wilcoxon **signed-rank** invalid for IFPOA-X vs 5 external baselines (independent RNG/init; only seed *number* shared). `run_benchmark.py:61-74`, `baselines.py:46-89`, `analyze.py:81` | **Major** (method description) | `[CODE][RAW]` MWU vs signed-rank recomputed; only tie-boundary cells move ±1 | Relabel/​recompute per-function tests as Mann-Whitney U (or restrict pairing to FPA/PSO). Update Tables 6, 7, S3. | No — recompute from raw |
| P0.1-b | IFPOA-X vs **FPA/PSO** pairing IS valid (harness reseeds `random`/`numpy` per run → identical LHS init = CRN). Ablation & factorial pairing valid (within-IFPOA-X). `benchmark_tester.py:1069-1070`, `run_benchmark.py:62-63` | No issue | `[CODE]` | Keep signed-rank for these; state the CRN justification explicitly | No |
| P0.2-a | §5.7.1 "every F1–F13 non-negative on all of ℝᴰ" is **false for F8**; contradicts §5.7.3. | **Moderate** (math) | `[MATH]` F8 = 418.98·D − Σx·sin√\|x\|; unbounded below outside [−500,500]ᴰ | Fix §5.7.1 wording to carve out F8 | No |
| P0.2-b | Negative F8 fitness occurs **only** in pre-fix "mixed" (49/120 rows, min −6400); Control 1 (min +784) and "far" (min +5907) are clean. Manuscript's empirical claim is **correct**. | No issue (confirms text) | `[RAW]` | None (verifies the claim) | No |
| P0.2-c | Domain-safe F8 = `f8(clip(x−s,−500,500))` → **boundary plateau** (landscape distortion), applied identically to all 8 algorithms. Not disclosed. | **Moderate** | `[CODE]` `rerun_f8_mixed.py:56-62` | Disclose the plateau in §5.7.3 / limitations | No |
| P0.2-d | `verify_shift.py` samples only 2000 random points — too weak to detect F8's narrow negative basin; passes vacuously. Actual results (P0.2-b) are the real safeguard. | Minor | `[CODE]` `verify_shift.py:37-38` | Note that empirical run-level non-negativity is the operative check | No |
| P0.3-a | "WOA wins **all 13**" shifted (§5.7.1) → **11/13** by median (12/13 for "far"). | **Moderate** (overclaim) | `[RAW]` WOA rank 1.46 ⇒ cannot be 13 wins | Replace "all 13" with "11 of 13" (and give the true winner split) | No |
| P0.3-b | "GWO wins **all 13**" mixed (§5.7.3) → **12/13**. | **Moderate** (overclaim) | `[RAW]` GWO rank 1.08 ⇒ 12 wins + 1 second | Replace "all 13" with "12 of 13" | No |
| P0.3-c | All mean ranks, Holm p-values, ablation W/L/T, factorial stats **verified exact**. | No issue | `[RAW]` | None | No |
| P0.4-a | "500/24 ≈ 21 generations" and "~10 pulls per arm" — loop is **steady-state**, one bandit decision per child. Measured **~450–486 iterations, ~225 pulls/arm**. | **Major** (code contradiction) | `[INSTR]` | Rewrite §5.4 budget arithmetic to measured counts | No — instrumentation done |
| P0.4-b | JADE F/CR from **fixed means 0.5, no success-history update** in code. §3.3 "success-history parameter control" and §5.4 "adaptation warm-up" are unsupported. | **Major** (code contradiction) | `[CODE]` `ifpoax.py:194-195,359-361`; grep: means never written | Rewrite §3.3 & §5.4 JADE mechanism | No |
| P0.4-c | Bandit ≈ uniform is supported by measured **~50/50 split**, not by "too few pulls". | Major (part of P0.4-a) | `[INSTR]` selG≈selL (e.g. 230/230) | Use the 50/50 split as the evidence | No |
| P0.4-d | "p-best from Pareto front-1" is **degenerate** in single-objective mode (both objectives equal → front = whole archive), so p-best ≈ random 20% of archive. | Moderate | `[CODE]` `ifpoax.py:364-380`, `benchmark_tester.py:297-306` | Clarify in §3.3 | No |
| P0.4-e | **Bonus:** OBL opposite accepted **0/485 on F8** vs ~300/450 centred — direct mechanistic support for the thesis. | Positive | `[INSTR]` | Optionally add one sentence to §5.7.5 | No |

---

## 3. P1 FINDINGS TABLE

| ID | Current wording / problem | Why problematic | Exact replacement |
|----|---------------------------|-----------------|-------------------|
| P1.1 | §4.4 "This choice avoids the common criticism that a proposed method is compared against under-tuned or over-tuned baselines." | Implies defaults *guarantee* fairness; ignores that IFPOA-X's own constants (`bandit_c=1.4`, `obl_frequency=3`, …) reflect prior design effort the baselines did not receive. | "Using each library's published defaults avoids selective post-hoc tuning of individual baselines. It does not, however, eliminate the possibility that algorithm-specific calibration would improve their performance, nor does it make the comparison perfectly symmetric: IFPOA-X's own constants reflect design effort during its development that the untuned baselines did not receive. The comparison should therefore be read as *out-of-the-box baselines against a purpose-built hybrid under a fixed budget*, and the reported margins interpreted with that asymmetry in mind." |
| P1.2-a | §3.3 "a JADE-style adaptive local search with **success-history parameter control**"; "drawn per-iteration from **success-history means, as in the original JADE**". | **Code contradiction:** F~Cauchy(0.5,0.1), CR~N(0.5,0.1) with **fixed** means; no μ_F/μ_CR update exists. | "a **JADE-style** current-to-*p*best/1 local operator with an external archive of displaced solutions. Unlike full JADE, the mutation and crossover factors are sampled from **fixed** distributions, F ∼ Cauchy(0.5, 0.1) and CR ∼ 𝒩(0.5, 0.1); the success-history adaptation of μ_F/μ_CR from JADE is **not** enabled in this instantiation. We therefore describe the operator as *JADE-style* rather than as a full JADE implementation." |
| P1.2-b | §3.3 "top `jade_p`=20% of the current **Pareto front-1** in the archive". | In single-objective mode the two objectives are identical, so the front is degenerate (whole archive); p-best is effectively a random 20% of the archive. | "top `jade_p` = 20% of the archive (in the single-objective instantiation used here the two internal objectives coincide, so this reduces to a random 20% subset of the current archive)". |
| P1.3 | §5.7 heading "four **independent** controls". | Three controls are built from the same classical suite → not statistically independent (the body already admits this). | Heading → "four **complementary** controls". Ensure Abstract already says "complementary" (it does) and Conclusion matches. |
| P1.4 | §5.5 "The advantage of IFPOA-X is **preserved as dimensionality grows**"; "sample-efficiency mechanisms … do not degrade at higher dimensions". | Two dimensions (30, 50) cannot support a general scalability claim; shifted controls were not run at D=50. | "The **classical-suite ranking pattern remains stable between D = 30 and D = 50** (IFPOA-X mean rank 1.31 at both, with GWO/WOA/PSO forming the second tier). We do not test beyond D = 50 and did not run the origin-bias controls at D = 50, so this stability is a statement about the two tested dimensions on the centred suite, not a general scalability claim." |
| P1.5 | §5.4 "paired Wilcoxon … with **full statistical power**"; §6 "A **full-power** ablation". | No formal power analysis was performed; "power" is a technical term. | §5.4 → "an **expanded 20-run paired** ablation across all 13 functions (rather than the smaller pilot), which enables a paired Wilcoxon signed-rank test at each function". §6 → "An **expanded 20-run paired ablation across all 13 functions**". |
| P1.6 | §3 opening "IFPOA-X extends the standard FPA by replacing its static, stochastic search policy with three adaptive mechanisms". | Does not state that FPA's local (self-pollination) operator is entirely replaced; a reviewer may dispute the "FPA" label. | Append: "Concretely, IFPOA-X retains FPA's Lévy-flight global-pollination operator as its global move but **replaces FPA's local self-pollination operator entirely** with the JADE-style operator of §3.3 and its fixed switch probability with the UCB1 selector of §3.1; it is thus best understood as an **FPA-backbone hybrid** used here as an experimental vehicle, not a minimal FPA variant." |

---

## 4. STATISTICAL CORRECTION PACKAGE (P0.1)

**Test selection.** Per-function comparison of two algorithms over 20 runs:
- **IFPOA-X vs FPA, IFPOA-X vs PSO:** runs share seed → the harness reseeds `random`/`numpy` before each run (`run_benchmark.py:62-63`) → identical Latin-Hypercube initial population (common random numbers). Paired **Wilcoxon signed-rank** is *defensible*.
- **IFPOA-X vs DE / L-SHADE / GWO / WOA / TPE:** mealpy/optuna use their own internal RNG (seeded by the same integer but a different stream) and **uniform** (not LHS) initialization; runs are **not matched**. Use **Mann-Whitney U** (Wilcoxon rank-sum, independent samples).
- **Ablation (full vs no-OBL/no-JADE/no-Bandit/base) and the OBL×geometry factorial:** all within IFPOA-X through the same harness and seed scheme → matched initial population → paired **signed-rank** is correct (keep as is).
- **F7 caveat:** F7's per-evaluation noise is drawn from the global `np.random` stream and is *not* matched across algorithms (or across ablation variants after the first divergence); note this where F7 is discussed.

**Assumptions.** Mann-Whitney U assumes independent samples and (for a location interpretation) similar-shape distributions; it makes no pairing assumption, which is the correct model for the unmatched families. Effect sizes (Vargha–Delaney A₁₂) are already computed the independent-sample way in `stats_advanced.py:_a12` and need no change.

**Executable recomputation (uses committed raw data; standardises inter-algorithm per-function tests on Mann-Whitney U):**
```python
import pandas as pd, numpy as np
from scipy import stats
PROP="IFPOA-X"
def wlt_mwu(path):
    df=pd.read_csv(path); funcs=list(dict.fromkeys(df.Function))
    bl=[a for a in dict.fromkeys(df.Algorithm) if a!=PROP]; rec={b:[0,0,0] for b in bl}
    for f in funcs:
        d1=df[(df.Function==f)&(df.Algorithm==PROP)]["Best"].values
        for b in bl:
            d2=df[(df.Function==f)&(df.Algorithm==b)]["Best"].values
            try: _,p=stats.mannwhitneyu(d1,d2,alternative="two-sided")
            except ValueError: p=1.0
            better=np.median(d1)<np.median(d2)
            rec[b][0 if(p<0.05 and better) else 1 if(p<0.05) else 2]+=1
    return rec
for name,p in [("classical","results/raw_D30.csv"),
               ("shifted","results_shifted/raw_D30.csv"),
               ("cec","results_cec/raw_D30.csv")]:
    print(name, wlt_mwu(p))
```

**Corrected results (Mann-Whitney U) — cells that differ from the current signed-rank tables are marked ⚠:**

*Classical D30 (Supp. Table S3):* FPA 13/0/0 · **PSO 12/0/1 ⚠** (was 12/1/0) · DE 12/1/0 · L-SHADE 13/0/0 · GWO 13/0/0 · WOA 12/1/0 · TPE 12/1/0. IFPOA-X still wins ≥12/13 vs every baseline — **conclusion unchanged**.

*Shifted D30 (Table 6):* **FPA 7/0/6 ⚠** (8/0/5) · **PSO 2/8/3 ⚠** (2/10/1) · **DE 7/3/3 ⚠** (8/3/2) · L-SHADE 0/11/2 · GWO 1/12/0 · WOA 0/12/1 · TPE 1/5/7. The collapse (heavy losses to L-SHADE/GWO/WOA) is **unchanged**.

*CEC D30 (Table 7):* FPA 7/2/1 · PSO 0/9/1 · DE 2/2/6 · L-SHADE 1/8/1 · GWO 0/9/1 · WOA 8/1/1 · TPE 0/5/5 — **already matches MWU** (the current Table 7 was evidently computed with a different tie-handling than the classical/shifted tables; standardising removes that inconsistency).

**Changed conclusions:** none. **Manuscript locations affected:** §4.5 (name the two tests and the pairing justification), §5.2, Table 6, Table 7, Supp. Table S3, and the one-line method note in §5.7. Effect sizes, Friedman ranks, Holm p-values, ablation, and factorial are **unaffected** (they never used the per-function signed-rank pairing).

---

## 5. SHIFTED-FUNCTION VALIDATION PACKAGE (P0.2)

**Mathematical verification.** For every function `g(x)=f(x−s)` with `s=o−x₀`: argmin g = x₀+s = o and min g = min f = 0. `[MATH]` Verified for all 13 in `verify_shift.py` (translation-invariance) and reproduced here at the run level.

**Non-negativity, per function `[MATH]`:** F1–F7, F9–F13 are non-negative on all of ℝᴰ (sums of squares / absolute values / penalty terms, all ≥ 0). **F8 is the sole exception:** `f8(x)=418.98·D − Σᵢ xᵢ·sin(√|xᵢ|)`; since `xᵢ·sin(√|xᵢ|)` grows unboundedly, f8 is **unbounded below** outside [−500,500]ᴰ (e.g. a coordinate near 713 gives sin(√x)≈1 ⇒ term ≈713 > 418.98 ⇒ negative contribution). So "every F1–F13 non-negative on all of ℝᴰ" is false.

**Per-function validation table (D=30, run-level, from raw results):**

| Fn | Native x₀ | Pure translation? | Domain of `x−s` can exit box? | Min preserved (g(o)=0)? | Empirical negative fitness in any control? | Code↔manuscript consistent? |
|----|-----------|-------------------|-------------------------------|--------------------------|--------------------------------------------|------------------------------|
| F1 | 0 | yes | n/a (non-neg on ℝᴰ) | yes | no | yes |
| F2 | 0 | yes | n/a | yes | no | yes |
| F3 | 0 | yes | n/a | yes | no | yes |
| F4 | 0 | yes | n/a | yes | no | yes |
| F5 | 1 | yes | n/a | yes (0.0e0) | no | yes |
| F6 | 0 | yes | n/a | yes | no | yes |
| F7 | 0 | yes (+ noise) | n/a | ~noise floor | no | yes |
| **F8** | 420.97 | **Control1/far: yes; mixed: clipped** | **yes (only F8)** | yes (8e-9) | **only pre-fix mixed: 49/120; clean after fix** | **needs the §5.7.1 & §5.7.3 fixes** |
| F9 | 0 | yes | n/a | yes | no | yes |
| F10 | 0 | yes | n/a | yes (4e-16) | no | yes |
| F11 | 0 | yes | n/a | yes | no | yes |
| F12 | −1 | yes | n/a | yes (4e-32) | no | yes |
| F13 | 1 | yes | n/a | yes (1e-32) | no | yes |

**Unit-test (run-level non-negativity — the operative safeguard, stronger than `verify_shift.py`'s 2000-point sample):**
```python
import pandas as pd
for tag,p in [("Control1","results_shifted/raw_D30.csv"),
              ("far","results_shift_multi/far/raw_D30.csv"),
              ("mixed_full","results_shift_multi/mixed_full/raw_D30.csv")]:
    f8=pd.read_csv(p).query("Function=='F8'")
    assert (f8.Best>=-1e-6).all(), f"{tag}: negative F8 present"
    print(tag,"F8 min =",f8.Best.min())   # +784, +5907, +6131 respectively
```

**Specific F8 verdict.** **Keep F8, no exclusion, no rerun.** The domain-safe construction is correct and the merged dataset is clean. Two disclosures are required: (i) fix the false blanket non-negativity sentence; (ii) state that the domain-safe F8 is a **clipped** landscape (a plateau outside the validity box), applied identically to all algorithms so it does not bias the *inter-algorithm* comparison, but it does mean the mixed-config F8 is no longer a pure translation.

**Corrected manuscript text — see §7 (patches for §5.7.1 and §5.7.3).**

---

## 6. UCB1 / JADE IMPLEMENTATION AUDIT (P0.4)

**Actual control flow `[CODE]` (`ifpoax.py:879-1103`).** The main loop is **steady-state**, not generational. Each iteration: pick one candidate → (re)evaluate parent (usually a **cache hit** on continuous functions, 0 real evals) → maybe one OBL opposite eval → **one bandit `_bandit_select`** → generate one child (Lévy *or* JADE) → evaluate child (1 real eval) → parent/child selection → **one `_bandit_update`**. So there is **exactly one bandit decision per child**, and the number of bandit decisions ≈ number of loop iterations.

**Measured counts `[INSTR]` (D=30, budget=500, seed=0; monkey-patched counters):**

| Function | Loop iterations (= bandit decisions) | Global-arm pulls | Local-arm (JADE) pulls | OBL applied | OBL **accepted** | Final archive |
|----------|-------------------------------------:|-----------------:|-----------------------:|------------:|-----------------:|--------------:|
| F1 | 460 | 230 | 230 | 459 | **302** | 6 |
| F5 | 454 | 227 | 227 | 453 | 308 | 2 |
| **F8** | 486 | 243 | 243 | 485 | **0** | 2 |
| F9 | 440 | 220 | 220 | 439 | 305 | 1 |
| F10 | 450 | 225 | 225 | 449 | 357 | 16 |
| F13 | 447 | 223 | 224 | 446 | 281 | 4 |

**Discrepancies with the manuscript:**
1. "500/24 ≈ **21 generations**" → the loop is not generational; there are **~440–486 iterations**. `[INSTR]`
2. "each arm accrues **O(10) pulls**" → **~225 pulls per arm** (≈22× higher). `[INSTR]`
3. "confidence radius never contracts" → with N_a ≈ 225 and t ≈ 450, `c·√(ln t / N_a) = 1.4·√(6.1/225) ≈ 0.23`. It *does* contract; the arms stay ~50/50 because the **reward signal (normalized HV gain) is too small/similar to separate them**, which the measured 50/50 split shows directly. `[INSTR]`
4. JADE "**F/CR self-adaptation needs to warm up**" / "the success archive never reaches a size at which its adapted F/CR distributions concentrate" → **there is no F/CR adaptation**: `jade_fmean=jade_cmean=0.5` are constants, sampled every call and **never updated** (`ifpoax.py:194-195,359-361`; no μ_F/μ_CR writer exists). `[CODE]` The stated mechanism cannot be the reason JADE hurts.

**Revised explanation (supported by code + data).** Replace the "budget arithmetic" with: the bandit makes ~450 decisions per run (~225 per arm) yet its two arms receive **near-identical, very small reward signals** (normalized hypervolume gains), so even after ~225 pulls each the estimated arm means stay inside the UCB confidence band and selection remains ≈ 50/50 — statistically indistinguishable from the uniform selector it is compared against (matching the 12/13 ablation ties). The JADE-style local operator uses **fixed** F/CR (no success-history adaptation), so its current-to-*p*best/1 steps — drawn against a degenerate single-objective *p*-best set — perturb the Lévy trajectory that OBL is already steering productively; removing it improves results on 11/13 functions. Both failures are therefore about **operator interaction under a tight budget with an ineffective reward/parameter signal**, not about "too few generations to warm up".

**Bonus (add to §5.7.5).** The OBL opposite is accepted **0/485 times on F8** (off-centre optimum) versus ~300/450 on the centred functions — a direct, within-run mechanistic confirmation that OBL's benefit is contingent on origin-centred geometry.

**Required instrumentation:** already performed (counters above). The one quantity **not** extracted is a μ_F/μ_CR trajectory — but since the code has no adaptation, that trajectory is constant by construction, so no further run is needed; the §5.4 claim simply must be corrected rather than substantiated.

---

## 7. READY-TO-PASTE MANUSCRIPT PATCHES

> Replace the indicated passages verbatim. American spelling retained. No result number is changed except the two overclaims (11/13, 12/13) which are corrected to match raw data.

### §3.1 (add one sentence at the end of the UCB1 paragraph, after "…ties are broken in favour of the less-selected arm.")
> In the single-objective instantiation of this paper the selector is invoked **once per generated child** within a steady-state loop (not once per generation); at a 500-evaluation budget this yields on the order of a few hundred operator decisions per run (§5.4).

### §3.3 (replace the whole paragraph)
> When the bandit selects the local arm, IFPOA-X applies a **current-to-*p*best/1** mutation with an external archive, following the structure of JADE [18]:
> [keep the existing displayed equation unchanged]
> clipped to [0,1] after each coordinate update. Unlike full JADE, the mutation and crossover factors are sampled from **fixed** distributions, F ∼ Cauchy(μ_F = 0.5, 0.1) and CR ∼ 𝒩(μ_CR = 0.5, 0.1) (`jade_fmean`, `jade_cmean`); the success-history adaptation of μ_F and μ_CR that defines full JADE is **not** enabled in this instantiation, which is why we describe the operator as *JADE-style* rather than as a complete JADE. The "*p*-best" vector u^pbest is drawn from the top `jade_p` = 20% of the current archive (in the single-objective setting used here the two internal objectives coincide, so this reduces to a random 20% subset of the archive); the difference vectors u^{r₁}, u^{r₂} are sampled without replacement from the union of the current population and an **external archive** of up to `jade_arch_max` = 128 previously displaced solutions, exactly as in standard JADE.

### §3 opening (append to the first paragraph of Section 3, after the sentence introducing the three mechanisms)
> Concretely, IFPOA-X retains FPA's Lévy-flight global-pollination operator as its global move but **replaces FPA's local self-pollination operator entirely** with the JADE-style operator of §3.3, and replaces FPA's fixed switch probability with the UCB1 selector of §3.1. It is therefore best understood as an **FPA-backbone hybrid** used as an experimental vehicle, not a minimal FPA variant.

### §4.4 "Baseline honesty" (replace the sentence beginning "This choice avoids…")
> Using each library's published defaults avoids selective post-hoc tuning of individual baselines. It does not, however, eliminate the possibility that algorithm-specific calibration would improve their performance, nor does it make the comparison perfectly symmetric: IFPOA-X's own constants reflect design effort during its development that the untuned baselines did not receive. The comparison should therefore be read as *out-of-the-box baselines against a purpose-built hybrid under a fixed budget*, and the reported margins interpreted with that asymmetry in mind (revisited in §5.6).

### §4.5 (replace the sentence defining the per-function test)
> *Per-function* significance uses a two-sample test on the 20 runs of a single function (IFPOA-X vs. each baseline, α = 0.05). Because IFPOA-X, FPA, and PSO run through a shared harness that fixes a common Latin-Hypercube initial population per seed, IFPOA-X-vs-FPA and IFPOA-X-vs-PSO are matched (common random numbers) and use the Wilcoxon **signed-rank** test; the `mealpy`/`optuna` baselines use independent initialization and random streams, so IFPOA-X-vs-{DE, L-SHADE, GWO, WOA, TPE} are treated as independent samples and use the **Mann-Whitney U** (rank-sum) test. The within-IFPOA-X ablation and the OBL×geometry factorial (§5.4, §5.7.5) are matched by construction and use the paired signed-rank test throughout. F7's additive noise is not matched across algorithms and its per-function result is read with that caveat.

### §5.4 (replace the paragraph "**Why the adaptive components fail at this budget: a quantitative account.**")
> **Why the adaptive components fail at this budget: a mechanism-level account.** Both failures are consistent with the algorithm's measured behaviour at 500 evaluations. (i) *Bandit.* The operator selector is invoked once per generated child in a steady-state loop; instrumentation shows roughly 440–490 such decisions per run, split almost exactly evenly between the global and local arms (for example 230/230 on F1, 243/243 on F8). Despite this, the two arms receive near-identical and very small reward signals (normalized hypervolume gains), so their estimated means stay within the UCB1 confidence band and selection remains close to 50/50 — statistically indistinguishable from the uniform 50/50 selector it is compared against, exactly the 12/13 ties observed. The bandit is not broken; its reward signal is too weak and too similar across arms to drive exploitation within the budget. (ii) *JADE-style local search.* This operator uses fixed F and CR distributions rather than JADE's success-history adaptation (§3.3), so its behaviour does not "warm up"; instead, its current-to-*p*best/1 steps — drawn against a degenerate single-objective *p*-best set — perturb the Lévy-flight trajectory that OBL has already begun to steer productively, which is why removing it *improves* results on 11 of 13 functions rather than merely leaving them unchanged. The lesson is not that these mechanisms have "too few generations"; it is that, under a tight budget, an operator-selection reward that cannot separate the arms and a non-adaptive local operator that interferes with the dominant OBL signal earn their keep on neither count.

### §5.7 heading
> #### 5.7 Origin-bias audit: four **complementary** controls

### §5.7.1 (replace the sentence in **Construction** beginning "Because every $F_1$–$F_{13}$ function is non-negative…")
> Because F1–F7 and F9–F13 are non-negative on all of ℝᴰ with minimum 0, translation cannot introduce a spurious lower minimum for those twelve functions; F8 (Schwefel 2.26) is non-negative only inside its canonical box [−500, 500]ᴰ and is treated separately in the signed "mixed" control (§5.7.3). We verify g(o)=0 numerically for every function, including the non-origin cases Rosenbrock (F5) and the penalized F12/F13, in `verify_shift.py`, and confirm at the run level that no evaluation produced a negative fitness in Control 1 or "far" (Supplementary Table S4 lists each function's native optimum, target, and verified residual).

### §5.7.1 (replace the sentence in **Result** beginning "WOA … wins all 13 of 13…")
> At D = 30, 20 runs per (function, algorithm), the ranking inverts. WOA, an algorithm with no centre-reflection mechanism, attains the best mean value on **11 of the 13 shifted functions** (with GWO best on the remaining two) and the best mean Friedman rank (1.46), followed by GWO (2.23). **IFPOA-X falls from rank 1 (1.31) on the classical suite to rank 6 of 8 (5.77)** on the shifted suite (Friedman χ² = 60.90, p = 1.0×10⁻¹⁰, CD = 2.91), behind WOA, GWO, L-SHADE, PSO, and TPE, and statistically indistinguishable from DE by the Nemenyi test.

### §5.7.3 (replace the sentence "We therefore give F8 … the domain-safe shifted form…")
> We therefore give F8 (and only F8, the other twelve functions being non-negative on all of ℝᴰ) the domain-safe form g(x) = f₈(clip(x − o, −500, 500)), which clamps every evaluation into the validity box while keeping the off-centre optimum at the same target o. This clamping is not a pure translation: outside the box the objective is constant along the clamped coordinates, so F8's mixed-config landscape carries a boundary plateau. Because the identical construction is applied to all eight algorithms it does not bias the inter-algorithm comparison, and we verified numerically that the domain-safe F8 yields the correct optimum value (g(o) = 8×10⁻⁹) and no negative fitness across all runs; all 13 functions are analysed for the mixed configuration with **no post-hoc exclusion**.

### §5.7.3 (replace the sentence "…5.31 of 8 ('mixed', winner GWO at 1.08; GWO wins all 13 functions outright…")
> …5.31 of 8 ("mixed", winner GWO at 1.08; GWO attains the best mean value on **12 of the 13 functions**, including the domain-safe F8, with DE best on the remaining one).

### §5.7.5 (append one sentence after the F8 observation "…exactly the point predicted by the central-symmetry account of §3.2.")
> Instrumentation of the run itself corroborates this at the operator level: the OBL opposite is accepted on none of ~485 triggers on F8 (off-centre optimum) but on roughly two-thirds of triggers on the centred functions, so the operator's contribution literally vanishes precisely where the symmetry that makes an elite's reflection a high-quality point is absent.

### §5.5 (replace the first and last sentences per P1.4)
> The classical-suite ranking pattern remains stable between D = 30 and D = 50: IFPOA-X's mean Friedman rank is **1.31 at both dimensions**, with WOA/GWO/PSO forming the second tier and TPE last. […] We do not test beyond D = 50, and the origin-bias controls (§5.7) were not run at D = 50, so this is a statement of ranking stability across the two tested dimensions on the centred suite rather than a general scalability claim (see §5.6).

### §6 Conclusion (replace "A full-power ablation, 20 paired runs across all 13 functions,")
> An expanded 20-run paired ablation across all 13 functions

### §6 Conclusion (add, after the sentence attributing the advantage to OBL)
> We also correct, relative to earlier framing, the mechanism by which the two other components fail: the operator-selection bandit is invoked several hundred times per run but its arms receive near-identical reward, and the local operator uses fixed (non-adaptive) mutation parameters; neither is limited by "too few generations".

---

## 8. CHANGE LOG

| Section | Old issue | Revision made | Evidence |
|---------|-----------|---------------|----------|
| §3 open | FPA identity not qualified | Added "replaces FPA local operator entirely; FPA-backbone hybrid" | `[CODE]` P1.6 |
| §3.1 | Bandit call frequency unstated | Added "once per child, steady-state, few-hundred decisions" | `[INSTR]` P0.4-a |
| §3.3 | "success-history parameter control"; "Pareto front-1" | Rewrote to fixed F/CR (no adaptation), degenerate front → random 20% | `[CODE]` P0.4-b,d / P1.2 |
| §4.4 | Defaults imply fairness | Neutral rewording, discloses design-effort asymmetry | `[CODE]` P1.1 |
| §4.5 | Per-function pairing invalid for external baselines | Split: signed-rank (FPA/PSO, CRN) + Mann-Whitney U (5 externals); F7 caveat | `[CODE][RAW]` P0.1 |
| §5.4 | "~21 generations, ~10 pulls/arm", JADE warm-up | Rewrote to measured ~450 iters/~225 pulls, 50/50 split, fixed-F/CR mechanism | `[INSTR][CODE]` P0.4 |
| §5.5 | Over-broad scalability claim | Limited to "ranking stable across D=30/50 on centred suite" | `[RAW]` P1.4 |
| §5.7 heading | "independent" controls | "complementary" | P1.3 |
| §5.7.1 | False blanket non-negativity; "WOA wins all 13" | Carve out F8; "11 of 13" | `[MATH][RAW]` P0.2-a, P0.3-a |
| §5.7.3 | Clip not disclosed; "GWO wins all 13" | Disclose plateau; "12 of 13" | `[CODE][RAW]` P0.2-c, P0.3-b |
| §5.7.5 | Mechanistic OBL/F8 evidence unreported | Added 0/485-vs-~2/3 acceptance sentence | `[INSTR]` P0.4-e |
| §6 | "full-power ablation"; residual bandit/JADE framing | "expanded 20-run paired"; corrected mechanism note | P1.5, P0.4 |
| Tables 6, 7, S3 | Signed-rank cells for external baselines | Recompute as Mann-Whitney U (few tie-boundary cells shift ±1) | `[RAW]` P0.1 |

---

## 9. FINAL CHECKLIST

| Item | Status |
|------|--------|
| Shift transform math (all 13, optimum preserved) | **Resolved** — verified `[MATH][RAW]` |
| F8 non-negativity blanket statement | **Resolved via text** (patch §5.7.1) |
| F8 negatives corrupting results | **Resolved** — none in Control1/far; pre-fix mixed only; post-fix clean `[RAW]` |
| Domain-safe F8 plateau disclosure | **Resolved via text** (patch §5.7.3) |
| "WOA/GWO wins all 13" | **Resolved via text** → 11/13, 12/13 `[RAW]` |
| Mean ranks, Holm p, ablation, factorial | **Resolved** — verified exact `[RAW]` |
| Per-function test validity | **Requires recomputation** — MWU tables in §4 (from committed raw data; no rerun) |
| UCB1/JADE quantitative explanation | **Resolved via instrumentation + text** `[INSTR][CODE]` |
| JADE "success-history adaptation" claim | **Requires code inspection** — done: no adaptation exists; text corrected `[CODE]` |
| Bandit pulls-per-arm claim | **Resolved** — measured ~225/arm `[INSTR]` |
| P1.1–P1.6 wording | **Resolved via text** (patches in §7) |
| μ_F/μ_CR trajectory | **Cannot vary** — constants by construction; no run needed `[CODE]` |
| Central conclusions (OBL drives advantage; geometry-dependent; factorial causal) | **Intact — verified from raw data** |

---

## DECISION

**(1) Safe after textual/statistical corrections.**

**Rationale (specific, not generic):** Every headline result was regenerated from the committed raw data and matched exactly — classical rank 1.31, Holm p = 0.061 for GWO/WOA, ablation 12/11/12, and the §5.7.5 factorial (W = 1.0, p = 4.88×10⁻⁴, Δ_shifted ∈ [−0.28, +0.09], F8 Δ ≈ 0). The origin-bias fix is sound: F8 negatives exist only in the pre-fix mixed run and are absent everywhere in the final dataset. The two Major issues are **code-vs-manuscript contradictions in the *explanation* of secondary components** (the bandit's pull count and JADE's non-existent adaptation), not in the results — the ablation still shows, from raw data, that OBL drives the advantage, the bandit does not, and JADE hurts. The paired-test issue changes the *label* of a test and a few tie-boundary cells, not a single conclusion. Therefore no experiment needs re-running; the required diagnostics (P0.4 instrumentation) are already complete. The corrections are mandatory for honesty and rigor, but the paper's spine — *a purpose-built OBL hybrid's low-budget advantage collapses under origin-bias controls, and a within-implementation factorial pins the cause on OBL's centre-reflection* — stands unchanged and, after the JADE/bandit explanation is corrected to match the code, is told more accurately than before.
