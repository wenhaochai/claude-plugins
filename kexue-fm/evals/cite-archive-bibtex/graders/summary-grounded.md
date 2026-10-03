---
type: llm
focus: last_message
---

The post is 苏剑林《除了交叉熵，LM Loss还有什么选择？》 (2026-08-09). It derives general LM loss constructions from two viewpoints ("learning the distribution" and "allowing sampling"), compares the losses by the gradient and convexity they give with the output activation, and reverses the question to find the matching optimal activation for a given loss: for cross-entropy that activation is Softmax, which explains why the two always come together (Sparsemax / Entmax / Tsallis appear as other cases).
PASS if the summary is about alternatives to cross-entropy as the LM training loss AND states at least two of these specifics: the two derivation viewpoints, the gradient/convexity comparison, the loss-to-optimal-activation reverse derivation, cross-entropy pairing with Softmax, Sparsemax/Entmax/Tsallis.
FAIL if the summary is generic or speculative (for example, guessed from the title only, hedged as "可能讲了"), describes a different paper, or says the content could not be read.
