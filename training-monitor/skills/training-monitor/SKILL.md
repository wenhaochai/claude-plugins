---
name: training-monitor
description: "Monitoring doctrine for a pretraining run, distilled from Chunyuan Deng, \"Reading a Pretraining Run\" (2026): the nine first-screen signals, the full metric table with cadence and priority (P0 every step, P1 every 100 steps, P2 on demand), the formulas, the cross-rank reduction rules, a robust spike detector, the fixed triage order, and the common mistakes. Use when starting, watching, comparing, or debugging a pretraining or large fine-tuning run, when building a dashboard or an alert set, or when the user asks 训练监控, 这个 run 健康吗, loss spike, 梯度爆炸, MFU 掉了, 专家不均衡, 怎么看训练曲线. Text only: the agent maps each signal onto what its own stack already logs and decides for itself whether a script, a dashboard, or a manual read is warranted."
---

# Training monitor

A pretraining run fails in a small number of ways, and most of them show up in a handful of every-step numbers before the loss curve moves. This skill restates the metric set, the reduction rules, and the triage order from Deng (2026) so that an agent can read a run the same way each time. The source is explicit that "every lab has its own dashboard, so this list is necessarily opinionated"; treat it as a starting point that the run's own healthy history then calibrates.

**Scope.** Language-model pretraining first; the loss, gradient, system, tensor, and evaluation sections also apply to large SFT and RL runs with the obvious substitutions. The expert-balance section applies only to mixture-of-experts models, the modality section only to multimodal models. This skill contains no code: which checks exist, where they run, and whether they become a script is the reading agent's decision, made from the procedure below.

## How to apply this to a project

1. **Inventory before you instrument.** List what the training stack already logs, namely the tracker keys, the stdout lines, and the evaluation outputs. Most stacks already emit the global loss, a global gradient norm, step time, tokens per second, and a held-out loss.
2. **Map the inventory onto the table** in the next section and mark each row as present, derivable, or missing. Derivable rows come from logged quantities without new hooks: co-spike count from the loss and gradient-norm histories, update ratio from update and weight norms when both are logged, tokens per second from token counts and step time, straggler score from per-rank step times.
3. **Fill P0 gaps first** and leave P1 and P2 for when a P0 signal misbehaves. A monitor that is complete but late is worth less than one that is partial and on time.
4. **Set thresholds from healthy runs**, never from one failure. Deng: "Choose thresholds from healthy runs. Do not tune the window length or the $z_t$ cutoff around one failure." Record the chosen thresholds next to the run config so the next run inherits them.
5. **Pick the sampling interval** $K$ from the cost rules in Part V, then measure the overhead on the actual model and hardware before adding anything.
6. **Decide the tooling last.** A check that repeats every run or chains into a gate deserves a script with an exit status. A single investigation deserves a query or a notebook. A short run deserves a person reading the dashboard. The doctrine is the same in all three.
7. **When something looks wrong, walk the triage order** in Part I and stop at the first step that explains the symptom; open per-layer charts only when the walk ends without an explanation.
8. **Compare runs by tokens or FLOPs, not by step**, whenever batch size or sequence length differs between them.

## Priorities and cadence

| Priority | Cadence | Role |
|---|---|---|
| P0 | every step, roughly ten metrics | on-call alerts; each one has a threshold and a response |
| P1 | every 100 steps | diagnostics opened when a P0 signal fires |
| P2 | on demand | "Turn these on for one investigation, such as a closer look at one parameter, expert, or data source." |

Deng's starting point: "compute cheap alerts every step, scan tensors every 100 steps, and evaluate every 0.5–2% of training. If you see a problem, sample more often or replay the step."

## Part I. First screen

"If you make only one dashboard, put these nine signals on it. Record all but the last one every step."

| Area | Signal | Question it answers |
|---|---|---|
| Loss | global and worst-rank mean | Is training improving, and is one worker or shard much worse than the rest? |
| Loss | by source and modality | Is one data source or modality getting worse while the overall loss stays flat? |
| Gradients | global norm and clip rate | Often warns you before the loss does. |
| Stability | co-spike count | Did loss and gradient norm jump on the same step? |
| System | step time and throughput | Shows stalls, replays, slow workers, and communication slowdowns. |
| System | peak memory, max over ranks | Shows how close the fullest GPU is to running out of memory. |
| Experts | expert-load MaxVio | Catches a router sending too many tokens to a few experts. |
| Numerics | absolute max at the output | Catches overflow or bad values before they affect the loss. |
| Quality | held-out loss per byte, every 0.5–2% of training | Shows whether more training is still helping. |

**Triage order.** "When something looks wrong, start here: job state → loss → gradient norm and spikes → step time → memory → expert balance. If those do not explain the problem, open the per-layer charts."

## The full metric table

Priority and cadence are Deng's; the purpose column is his one-line description of what the metric catches.

| Group | Metric | What it catches | Cadence | Priority |
|---|---|---|---|---|
| Loss | global mean $L$ | whether training is improving; the main number for comparing runs | every step | P0 |
| Loss | worst-rank mean $L_{\max}$ | a bad worker or data shard hidden inside $L$ | every step | P0 |
| Loss | by source and modality | a domain or modality regressing under a flat global curve | every 1–10 steps | P0 |
| Gradients | global norm $G_2$ | numerical stability; moves before the loss | every step | P0 |
| Gradients | clip rate | a clip threshold that no longer matches the run | every step | P0 |
| Gradients | co-spike count | loss and gradient norm jumping at the same time | every step | P0 |
| Gradients | robust spike score $z_t$ | spikes, without assuming a Gaussian | every step | P1 |
| Gradients | mean and max $\lvert g\rvert$ | typical scale versus one exploding element | every step | P1 |
| Gradients | zero fraction $Z_g$ | dead paths, underflow, parameters getting no gradient | every step | P1 |
| Gradients | skip and replay counters | steps dropped by the spike guard; nondeterministic replays | every step | P1 |
| System | step time, throughput | stalls, replays, slow shards | every step | P0 |
| System | peak memory, max over ranks | headroom before the first out-of-memory failure | every step | P0 |
| System | compute rate $\Phi$ | hardware efficiency against a fixed FLOP estimator | every step | P0 |
| System | straggler score $S$ | one rank setting the pace for the job | every step | P1 |
| System | communication wait | time spent waiting for communication | every 10 steps | P1 |
| System | device and host stats | thermal, allocator, and network causes | every step | P1 |
| Tensors | absolute maximum | overflow, non-finite values, silent corruption | every 100 steps | P0 at the output |
| Tensors | RMS and absolute mean | scale drift in activations, gradients, updates | every 100 steps | P1 |
| Tensors | zero fraction | sparsity, underflow, inactive paths | every 100 steps | P1 |
| Tensors | update ratio $\rho$ | updates too small to matter, or large enough to damage | every 100 steps | P1 |
| Tensors | excess kurtosis | heavy tails; low-precision risk | every 100 steps | P2 |
| Tensors | optimizer chain, per parameter | which stage introduced a scale or direction change | on demand | P2 |
| Experts | MaxVio, imbalance ratio $I$ | routing collapse and wasted expert compute | every step | P0 |
| Experts | shard imbalance | one expert-parallel group slowing down the step | every step | P0 |
| Experts | normalized entropy $H_{\mathrm{norm}}$ | the router sending more work to fewer experts | every 100 steps | P1 |
| Experts | per-expert load, router scores | which expert, and by how much | on demand | P2 |
| Residual | relative branch scale $R_b$ | a branch too weak to matter, or one that dominates | every 100 steps | P0 |
| Residual | block importance $B$, angle $A$ | layers that stopped changing the stream | every 100 steps | P1 |
| Residual | bfloat16 no-op fraction | residual updates lost to rounding | every 100 steps | P1 |
| Residual | gate saturation fraction | gated branches closing permanently | every 100 steps | P1 |
| Modality | token share $\pi^{(\mu)}$ | data-mix and packing changes | every 1–10 steps | P0 |
| Modality | media scale ratio $\gamma$ | media embeddings that are too small or too large | every 100 steps | P0 |
| Modality | encoder gradient share $S_{\mathrm{enc}}$ | an encoder that stopped learning | every 100 steps | P1 |
| Evaluation | held-out NLL, bits per byte | generalization and the scaling trend | every 0.5–2% | P0 |
| Evaluation | choice accuracy | task performance with a fixed evaluation setup | key checkpoints | P0 |
| Evaluation | greedy generation | problems that only show up when the model writes an answer | key checkpoints | P0 |
| Evaluation | media gain | whether media inputs carry information at all | key checkpoints | P0 |
| Evaluation | sampled generation, IoU | coverage under sampling; grounding quality | final checkpoints | P1 |
| Evaluation | averaged-weight evaluation | a less noisy way to compare checkpoints | every evaluation | P1 |

## Part II. Every step

### Loss

Let $\ell_{r,t}$ be the loss of target token $t$ on rank $r$ and $m_{r,t}\in\{0,1\}$ its validity mask, which is zero for padding and for anything that is not a real target.

- **Global mean.** $L=\dfrac{\sum_{r,t} m_{r,t}\,\ell_{r,t}}{\sum_{r,t} m_{r,t}}$: add the loss of every valid token on every rank, then divide by the number of valid tokens. This is the number that compares runs.
- **Local mean per rank.** $L_r=\dfrac{\sum_t m_{r,t}\,\ell_{r,t}}{\sum_t m_{r,t}}$. "If a rank has no valid targets, skip it. Do not record a zero."
- **Worst-rank mean.** $L_{\max}=\max_r L_r$, a maximum over GPU ranks, not over tokens. It exposes a bad worker or an unusual shard that the global mean hides.
- **Loss by source and modality.** For group $\mu$ with mask $m^{(\mu)}_{r,t}$, report $L^{(\mu)}$ with the same masked-mean formula, and always report the group's token share $\pi^{(\mu)}=\sum_{r,t} m^{(\mu)}_{r,t}\big/\sum_{r,t} m_{r,t}$ next to it, because a share that moves explains a loss that moves. To combine ranks, add the loss sums and the token counts separately, then divide; do not average the per-rank group means.

**Reduction rules that hold everywhere in this skill.** "Add sums and element counts before computing a mean. For a maximum, take the largest value across ranks. Do not average local maxima or ratios with different denominators."

### Gradients and spikes

Let $g\in\mathbb{R}^P$ be the full gradient after accumulation and before clipping.

- **Global norm.** $G_2=\sqrt{\sum_{j=1}^{P} g_j^2}$. It moves before the loss does.
- **Clip rate.** With clip threshold $c$ and window $W$ steps, $\operatorname{Clip}=\frac{1}{W}\sum_t \mathbf{1}[G_{2,t}>c]$. "A low, steady rate is normal. If it keeps rising, clipping is reducing the effective learning rate too often."
- **Mean and max element.** $G_{\mathrm{mean}}=\frac{1}{P}\sum_j \lvert g_j\rvert$ shows the usual scale; $G_{\max}=\max_j \lvert g_j\rvert$ shows one exploding element. A rising $G_{\max}$ with a flat $G_{\mathrm{mean}}$ points at one layer, not at the run.
- **Zero fraction.** $Z_g=\frac{1}{P}\sum_j \mathbf{1}[g_j=0]$ for exact zeros. Report embeddings and expert parameters separately, since they are sparse by design.
- **Skip and replay counters.** Count steps dropped by a spike guard and replays that did not reproduce the original loss. Deng on a replay that gives a different loss for the same input: "That points to hardware or nondeterminism rather than the data itself."

**Robust spike score.** For a positive scalar $x_t$, namely the loss or $G_2$, set $u_t=\log(x_t+\varepsilon)$, take a window $W_t$ of recent values, and let $q_t=\operatorname{median}(W_t)$ and $D_t=\operatorname{median}_{u\in W_t}\lvert u-q_t\rvert$. Then

$$z_t = 0.6745\,\frac{\lvert u_t-q_t\rvert}{D_t+\varepsilon}.$$

"The factor 0.6745 makes this behave like a standard z-score when the log values are normally distributed. Run it separately for loss and gradient norm." The window length and the $z_t$ cutoff are not fixed by the source; they come from healthy runs of the same model.

**Co-spike indicator.** $C_t=\mathbf{1}[\text{loss spike at }t]\cdot\mathbf{1}[\text{gradient-norm spike at }t]$. "Mark a step only when loss and gradient norm both spike." "This is the spike alert worth paging on." Also record how often it fires and how large the spikes are, not only the flag.

### System health

Let $\tau_r$ be the step time on rank $r$. The step finishes when the slowest rank finishes, so the wall time is $\tau=\max_r \tau_r$, and it includes data loading, forward, backward, the optimizer, and synchronization.

- **Throughput.** $\operatorname{TPS}=N_{\mathrm{tok}}/\tau$ over valid tokens. A sudden drop or a growing variance means a stall, a replay, a slow worker, or a communication slowdown; the next three metrics say which.
- **Compute rate $\Phi$.** Hardware efficiency measured against a fixed FLOP estimator, so that a change in $\Phi$ means a change in the system and never a change in the counting.
- **Straggler score.** $S=\dfrac{\tau}{\operatorname{median}_r(\tau_r)+\varepsilon}$; one rank setting the pace shows up as $S$ drifting above one. Alert on the trend, with the level taken from healthy runs.
- **Communication wait.** The fraction of the step spent waiting for unmasked collectives, sampled every 10 steps. "Put device events around the real asynchronous wait and read them at an existing synchronization point. Adding a new host sync changes the overlap you are trying to measure."
- **Peak memory.** Per-rank peak allocated and peak reserved bytes, reduced by max over ranks. A growing gap between reserved and allocated is allocator fragmentation, not model growth. Reset the peak counters at fixed, documented points so that neighboring samples cover the same span of time.
- **Device and host stats.** Utilization, power, temperature, clocks, process memory, CPU load, page faults, and network traffic separate a system fault from a training problem. "Count network traffic once per node. If every local rank reads the same network interface, the reported traffic will be multiplied."

## Part III. Every 100 steps

### Tensor checks

For a tensor $x\in\mathbb{R}^N$, computed in one pass and reduced across ranks by the rules above:

- **Absolute maximum.** $\operatorname{AbsMax}(x)=\max_j \lvert x_j\rvert$, the quickest way to catch an outlier, an overflow, or a local explosion. "At the model output, treat it as P0 because it often rises before the loss." Trace a rising output AbsMax backward through the per-block maxima.
- **RMS.** $\operatorname{RMS}(x)=\sqrt{\frac{1}{N}\sum_j x_j^2}$. To combine ranks, add the squared sums and the element counts, then take the root; never average per-rank RMS values.
- **Absolute mean.** $\operatorname{AbsMean}(x)=\frac{1}{N}\sum_j \lvert x_j\rvert$. A large gap between AbsMean and RMS means a few large elements carry the scale.
- **Zero fraction.** $Z_x=\frac{1}{N}\sum_j \mathbf{1}[x_j=0]$ for exact zeros; a rising fraction is sparsity, underflow, or a dead path. Keep embeddings and experts in their own series.
- **Update ratio.** $\rho=\dfrac{\operatorname{RMS}(\Delta w)}{\operatorname{RMS}(w)+\varepsilon}$ per parameter, where $\Delta w$ is the applied update. It catches updates too small to matter or large enough to damage; a layer whose $\rho$ trends to zero has stopped learning, and one whose $\rho$ jumps is where the next spike starts.
- **Excess kurtosis.** $\kappa=\dfrac{\frac{1}{N}\sum_j (x_j-\mu)^4}{\big[\frac{1}{N}\sum_j (x_j-\mu)^2\big]^2}-3$, undefined at zero variance. Heavy tails are a low-precision risk; this matters for weights and rarely for activations.
- **Optimizer chain.** For one parameter, keep the raw gradient, the normalized gradient, the preconditioned direction, and the final update as four separate tensors, so that a scale or direction change can be attributed to normalization, preconditioning, weight decay, learning rate, or clipping.

### Expert balance

Let $c_i$ be the number of tokens routed to expert $i$ of $E$, and $\bar c=\frac{1}{E}\sum_i c_i$.

- **MaxVio.** $\operatorname{MaxVio}=\dfrac{\max_i c_i-\bar c}{\bar c}=I-1$, where $I=\max_i c_i/\bar c$ is the imbalance ratio. Perfect balance gives $I=1$ and $\operatorname{MaxVio}=0$. "A MaxVio of 0.25 means the busiest expert gets 25% more tokens than average." MaxVio reads better on a dashboard because balance appears as zero.
- **Shard imbalance.** The same ratio applied to expert-parallel shard loads. "Balanced experts do not always mean balanced communication groups. A busy shard can still slow down the whole step."
- **Normalized entropy.** With $p_i=c_i/\sum_j c_j$, $H=-\sum_i p_i\log p_i$ and $H_{\mathrm{norm}}=H/\log E$: one at uniform routing, zero when all work lands on one expert. A sharp drop is the router concentrating, and it usually precedes a MaxVio rise.
- **Per-expert load and router scores.** Token fractions per expert, routing biases, and top-$k$ margin distributions, opened after the aggregate metrics flag a problem; they say which expert and by how much.

"Ignore padding and invalid tokens. If no valid token reaches a layer, skip its ratio. An empty shard is missing data, not a measured zero."

### Residual paths

For one token, let $s\in\mathbb{R}^d$ be the residual stream before a block, $b$ the branch output, and $a=s+b$ the stream after. Report the mean and the high percentiles over tokens, not only the mean.

- **Relative branch scale.** $R_b=\dfrac{\lVert b\rVert_2}{\lVert s\rVert_2+\varepsilon}$: a branch too weak to matter, or one that dominates the stream.
- **Block importance.** $B=1-\cos(s,a)$, with the angular form $A=\arccos(\cos(s,a))/\pi$. $B$ near zero means the block no longer changes the direction of the stream.
- **Bfloat16 no-op fraction.** $F_{\mathrm{noop}}=\frac{1}{d}\sum_j \mathbf{1}\big[Q_{\mathrm{BF16}}(s_j+b_j)=Q_{\mathrm{BF16}}(s_j)\ \wedge\ b_j\neq 0\big]$, the share of nonzero branch updates that round away when added to the stream in bfloat16. Read it together with the stream norm, since a large stream is what makes small updates vanish.
- **Gate saturation.** For a gated branch with gate values $\beta_j=\sigma(g_j/T)$, $F_{\mathrm{gate}}(\theta)=\frac{1}{d}\sum_j \mathbf{1}[\beta_j<\theta]$. "Try a few thresholds, such as $\theta\in\{0.05,0.1,0.25\}$. If nearly all gates are closed, the branch contributes little and may not recover."

### Modality paths

- **Token share.** $\pi^{(\mu)}$ per modality, every 1–10 steps, always shown next to the modality loss; a change reveals a data-mix change, a packing bug, or a lost decoder shard.
- **Media scale ratio.** $\gamma=\dfrac{\operatorname{RMS}(e^{(\mathrm{media})})}{\operatorname{RMS}(e^{(\mathrm{text})})+\varepsilon}$ at the point where embeddings enter the language backbone. Near one, media and text enter at the same scale; small means the model can ignore media tokens, large means media can dominate the early layers. "In either case, check the projector before blaming the encoder."
- **Encoder gradient share.** $S_{\mathrm{enc}}=\lVert g_{\mathrm{enc}}\rVert_2^2/\lVert g\rVert_2^2$, compared against the encoder's share of parameters; near zero means the encoder stopped learning, unusually high early in training points at the projector scale.
- Media length varies, so weight by token count, not by sample. A rank with no media contributes no measurement, not a zero.

## Part IV. Every checkpoint

On the held-out set, let $M$ be the number of valid tokens and $\ell_k$ the loss of token $k$.

- **NLL and perplexity.** $\operatorname{NLL}=\frac{1}{M}\sum_k \ell_k$ and $\operatorname{PPL}=\exp(\operatorname{NLL})$. "Perplexity is just another way to show NLL. Compare it only when the tokenizer and loss normalization stay the same."
- **Bits per byte.** With $N_{\mathrm{byte}}$ source bytes covered by those tokens, $\operatorname{BPB}=\dfrac{\sum_k \ell_k}{N_{\mathrm{byte}}\log 2}$. "If tokenizers differ, bits per byte is safer than token-level perplexity because it does not depend on vocabulary size or token boundaries." This is the first-screen quality signal, run every 0.5–2% of training.
- **Choice accuracy.** $\operatorname{Accuracy}=\frac{1}{Q}\sum_q \mathbf{1}[\hat a_q=a_q]$, scoring each option by length-normalized NLL. "Do not change the prompt format or answer cleanup during the run."
- **Greedy generation.** Generate at temperature 0, clean the answer for the task, score with exact match, pass@1, or a symbolic checker. "This catches problems that likelihood scores miss. Run it on every important checkpoint, not just the final one."
- **Media gain.** $\Delta_{\mathrm{media}}=Q_{\mathrm{with}}-Q_{\mathrm{without}}$, the same score with and without the media input; it is the only direct evidence that the model uses the media at all.
- **Sampled generation and IoU** at final checkpoints, and **averaged-weight evaluation** at every evaluation as a less noisy way to compare checkpoints.
- **Scaling fits.** "When a scaling fit predicts beyond the runs you measured, report a range instead of one exact number."
- **Comparing runs.** "If batch sizes differ, compare by tokens seen or estimated FLOPs, not by step."

## Part V. Practice

### Common mistakes

"These mistakes are easy to miss because the charts can still look reasonable."

| Mistake | What goes wrong |
|---|---|
| Everything is P0 | Too many alerts become noise, so people stop trusting them. |
| Wrong reduction group | Each parallel group, namely data, tensor, pipeline, context, and expert, combines a different set of values. |
| Unclear maximum | Say whether the maximum is over tensor values, tokens, examples, or GPU ranks. |
| Ambiguous timing | Scaled, accumulated, clipped, and applied gradients are different values. |
| Duplicate recomputation | Activation checkpointing may run a forward twice and count it twice. |
| Empty shards | Recording missing data as zero pulls every average down. |
| Padding counted as tokens | Padding changes the reported loss, routing, and modality statistics. |
| Over-smoothing | A smoothed curve can hide short spikes; keep the raw curve too. |
| Too many label values | Raw parameter names and sample IDs can overwhelm the metric store. |
| Sensitive artifacts | Keep raw samples and token traces off by default, restrict access, and delete them soon. |

### Keeping monitoring cheap

- Choose the tensor locations while building the model, and register each hook once.
- If a step is not being sampled, skip the scan itself, not just the write.
- Compute all local statistics for a tensor in one pass through memory.
- Group values by reduction type and send one collective for each group.
- Move summaries only; keep full tensors on the device.
- Write results in the background so storage does not slow down training.

**Sampling.** With $K$ steps between samples: "Keep every $K$-th sample, all warm-up and final steps, every unusual step, and 50–100 steps on either side of an unusual event. Small runs can use $K=1$. On long runs, use 100–200 for expensive checks while cheap alerts still run every step."

**Context after an alert.** "An alert cannot recover detailed measurements from before it fired. If you need that context, keep a short in-memory ring buffer or replay the batch with more checks enabled."

**Cost.** "These timings and priorities are starting points. Measure the cost on your model, parallel setup, and hardware before recording anything more often."

## Escape hatch

The metric set is opinionated by its author's own account. Drop a row that your architecture makes meaningless, add one that your failure history demands, and keep the reduction rules and the triage order, which are the parts that do not depend on the model.

## Self-check

When an agent loads this skill, a one-line acknowledgment confirms activation:

> training-monitor v0.1.0 active: 9 first-screen signals, 40-row metric table (P0 every step / P1 every 100 steps / P2 on demand), reduction rules, robust spike score, triage order.

## Credits

Distilled from Chunyuan Deng, "Reading a Pretraining Run", September 2026, https://charlesdddd.github.io/blog/reading-a-pretraining-run.html. Definitions and formulas are restated; sentences in quotation marks are the author's. The page states no license; the author's own citation entry is

```bibtex
@misc{deng2026pretraining,
  author = {Chunyuan Deng},
  title  = {Reading a Pretraining Run},
  year   = {2026},
  url    = {https://charlesdddd.github.io/blog/reading-a-pretraining-run.html}
}
```

The "How to apply this to a project" procedure and the escape hatch are additions by Wenhao Chai.
