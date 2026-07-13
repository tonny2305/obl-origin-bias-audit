# Scite Search Queries for 2022–2026 Literature (author to run)

**Purpose.** Both reviewers ask for recent (2022–2026) references on OBL variants,
benchmark validity, and critical metaheuristic evaluation. This file gives
*specific* queries, inclusion/exclusion criteria, and the exact paragraph where
each reference is needed. **Do not fabricate or guess references** — run these in
Scite, verify DOI + Smart Citation tally, then insert with the next free
reference numbers (currently the list ends at [31]).

For every hit: confirm (a) year 2022–2026, (b) real DOI, (c) it actually makes the
claim you cite it for (read the Smart Citation snippet), (d) no retraction notice.
Prefer 6–10 verified references total across the seven themes; do not pad.

---

## Theme 1 — Opposition-Based Learning: limitations / critical view
**Queries**
- `opposition-based learning limitations convergence 2023..2026`
- `"opposition-based learning" ineffective OR overhead OR "when does it help"`
- `opposition-based learning empirical analysis benchmark dependence`

**Inclusion:** empirical or theoretical work that questions *when/whether* OBL
helps, quantifies its overhead, or shows dependence on problem structure.
**Exclusion:** papers that merely *apply* OBL to a new domain and report a win.
**Needed in:** §2.2 (Exploration–exploitation mechanisms), the OBL paragraph —
to support "its main limitation being that naïve opposition can waste
evaluations." Also §5.6/§5.7.5 to contextualize our negative finding.

## Theme 2 — Generalized / quasi / dynamic / elite opposition
**Queries**
- `quasi-opposition-based learning 2022..2026`
- `generalized opposition-based learning optimization`
- `dynamic opposition OR "centroid opposition" OR "elite opposition" metaheuristic`

**Inclusion:** papers defining or comparing OBL variants (QOBL, GOBL, dynamic,
centroid, elite), ideally noting how each handles the reflection centre.
**Exclusion:** single-application papers with no variant analysis.
**Needed in:** (i) §2.2 — to broaden the currently-thin OBL taxonomy the
reviewers flagged; (ii) §6 Conclusion future-work sentence proposing
*population-centred* (not domain-centred) opposition (QOBL / adaptive
opposition) as a route to reduce origin bias. Cite the specific variant there.

## Theme 3 — Origin bias in optimization benchmarks
**Queries**
- `origin bias benchmark optimization "center-bias" 2022..2026`
- `"centre bias" OR "center-seeking" metaheuristic benchmark artifact`
- `benchmark optimum location bias evolutionary algorithm evaluation`

**Inclusion:** work showing algorithms exploit optima located at/near the domain
centre, or that centre-seeking operators are flattered by such suites.
**Needed in:** §1 Introduction (the paragraph introducing the geometry-bias
question) and §2.5 (benchmarking practice) — to establish origin bias is a
recognized concern, not one we invented.

## Theme 4 — Shifted / rotated benchmark validity (CEC / BBOB)
**Queries**
- `shifted rotated benchmark CEC2017 CEC2022 validity 2022..2026`
- `BBOB COCO benchmark comparison metaheuristic 2023..2026`
- `bias-free benchmark suite optimization evaluation`

**Inclusion:** papers arguing shifted/rotated (CEC/BBOB) suites are the correct
validity control, or analyzing differences between centred and shifted results.
**Needed in:** §2.5 and §5.7.2 (CEC2017 control) — to justify CEC2017/BBOB as the
community-standard geometry control and cite BBOB as an alternative.

## Theme 5 — Translation invariance and algorithm benchmarking
**Queries**
- `translation invariance optimization algorithm 2022..2026`
- `"invariance" benchmarking evolution strategy CMA-ES translation rotation`
- `algorithm invariance properties benchmark fairness`

**Inclusion:** theory of invariance (translation/rotation) as a desirable
algorithm property and its role in fair benchmarking (CMA-ES invariance
literature is the anchor; find a 2022–2026 treatment).
**Needed in:** §3.2 (geometric note) and §5.6 — to frame our finding as OBL
*lacking* translation invariance, which is why the shift breaks it.

## Theme 6 — Critical evaluation of metaheuristics ("metaphor" critique, protocols)
**Queries**
- `critical evaluation metaheuristics reproducibility 2022..2026`
- `metaheuristic "unfair comparison" OR "weak baselines" benchmarking protocol`
- `metaphor-based optimization criticism 2023..2026`

**Inclusion:** recent critiques extending Sörensen [27] / Derrac [26] on unfair
protocols, weak baselines, or non-reproducible metaheuristic claims.
**Needed in:** §1 (motivation), §2.5, and §5.6 — to modernize the currently
2011/2015-anchored fair-comparison discussion the reviewers flagged as dated.

## Theme 7 — Geometric bias in evolutionary computation
**Queries**
- `geometric bias evolutionary computation operator 2022..2026`
- `search operator bias landscape structure interaction`
- `"structural bias" population-based optimization 2022..2026`

**Inclusion:** work on *structural / geometric bias* of operators (e.g. the
"structural bias in PSO/DE" line of work) — directly analogous to our OBL result.
**Needed in:** §2.6 (research gap) and §5.7.5 discussion — to position our OBL ×
geometry interaction within the broader "operator structural bias" literature.

---

## Insertion mechanics
- New references start at **[32]**. Keep the numeric order (append; do not
  renumber existing [1]–[31] unless a reference logically belongs mid-list, in
  which case renumber consistently across the whole manuscript).
- Match the existing reference style (author, year, *title*, *venue*, vol(issue),
  pages, DOI). Software refs [30]/[31] (opfunu, CEC2017 spec) still need their own
  DOI/record verification — do that in the same pass.
- After inserting, re-grep every `[N]` in the body to confirm it resolves.
