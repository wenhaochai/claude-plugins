# Consistency Audit — rationale

## Why this exists

An autoresearch pipeline (or rushed human) writes the abstract, the tables, the
method section, and the appendix in separate passes and never reconciles them. The
result is a paper that disagrees with **itself**:

- abstract quotes 85.3% accuracy; the best row of its own Table 2 is 84.7%;
- "improves by 16%" when 73.1 → 78.0 is +6.7% relative / +4.9 points;
- "mean over 5 seeds" where the number is the single best seed, and N=3 in the table;
- method section says "no test-time labels"; the experimental-setup paragraph loads
  gold labels for calibration;
- "comprehensive evaluation across diverse benchmarks" on two datasets, one domain.

None of this needs the code, the data, or a single external fact to detect — only
the paper, read against itself. That is why this skill is the flagship and the only
auditor that always runs: it **runs at L0** (no external GT), the level at which we
have the least to work with — though L0/PDF-text recall is bounded by what the
extractor recovers (number/scope spans only); the richer table/caption checks need
the L1 LaTeX ledger.
