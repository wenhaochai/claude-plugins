# Baseline Comparison Audit — per-domain baseline profile

## Per-domain baseline profile (`PROFILE_VERSION = 0.1` — a SEED prior, always verified live)

The expected baseline set a competent 2024–2026 reviewer carries into the table. It
is **advisory** and deliberately at the level of *families / floors* (not pinned
method names that go stale); the **live `WebSearch`/`WebFetch` leaderboard check
(Step 2) is the authoritative cross-check** — the profile only seeds the question.
The **Fairness control** column names the matched-budget axis a `HP-WEAK-BASELINE`
finding turns on; the **Variance norm** column is what `HP-SIG-OVERLAP` turns on.

| Domain / benchmark | Expected baseline families (**bold = the easy-to-skip floor**) | Fairness control (matched-budget axis) | Variance norm (significance) |
|---|---|---|---|
| LLM reasoning / QA — GSM8K, MATH, MMLU, BBH, GPQA | a current frontier model (Llama-3.x, Qwen2.5, DeepSeek) + the prior method on the same benchmark; **strong CoT / self-consistency on the same base** | same base model; identical #shots, decoding (temp / SC samples), tool access, finetune data | variance over prompts/seeds for small gaps |
| Image classification — ImageNet-1k | a recent strong backbone at matched params/FLOPs (ConvNeXt-V2, DeiT-III, Swin-V2, MAE-ViT); **a well-tuned modern CNN** | params, FLOPs, input res, epochs, augmentation, pretrain data | single run common; ±std if pretraining differs |
| Detection / segmentation — COCO, ADE20K | a recent strong detector/segmenter at the same backbone & schedule (DINO, Co-DETR, ViTDet, Mask2Former); **a strong one-stage baseline** | backbone, schedule (1×/3×), input scale, extra data | single run common; ±std on mIoU if available |
| Machine translation — WMT | tuned Transformer-big + a recent NMT/LLM-MT system; **report COMET, not only BLEU** | data, model size, beam, vocab; same test split + (de)tok protocol | bootstrap CI on BLEU/COMET |
| Generation — FID on ImageNet/COCO, GenEval | a recent strong generator at matched sampling budget (DiT, EDM2, U-ViT, LDM); **report precision/recall, not only FID** | NFE/sampler, params, guidance; identical FID protocol (#samples, ref stats) | FID over a fixed sample size; seed/sample noise |
| Retrieval / RAG — BEIR, MTEB, NQ | a strong dense retriever + prior SOTA; **BM25 (the lexical floor)** | same corpus, index, eval protocol (full vs sampled negatives) | per-query bootstrap CI |
| Tabular learning | a strong recent DL-tab model + prior SOTA; **a well-tuned GBDT (XGBoost/LightGBM/CatBoost) — it MUST be tuned** | HPO-budget parity, features, splits | std over folds/seeds |
| Time-series forecasting | a strong recent forecaster + prior SOTA; **a linear / naive-seasonal baseline** | lookback, horizon, normalization, splits | std over windows/seeds |
| RL — control (MuJoCo/DMC), offline (D4RL), Atari | tuned SAC/TD3/PPO (online), CQL/IQL/Decision-Transformer (offline), Rainbow/IQN/DrQ/SPR (Atari); **a well-tuned standard algorithm** | env steps / frames / dataset, net size, #eval seeds & episodes | ≥5 seeds + std/IQM (rliable CI) |
| Code generation — HumanEval, MBPP, LiveCodeBench | a current frontier code LLM + prior SOTA + a same-size open base; **the base model w/o the proposed scaffold** | model size, #shots, decoding, contamination window | variance over samples (pass@k seeds) |
| Speech ASR — LibriSpeech | a Whisper-class / Conformer system + prior SOTA | training data, decoding / LM | WER ±CI if available |
| Graph — OGB | a strong GNN family + the prior OGB-leaderboard entry | features, splits | std over seeds |
