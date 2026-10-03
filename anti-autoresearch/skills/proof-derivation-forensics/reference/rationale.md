# Rationale

## Contents

- Why this exists

## Why this exists

An autoresearch pipeline (or a rushed human) writes a theorem statement, then a
proof, then an abstract that advertises the theorem — in separate passes, never
reconciled at the level of the *argument*. The result is a proof that does not
establish its own claim:

- "By compactness a maximizer exists" — but compactness of the domain is never shown
  (a missing existence obligation invoked as fact);
- "Lemma 3 follows from Theorem 1," whose proof in turn invokes Lemma 3 (circular);
- "By Jensen, $\mathbb{E}[f(X)] \ge f(\mathbb{E}[X])$" for a **concave** $f$ — the
  inequality runs the wrong way (an invalid step);
- the definition fixes $\le$, but equation (7) and the proof use $\ge$; or `argmin`
  in Def 2 becomes `argmax` in the proof of Thm 4 (a symbol's meaning drifts);
- a concentration bound uses **independence** of the $X_i$, but the theorem only
  assumes they are identically distributed (a stronger assumption smuggled in).

None of this needs the code, the data, or any external fact to detect — only the
proof, read against the obligations its own theorem creates. That is why family G is
**substantive and decided from the written proof (verdict-bearing at L1)**: a senior
area chair reads a proof and decides validity from the page; this tool needs the LaTeX
source (L1) to do it reliably, since PDF-extracted math is unreliable — at an L0 PDF-only
run it surfaces info only. So does this skill — via a cross-model reviewer, with every finding
anchored to a verbatim ledger span and the verdict computed by deterministic code.

**Honest recall bound (read this).** The evidence ledger (`build_claim_ledger.py`)
has **no dedicated theorem/proof/equation extractor**: proof text enters
`claims.json` only as the `number`, `scope`, `citation`, `caption`, and `table_cell`
spans that happen to *overlap* it (a bound with a constant, a "for all / general"
sentence, a `\cite{}` to an imported result, an equation paragraph carrying a
decimal). The reviewer **judges from the full proof source**, but every finding must
**anchor to a ledger claim** whose `text_span` verbatim-contains the failing
fragment. A pure-symbol step covered by no such claim cannot rise above `info` — that
is the honest outcome, not a defect. Recall is materially higher at **L1** (LaTeX:
equation paragraphs and theorem-statement sentences are captured with stable line
numbers) than at **L0** (PDF text). Step 1 pre-computes, per theorem, the exact
**anchor-candidate** `claim_id`s so the reviewer knows where it can and cannot ground
a finding.
