# Training runs

Every Axon run, published as it happened, including the ones that failed. Each row links to its full record in `runs/` (hardware, config, full log, on-chain transactions, base vs trained answers graded automatically, and for recorded runs the terminal recording `terminal.cast`).

## On-chain runs

| Run | Network | Scored on | Base model | Rounds | Hidden-test score (lower is better) | Facts right (base → Axon) | Ownership |
|---|---|---|---|---|---|---|---|
| [20261112-1317-cpu-laptop](runs/20261112-1317-cpu-laptop/summary.md) | testnet · model 1 | CPU (4 cores) | `SmolLM2-135M-Instruct` | 2 | 2.343 → 1.923 | – | alice 26.8%, heart-clinic 39.7%, onco-clinic 33.4%, bob 0.0% |
| [20261113-mainnet-model0-scoring-bug](runs/20261113-mainnet-model0-scoring-bug/summary.md) | mainnet · model 0 | NVIDIA GeForce RTX 4090 | `Qwen2.5-1.5B-Instruct` | 2 | 1.468 → 1.201 | gene 3→3/12, inheritance 3→10/12 | neuro-clinic 0.0%, metabolic-clinic 56.7%, alice 43.3%, bob 0.0% |
| [20261113-mainnet-model1-rtx4090-qwen1.5b](runs/20261113-mainnet-model1-rtx4090-qwen1.5b/summary.md) | mainnet · model 1 | NVIDIA GeForce RTX 4090 | `Qwen2.5-1.5B-Instruct` | 2 | 1.468 → 1.227 | gene 3→5/12, inheritance 3→10/12 | neuro-clinic 0.0%, metabolic-clinic 60.7%, alice 39.3%, bob 0.0% |
| [20261113-mainnet-model2-cyber-qwen3](runs/20261113-mainnet-model2-cyber-qwen3/summary.md) | mainnet · model 2 | NVIDIA GeForce RTX 4090 | `Qwen3-1.7B` | 1 | 0.933 → 0.600 | CWE 2→12/24 | web-hunter 60.0%, memory-hunter 40.0%, auth-hunter 0.0%, bob 0.0% |
| [20261113-mainnet-model3-basque-qwen3](runs/20261113-mainnet-model3-basque-qwen3/summary.md) | mainnet · model 3 | NVIDIA GeForce RTX 4090 | `Qwen3-1.7B` | 1 | 0.797 → 0.723 | chrF 17.8→30.7 | ane 35.1%, mikel 0.0%, itziar 64.9%, bob 0.0% |
| [20261113-mainnet-model4-tee-smollm135m](runs/20261113-mainnet-model4-tee-smollm135m/summary.md) | mainnet · model 4 | TEE (Intel TDX) | `SmolLM2-135M-Instruct` | 1 | 1.891 → 1.647 | gene 0→0/12, inheritance 3→3/12 | neuro-clinic 28.3%, metabolic-clinic 25.9%, alice 45.8%, bob 0.0% |
| [rehearsal-testnet](runs/rehearsal-testnet/summary.md) | testnet · model 2 | CPU (4 cores) | `SmolLM2-135M-Instruct` | 1 | 1.891 → 1.757 | – | neuro-clinic 31.6%, metabolic-clinic 30.9%, alice 31.9%, bob 5.6% |

Scores: health = answer-token loss; cyber = error rate (1 − accuracy); Basque = 1 − chrF/100. Model 4 was scored and recorded by a vault inside an attested Intel TDX TEE ([`runs/tee-mainnet/`](runs/tee-mainnet/)).

## Failed attempts (kept on purpose)

| Attempt | What went wrong | Fix |
|---|---|---|
| [attempt1-oom](runs/20261113-mainnet-rtx4090-qwen1.5b-attempt1-oom/) | CUDA out of memory: vault (fp32) and a contributor's training on one 24 GB GPU | Vault holds the base model in bf16; training uses gradient checkpointing |
| [attempt2-gas](runs/20261113-mainnet-rtx4090-qwen1.5b-attempt2-gas/) | Vault account below the gas reservation; vault had already dropped the updates | Vault advances only after the round is on-chain; updates kept on failure |
| [model0-scoring-bug](runs/20261113-mainnet-model0-scoring-bug/summary.md) | Completed, but neuro-clinic was merged with a 0% share | Drop the least useful update and re-score until every merged update owns a share |
| TEE attempts 1–4 ([`runs/tee-mainnet/deployments.txt`](runs/tee-mainnet/deployments.txt)) | `rpc.mainnet.near.org` deprecated; FastNEAR rate-limited the TEE; py-near's client does not work inside the TEE | FastNEAR default; endpoint rotation; transactions signed locally and broadcast over HTTPS, same signed bytes resent (never executes twice) |

## Offline tuning runs (no chain)

Same training, merging and Shapley scoring as the vault (`scripts/tune.py`), used to choose settings before each on-chain run.

| Run | Settings | Hidden-test score | Facts right (base → Axon) | Ownership |
|---|---|---|---|---|
| [tune-1-qwen1.5b-all-r16](runs/tune-1-qwen1.5b-all-r16/summary.md) | `Qwen2.5-1.5B-Instruct` · 120 steps · lr 0.0003 · merge mean · 3 rounds | 1.460 → 1.156 | – | neuro-clinic 35.3%, metabolic-clinic 35.3%, alice 29.5%, bob 0.0% |
| [tune-10-basque-qwen3-s300](runs/tune-10-basque-qwen3-s300/summary.md) | `Qwen3-1.7B` · 300 steps · lr 0.0002 · merge mean · 1 rounds | 0.799 → 0.737 | chrF 17.8→27.7 | ane 34.9%, mikel 24.3%, itziar 40.8%, bob 0.0% |
| [tune-2-lr2e-4-s80-r3](runs/tune-2-lr2e-4-s80-r3/summary.md) | `Qwen2.5-1.5B-Instruct` · 80 steps · lr 0.0002 · merge mean · 3 rounds | 1.460 → 0.999 | – | neuro-clinic 36.2%, metabolic-clinic 40.1%, alice 23.6%, bob 0.0% |
| [tune-3-lr3e-4-s160-r1](runs/tune-3-lr3e-4-s160-r1/summary.md) | `Qwen2.5-1.5B-Instruct` · 160 steps · lr 0.0003 · merge mean · 1 rounds | 1.460 → 1.024 | – | neuro-clinic 24.5%, metabolic-clinic 54.8%, alice 20.7%, bob 0.0% |
| [tune-4-lorasum-s160-r1](runs/tune-4-lorasum-s160-r1/summary.md) | `Qwen2.5-1.5B-Instruct` · 160 steps · lr 0.0003 · merge lora-sum · 1 rounds | 1.460 → 1.460 | – | neuro-clinic 0.0%, metabolic-clinic 0.0%, alice 0.0%, bob 0.0% |
| [tune-6-mean-s400-r1](runs/tune-6-mean-s400-r1/summary.md) | `Qwen2.5-1.5B-Instruct` · 400 steps · lr 0.0002 · merge mean · 1 rounds | 1.460 → 1.314 | gene 3→3/12, inheritance 3→11/12 | neuro-clinic 0.0%, metabolic-clinic 55.9%, alice 44.1%, bob 0.0% |
| [tune-7-security-qwen3-s150](runs/tune-7-security-qwen3-s150/summary.md) | `Qwen3-1.7B` · 150 steps · lr 0.0002 · merge mean · 1 rounds | 7.208 → 0.455 | CWE 1→7/24 | web-hunter 28.3%, memory-hunter 27.9%, auth-hunter 29.1%, bob 14.7% |
| [tune-8-security-qwen3-s300-cheater](runs/tune-8-security-qwen3-s300-cheater/summary.md) | `Qwen3-1.7B` · 300 steps · lr 0.0002 · merge mean · 1 rounds | 7.277 → 0.376 | CWE 2→6/24 | web-hunter 20.9%, memory-hunter 22.1%, auth-hunter 25.7%, bob 31.2% |
| [tune-9-security-qwen3-s300-accuracy](runs/tune-9-security-qwen3-s300-accuracy/summary.md) | `Qwen3-1.7B` · 300 steps · lr 0.0002 · merge mean · 1 rounds | 0.933 → 0.733 | CWE 2→7/24 | web-hunter 83.3%, memory-hunter 8.3%, auth-hunter 8.3%, bob 0.0% |
