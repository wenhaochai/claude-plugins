# Novelty & Duplication Advisory — rationale and ARIS lineage

## Lineage: adapted from ARIS `novelty-check`

> Adapted from ARIS `novelty-check`, with **one deliberate reframing and one deliberate
> downgrade.** The reframing: ARIS `novelty-check` asks *"is MY idea novel — should I PROCEED
> / ABANDON?"* and hands the author a `Score: X/10` + a recommendation; this skill asks *"here
> is the overlap a third-party reviewer should weigh"* and hands the human candidates, not a
> verdict. The downgrade: it is **memo-only.** Novelty is the textbook example of a judgment
> that is **not decidable from the paper alone, and not decidable at any observability level**
> — it depends on a corpus you can never prove you searched exhaustively. So this skill
> **retrieves and lays out** overlap; it refuses to grade it. `tools/adjudicate_findings.py`
> lists `novelty-duplication-advisory` in `MEMO_ONLY_SKILLS` and caps anything it emits at
> `info`. The memo *informs*; the human *judges*; the deterministic adjudicator owns the
> report verdict — and this skill never moves it.

## Why this exists

Two complaints recur in real reviews of autoresearch (and rushed human) output, and neither
is an *internal*-consistency failure the other auditors catch — they are *relational* to the
wider literature:

- **"标准的 A + B + C，全是已知模块" / "缝合" (stapling)** — the paper bolts together three
  well-known techniques and presents the bundle as the contribution. Whether that bundle is a
  genuine advance or a trivial staple is a **reviewer judgment** — a surprising combination is
  publishable, an obvious one is not, and no tool can draw that line.
- **"这不就是 X 换了个壳" (repackaged / duplicate submission)** — the submission looks like a
  prior paper (often the authors' own) with a new title. An *exact* title/abstract/DOI match
  is reportable; the **absence** of a match proves nothing, because your search corpus is
  never complete.

Both are listed in `references/hack-pattern-taxonomy.md` (v0.4) under **Advisory signals (NOT
in the 39 · zero verdict weight · reviewer-judgment only)** — `ADV-TRIVIAL-COMBINATION` and
`ADV-DUPLICATE-PUBLICATION`. The taxonomy is explicit: *"Novelty is a reviewer judgment; the
tool can lay out the prior-work overlap, it cannot rule 'trivial'"* and *"the absence of a
match is **not** evidence of originality."*

So this skill does the one honest, high-leverage thing the other auditors do not: it **reaches
outside the paper** to *retrieve* candidate prior work, and **lays it out side-by-side**
against the paper's own contribution so a human can weigh novelty with the overlap in front of
them. It is the only auditor that consults an external corpus — which is exactly why it can
carry **no verdict weight**: the moment a tool grades novelty from an incomplete search, it
manufactures the "AI slop grading AI slop" failure this repo exists to refuse. It is the
literature-facing complement to `citation-forensics`: that skill audits the papers the
submission **does** cite; this one surfaces prior work it may **not** have cited at all.

## Design notes from the core principle

> **Deliberate exception to "the reviewer reads only the ledger."** The other auditors reason
> strictly inside the paper. This one must consult an external corpus, so the executor
> performs the retrieval and hands each reviewer a *structured candidates file* (real records,
> with identifiers) alongside the ledger. That file is retrieval output, **not** a Claude
> opinion or digest of the paper — so the spirit of reviewer-independence (no executor
> judgment leaks into the reviewer prompt) still holds.

> **The anchor is the contribution sentence, not the prior work.** Every surfaced item anchors
> to one of the submission's own **contribution claims** — a `scope` / `method` / `comparison`
> claim, OR (because the deterministic extractor types most abstract/intro contribution
> sentences as `number` / `citation` / `scope`, so the three contribution *types* alone are
> too thin to anchor to on a real ledger) any claim located in the `abstract` / `intro`
> section. The candidate prior work — its title, arXiv id / DOI / DBLP url, overlap kind —
> lives in the memo table and the finding's `description`, **never** as the anchor span: there
> is no ledger claim for an external paper (same shape as `citation-forensics`, where the DBLP
> facts go in `description` and the anchor is the citing sentence).

## Why a standalone run reads CLEAN_GIVEN_EVIDENCE

The adjudicator applies its gates in order (ANCHOR → OBSERVABILITY → FP-RISK → **MEMO** →
SURFACE) and computes `overall_verdict` ∈ {CLEAN_GIVEN_EVIDENCE, SOFT_FLAGS, HARD_FLAGS} from
the **other** auditors' findings. The MEMO gate caps every `novelty-duplication-advisory`
finding at `info`, and this skill is absent from `SKILL_TO_DIMENSION`, so it contributes **no
dimension verdict and cannot move the overall verdict** — by design. A standalone run with no
other findings therefore yields `CLEAN_GIVEN_EVIDENCE`; that is **correct**, not a miss — the
value of this skill is the **memo**; read it. Treat a single-skill report as a PREVIEW.

## Review tracing

Trace policy is **forensic** (never silently skipped) — see **Step 5** for the exact layout:
`run.meta.json` + per-axis `001-duplicate.{request.json,response.md,meta.json}` and
`002-combination.{...}` (and, under `— effort: max`, each combination-component probe). Write
each `.response.md` during Step 3, immediately after its reviewer call. Every `request.json`
must contain only the paths + the ledger + the candidates file + the per-axis checklist that
were sent — the reviewer-independence audit trail. The retrieved `candidates.json` and
`profile.json` are persisted in `PAPER_DIR` and referenced from `run.meta.json` so the
prior-work universe the memo rests on is reproducible.
