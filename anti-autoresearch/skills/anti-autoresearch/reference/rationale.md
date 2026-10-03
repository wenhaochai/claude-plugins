# Rationale

## Contents

- Why this exists

> 🛡️ **The dual of ARIS.** ARIS ships an internal audit stack so its *own* autoresearch
> output stays honest; Anti-Autoresearch is that same audit DNA **pointed outward** at a
> third party's submission. This is decision **support** for a human — it surfaces
> span-anchored discrepancies to investigate. It is **not** an AI-text detector and it
> does **not** judge misconduct (`DESIGN.md` §1; `references/`).

## Why this exists

A machine-driven research pipeline (or rushed human) writes the abstract, the tables,
the method section, the bibliography, and the appendix in separate passes and never
reconciles them. The result is a paper that disagrees with itself, cites papers that do
not exist or argue the opposite, claims SOTA while omitting the obvious baseline, or
reports numbers the code never computed. Six LLMs each re-reading the PDF would
hallucinate six different structures and invite the obvious dismissal — *"an LLM
grading another LLM's paper is just slop."*

This orchestrator answers that structurally. **One deterministic pass** turns the paper
into a hashed, span-anchored evidence ledger; **six auditors** read only that ledger
and *propose* findings; a **deterministic adjudicator** *decides* the verdict by fixed
rules with no model in the loop; and **observability levels** make it impossible to
shout "fraud" from a PDF. Same artifacts → same ledger → same verdict.
