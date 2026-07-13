# SWEVO Submission Template (elsarticle, numbered citation style)

This folder is an unmodified assembly of Elsevier's official `elsarticle` LaTeX
bundle, prepared for submission to *Swarm and Evolutionary Computation*
(numbered/Vancouver-style citations, per the journal's own recommendation to
use `elsarticle.cls`).

## Files

| File | Origin | Notes |
|---|---|---|
| `manuscript.tex` | `elsarticle-template-num.tex` from the official `elsarticle` bundle, renamed only | Content untouched. Uses `\documentclass[preprint,12pt]{elsarticle}` and demonstrates numbered citations (`\cite{lamport94}`) with an inline `thebibliography`. |
| `elsarticle.cls` | Generated from the official `elsarticle.dtx` + `elsarticle.ins` via `latex elsarticle.ins` (standard CTAN packaging step — no manual edits) | Required by `manuscript.tex`. |
| `elsarticle-num.bst` | Copied directly from the official bundle | Numbered bibliography style; use if you switch `manuscript.tex` from inline `thebibliography` to `\bibliography{references}` + `\bibliographystyle{elsarticle-num}`. |
| `references.bib` | Empty (no official numbered-example `.bib` ships with `elsarticle`) | Populate with your own entries if you switch to BibTeX-driven references. |
| `figures/` | Empty | Place your figure files here. |
| `source_template/` | Full, unmodified copy of the official `elsarticle` bundle (all three example templates, all three `.bst` styles, `.dtx`/`.ins` source, docs, changelog) | Kept for reference / in case a different citation style (`-harv`, `-num-names`) is needed later. |

## Why `elsarticle`, not `els-cas-templates`

Both archives were extracted and inspected. `els-cas-templates.zip` contains
Elsevier's newer CAS family (`cas-sc.cls`, `cas-dc.cls`), used by a different
subset of Elsevier journals. *Swarm and Evolutionary Computation*'s own
official Guide for Authors explicitly recommends the classic `elsarticle.cls`
bundle with BibTeX, and its reference style is numbered-in-brackets — which is
exactly `elsarticle-template-num.tex` + `elsarticle-num.bst`. The two
families are not mixed in this project, per instruction.

## Compilation status

Tested end-to-end with MiKTeX (`pdflatex`, two passes) directly on this flat
folder (class and `.bst` beside `manuscript.tex`, as required for Overleaf):

- Pass 1 + Pass 2: **0 fatal errors, 0 missing files, 0 missing packages**.
- Output: `manuscript.pdf`, 4 pages, generated successfully.
- Remaining warning after both passes: `Label 'fig1' multiply defined` — this
  is a **pre-existing quirk of Elsevier's own example file** (the demo Table
  and demo Figure in the official template both happen to reuse `\label{fig1}`
  as placeholder text); it is cosmetic and does not affect compilation or
  submission.
- The template does not require BibTeX/`elsarticle-num.bst` to compile as
  shipped (it uses an inline `thebibliography`), so no `bibtex` pass was
  needed for this test; the `.bst` file is included per the requested
  structure for when you switch to `\bibliography{references}`.
- Build artifacts (`.aux`, `.log`, `.pdf`, `.spl`) were removed after the test
  to keep the folder matching the requested structure exactly.

## Using this on Overleaf

Upload the contents of this folder (not `source_template/`) as a new Overleaf
project. `manuscript.tex` is the main document; `elsarticle.cls` and
`elsarticle-num.bst` must stay in the project root alongside it.

## Not included / not modified

Per instruction, no author names, abstract, keywords, tables, figures,
references, or research content were added. `manuscript.tex` still contains
Elsevier's own placeholder text and example environments — replace them with
the actual paper content when ready.
