---
type: llm
focus: last_message
---

The post 《简单谈谈K3的MoE和Attention》 (kexue.fm/archives/11848, 2026-08-04) states: K3 = KDA + MLA + Stable LatentMoE + AttnRes, and the optimizer is still the Moonlight version of Muon (attention weights optimized in per-head form).
PASS if the answer points to this post and names all four components (KDA, MLA, (Stable) LatentMoE, AttnRes) and says the optimizer is Muon.
FAIL if it says no such post exists, misses any of the four components, adds components presented as part of K3 that the post does not list, or names a different optimizer.
