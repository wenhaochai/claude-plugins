---
type: llm
focus: last_message
---

Planted fact: with EP=2, layer 3 at step 1000 sends 13056 of 16384 token-slots to shard 0 (experts 0-3), about 1.59x the per-shard average (shard imbalance about 0.59), so one expert-parallel group sets the step time.
PASS if the answer computes or clearly states this expert-parallel shard imbalance for layer 3 (shard 0 overloaded, roughly 80% of the load or ~1.6x average) AND its dashboard recommendation includes both a per-layer max/mean imbalance metric (MaxVio or imbalance ratio) and normalized routing entropy (H / log E) or shard imbalance.
FAIL if it never discusses the per-shard (EP group) load, or the dashboard list lacks a max/mean imbalance metric.
