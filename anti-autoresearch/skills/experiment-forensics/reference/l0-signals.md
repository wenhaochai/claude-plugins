# Experiment Forensics — L0/L1 could-not-verify signals

## Contents

- Step 2 signal script
- Example L0 signal

## Step 2 signal script

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; TARGET="$ARGUMENTS"
python3 - "$TARGET" <<'PY'
import json, re, sys
t = sys.argv[1]
claims = json.load(open(f"{t}/claims.json"))["claims"]
out, n = [], 1
def add(pat, title, desc, ev, act):
    global n
    out.append({"finding_id": f"EF{n:03d}", "skill": "experiment-forensics",
                "pattern_id": pat, "title": title, "description": desc,
                "severity": "info", "observability_level_required": 2,
                "evidence": ev, "verdict_local": "needs_external_check",
                "requires_external_check": True, "false_positive_risk": "high",
                "recommended_reviewer_action": act}); n += 1
def anc(c): return [{"claim_id": c["claim_id"], "span": c["text_span"], "location": c.get("location", {})}]

GT   = re.compile(r"reference|ground.?truth|\bgt\b|gold|agreement|target", re.I)
SCOPE= re.compile(r"comprehensive|extensive|robust|general|thorough|state[- ]of[- ]the[- ]art|\bSOTA\b", re.I)
nums = [c for c in claims if c.get("type") in ("number", "comparison")]

for c in nums:                                   # GT-provenance pointer
    if GT.search(c.get("text_span", "")):
        add("HP-FAKE-GT", "Ground-truth provenance not verifiable without the repo (L0 could-not-check)",
            "This number is reported against a 'reference/target/GT'. At this level it cannot be determined whether that reference is dataset-provided or derived from model outputs. NOT an allegation — verifiable only at L2 (eval code + result files).",
            anc(c), "Request the eval code + result files; verify GT provenance at L2 (HP-FAKE-GT).")
for c in nums:                                   # near-ceiling -> normalization pointer
    v = (c.get("value") or {}).get("normalized")
    if isinstance(v, (int, float)) and ((0.99 <= v <= 1.0) or (99.0 <= v <= 100.0)):
        add("HP-SELF-NORM", "Near-perfect score — normalization not verifiable from text",
            "A near-ceiling score with no raw value shown cannot be checked for self-normalization from a PDF.",
            anc(c), "At L2, check whether the metric is divided by the model's own output statistics (HP-SELF-NORM).")
for c in claims:                                 # verified-run-count pointer (defer text scope to consistency-audit)
    if SCOPE.search(c.get("text_span", "")):
        add("HP-SCOPE-INFLATE", "Scope language — actual run count not verifiable without the repo",
            "consistency-audit owns the L0 scope-vs-evidence-in-text check; experiment-forensics can only verify how many datasets/seeds/configs ACTUALLY ran at L2.",
            anc(c), "At L2, count the configs/seeds actually executed in the result files vs this wording.")
        break
add("HP-PHANTOM-RESULT", "Result existence not verifiable without backing files",
    "Whether each reported number maps to a real key in a real result file cannot be decided from a PDF.",
    (anc(nums[0]) if nums else []), "At L2, map each headline number to a result-file key (HP-PHANTOM-RESULT).")
add("HP-DEAD-METRIC", "Metric-code liveness not verifiable without the repo",
    "Whether any discussed metric is actually computed/called cannot be decided from a PDF.",
    [], "At L2, confirm each discussed metric is called and appears in a result file (HP-DEAD-METRIC).")
add("HP-PLACEHOLDER-DATA", "Placeholder / fake data in released code not verifiable without the repo",
    "Whether the released code still contains placeholder/dummy/fake data (e.g. a '# fake data for plotting' annotation or a hard-coded random array) feeding a reported figure/number cannot be decided from a PDF — flag the code marker, not who wrote it.",
    (anc(nums[0]) if nums else []), "At L2, grep the code for placeholder/dummy/fake markers and trace whether any reported figure/number is drawn from them (HP-PLACEHOLDER-DATA).")
add("HP-RESULT-ARTIFACT-MISMATCH", "Code-output vs paper-number agreement not verifiable without the repo",
    "Whether the released code / result artifacts actually produce the paper's reported numbers cannot be decided from a PDF. (A code-vs-equation implementation divergence is HP-METHOD-DRIFT, not this.)",
    (anc(nums[0]) if nums else []), "At L2, read the code's computation + result files and check each reported number against the code-produced value (HP-RESULT-ARTIFACT-MISMATCH).")
if nums:                                          # repro-artifact inventory pointer (absence is L0-observable)
    add("HP-MISSING-REPRO-ARTIFACT", "Reproducibility artifacts absent — empirical claims not checkable even in principle (absence noticeable at L0; verdict-bearing only at L2)",
        "This paper reports empirical/number results but the submission ships no eval code and no prompts/configs the results depend on. The ABSENCE is observable now (L0 'stated'); whether the SPECIFIC prompts/configs/hyperparameters its results need are present is verifiable only if a repo is released (L2). NOT a misconduct claim — a reproducibility gap. FP: a genuinely theoretical paper; double-blind submission norms (treat as a camera-ready expectation, lower severity).",
        anc(nums[0]), "Ask for the code + the exact prompts/configs/hyperparameters the reported numbers depend on; at L2 verify they are present and complete (HP-MISSING-REPRO-ARTIFACT).")

json.dump(out, open(f"{t}/experiment-forensics.findings.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"L<2: wrote {len(out)} info 'could-not-verify' signals (severity=info, req:2 — the adjudicator keeps them at info).")
PY
```

## Example L0 signal

```json
{
  "finding_id": "EF001",
  "skill": "experiment-forensics",
  "pattern_id": "HP-FAKE-GT",
  "title": "Ground-truth provenance not verifiable without the repo (L0 could-not-check)",
  "description": "Claim C014 reports agreement against a 'reference'. At L0 (PDF only) it cannot be determined whether that reference is dataset-provided or derived from model outputs. This is NOT an allegation — verifiable only once the eval code + result files are available (L2).",
  "severity": "info",
  "observability_level_required": 2,
  "evidence": [
    {"claim_id": "C014", "span": "98% agreement with the reference",
     "location": {"file": "paper.txt", "section": "experiments"}}
  ],
  "verdict_local": "needs_external_check",
  "requires_external_check": true,
  "false_positive_risk": "high",
  "recommended_reviewer_action": "Request the evaluation code and result files; verify GT provenance at L2. Do not treat as a flag at this observability level."
}
```
