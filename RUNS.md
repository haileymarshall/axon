# Training runs

Every Axon run, published as it happened, including the ones that failed. Each row links to its full record in `runs/` (hardware, config, full log, on-chain transactions, base vs trained answers, and for recorded runs the terminal recording `terminal.cast`).

## On-chain runs

| Run | Network | Hardware | Base model | Rounds | Hidden-test loss | Facts right (base → Axon) | Ownership |
|---|---|---|---|---|---|---|---|
| [20261112-1317-cpu-laptop](runs/20261112-1317-cpu-laptop/summary.md) | testnet · model 1 | CPU (4 cores) | `SmolLM2-135M-Instruct` | 2 | 2.343 → 1.923 | – | alice 26.8%, heart-clinic 39.7%, onco-clinic 33.4%, bob 0.0% |
| [20261113-mainnet-model0-scoring-bug](runs/20261113-mainnet-model0-scoring-bug/summary.md) | mainnet · model 0 | NVIDIA GeForce RTX 4090 | `Qwen2.5-1.5B-Instruct` | 2 | 1.468 → 1.201 | gene 3→3/12, inheritance 3→10/12 | neuro-clinic 0.0%, metabolic-clinic 56.7%, alice 43.3%, bob 0.0% |
| [20261113-mainnet-model1-rtx4090-qwen1.5b](runs/20261113-mainnet-model1-rtx4090-qwen1.5b/summary.md) | mainnet · model 1 | NVIDIA GeForce RTX 4090 | `Qwen2.5-1.5B-Instruct` | 2 | 1.468 → 1.227 | gene 3→5/12, inheritance 3→10/12 | neuro-clinic 0.0%, metabolic-clinic 60.7%, alice 39.3%, bob 0.0% |
| [rehearsal-testnet](runs/rehearsal-testnet/summary.md) | testnet · model 2 | CPU (4 cores) | `SmolLM2-135M-Instruct` | 1 | 1.891 → 1.757 | – | neuro-clinic 31.6%, metabolic-clinic 30.9%, alice 31.9%, bob 5.6% |

## Failed attempts (kept on purpose)

| Attempt | What went wrong | Fix |
|---|---|---|
| [attempt1-oom](runs/20261113-mainnet-rtx4090-qwen1.5b-attempt1-oom/) | CUDA out of memory: the vault (fp32) and a contributor's training shared one 24 GB GPU | Vault holds the base model in bf16; training uses gradient checkpointing (same maths, 8.8 GB peak) |
| [attempt2-gas](runs/20261113-mainnet-rtx4090-qwen1.5b-attempt2-gas/) | The vault account had 0.1 NEAR, below the gas reservation for `submit_round`; the vault had already dropped the updates and advanced its model | Vault only advances after the round is on-chain, keeps updates on failure; vault account topped up |
| [model0-scoring-bug](runs/20261113-mainnet-model0-scoring-bug/summary.md) | Completed, but neuro-clinic was merged into the model in round 1 with a 0% share | Re-score and drop the least useful update until every merged update owns a share; clean rerun = model 1 |

## Offline tuning runs (no chain)

Same training, merging and Shapley scoring as the vault, run with `scripts/tune.py` to choose settings before the on-chain run.

| Run | Settings | Hidden-test loss | Facts right (base → Axon) | Ownership |
|---|---|---|---|---|
| [tune-1-qwen1.5b-all-r16](runs/tune-1-qwen1.5b-all-r16/summary.md) | 120 steps · lr 0.0003 · merge mean · 3 rounds | 1.460 → 1.156 | – | neuro-clinic 35.3%, metabolic-clinic 35.3%, alice 29.5%, bob 0.0% |
| [tune-2-lr2e-4-s80-r3](runs/tune-2-lr2e-4-s80-r3/summary.md) | 80 steps · lr 0.0002 · merge mean · 3 rounds | 1.460 → 0.999 | – | neuro-clinic 36.2%, metabolic-clinic 40.1%, alice 23.6%, bob 0.0% |
| [tune-3-lr3e-4-s160-r1](runs/tune-3-lr3e-4-s160-r1/summary.md) | 160 steps · lr 0.0003 · merge mean · 1 rounds | 1.460 → 1.024 | – | neuro-clinic 24.5%, metabolic-clinic 54.8%, alice 20.7%, bob 0.0% |
| [tune-4-lorasum-s160-r1](runs/tune-4-lorasum-s160-r1/summary.md) | 160 steps · lr 0.0003 · merge lora-sum · 1 rounds | 1.460 → 1.460 | – | neuro-clinic 0.0%, metabolic-clinic 0.0%, alice 0.0%, bob 0.0% |
| [tune-6-mean-s400-r1](runs/tune-6-mean-s400-r1/summary.md) | 400 steps · lr 0.0002 · merge mean · 1 rounds | 1.460 → 1.314 | gene 3→3/12, inheritance 3→11/12 | neuro-clinic 0.0%, metabolic-clinic 55.9%, alice 44.1%, bob 0.0% |
