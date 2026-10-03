# Adjudicator flags and gates

- **`--observability-level "$L"`** is the run level: it auto-demotes any finding whose
  `observability_level_required` exceeds `L` (e.g. an L2 code-fraud pattern on an L0 run
  → `info`, counted under `downgraded_for_observability`).
- The adjudicator **auto-writes level-derived limitations** at L0/L1 (and an anchoring
  note if `--ledger` anchoring ever fails); Step 4 **also always passes an explicit
  `--limitation`** (above), so the report's `limitations` is never empty on this path —
  honesty is part of the contract. Each extra `--limitation` (repeatable) is added
  alongside the auto-written ones. For a byte-reproducible eval run add
  `--generated-at "<fixed ISO8601>"`; omit it normally (a harmless `utcnow`
  DeprecationWarning may print to stderr; exit 0).

It applies, in order (each gate fail-closed and logged per finding): **ANCHOR**
(above-info without a verbatim ledger span → `info`; counted under `unanchored_demoted`) →
**OBSERVABILITY** (`observability_level_required` missing/invalid or > run `L` → `info`;
counted under `downgraded_for_observability`) → **FP-RISK** (`high` caps at `minor`,
`medium` caps at `major`) → **MEMO** (`adversarial-case-builder` + `novelty-duplication-advisory` → `info`) → **SURFACE**
(`presentation-signals` skill OR a `SURFACE_PATTERNS` `pattern_id` → `minor`). Then, over
the **surviving** severities:

```
any surviving critical          → HARD_FLAGS
else any surviving major/minor  → SOFT_FLAGS
else                            → CLEAN_GIVEN_EVIDENCE   (= "nothing checkable at L is broken", NOT "honest")
```
