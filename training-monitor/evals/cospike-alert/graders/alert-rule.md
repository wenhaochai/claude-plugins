---
type: llm
focus: last_message
---

PASS if the proposed alert pages on a co-spike, meaning loss AND gradient norm both flagged as spikes on the same step (a gradient-norm-only or loss-only spike may be logged or warned, but not paged), AND the spike test is robust: a rolling median with median absolute deviation (MAD), ideally on log values, or a cutoff explicitly calibrated from healthy-run history.
FAIL if the paging condition is either signal alone, or if the spike test is only a fixed absolute threshold (e.g. grad_norm > 5) or a mean + k*std rule.
