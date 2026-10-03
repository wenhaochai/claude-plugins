# Rationale

## Contents

- Why this exists

> Adapted from ARIS `citation-audit`, re-wired onto this repo's evidence ledger and
> the reviewer≠adjudicator contract, and reframed from "audit + **rewrite** the bib"
> to **"emit ledger-anchored findings, never touch the paper."** Three layers, ported
> verbatim: **existence → metadata → context.** Following the repo's
> `baseline-comparison-audit` pattern, the **executor** gathers the canonical facts
> (DBLP / arXiv / DOI) as neutral evidence; a **fresh cross-model reviewer** judges
> existence + metadata + context over those facts. The reviewer never grades — the
> deterministic adjudicator does.

## Why this exists

An autoresearch pipeline (or a rushed human) generates a bibliography in a separate
pass from the prose and never reconciles the two. The failure modes are **not**
wildly fake entries — those are easy to spot. The dangerous ones are:

- **Hallucinated reference** — no paper exists at the claimed arXiv id / DOI / venue;
  authors, title, or year are fabricated. (`HP-CITE-HALLUC`, critical)
- **Metadata drift** — a real paper cited with the wrong year, wrong venue (the arXiv
  preprint number used after the work appeared at CVPR/ICML/NeurIPS, or vice versa),
  or a v1 title silently merged with a v3 retitle. (`HP-CITE-HALLUC`, major)
- **Wrong-context citation** — a real paper used to support a claim it does **not**
  make, or argues *against* (e.g. citing a self-refinement paper to support
  "self-feedback yields correlated errors" when the cited paper argues the
  opposite). (`HP-CITE-CONTEXT`, major)

None of this needs the code, the data, or a re-run — only the citing sentence (from
the ledger) checked against the cited work's public record (DBLP / arXiv /
publisher). That is why this layer is **L0-decidable** (observability-wise — no repo
or result files needed) and independently defensible. (The citing-sentence *claims* it
anchors to still enter the ledger only via the LaTeX path; a pure PDF-text ledger
yields none — see Step 0.)
