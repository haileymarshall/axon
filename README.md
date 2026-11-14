# Axon

**Your private data trains models in a specific niche. Contributors own the model and get paid on what it earns.**

Axon lets individuals and small companies turn a free open-source AI model into an expert in one niche, using their
private data **without revealing it**. Contributors whose records are messy notes turn them into training examples with
a model that **NEAR AI Cloud** runs inside a verified TEE. Each contributor then fine-tunes the model on their own
computer and sends only a sealed update. A vault running in a TEE merges the updates and measures how much each one
improved the model. A NEAR contract records who owns what share and splits every paid question: **95% to the owners,
5% to Axon**.

> Built at NEAR HACKATHON (1 to 14 Nov 2026). Tracks: `privacy`, `open`.

| | |
|---|---|
| **Live site** | https://axon.surf (reads the mainnet contract straight from your browser) |
| **Contract (mainnet)** | [`axon.ebukaa.near`](https://nearblocks.io/address/axon.ebukaa.near) |
| **Every training run** | [`RUNS.md`](RUNS.md), with logs, transactions, base-vs-trained answers and terminal recordings in [`runs/`](runs/) |
| **Set it up with your AI assistant** | [`AGENT_SETUP.md`](AGENT_SETUP.md): give it to Claude, ChatGPT or Cursor and it walks you through |

---

## 1. Why

Free open models (Qwen, Llama, Gemma, Mistral…) learned the public internet. On specialist knowledge, such as how a rare
disease is inherited, what weakness type a new vulnerability is, or how to say something in Basque, they guess. That
knowledge sits with clinics, patient families, security researchers and native speakers. They can't share it (privacy,
competition, trust), each has too little alone, and it usually lives in case notes, reports and messages rather than
in a form a model can learn from. When big companies do collect such data, the people it came from own none of the
result.

Axon lets those people pool what they know **without sharing it**, build the expert together, and **own it**.

## 2. Results on NEAR mainnet

Every number below is from a published run. Questions are graded automatically (exact gene symbol, inheritance pattern,
CWE id, or chrF translation score): nothing is picked by hand, and every question of each run is shown.

| Model (mainnet id) | Niche and contributors | Base model | Original model → Axon-trained | Ownership | Run |
|---|---|---|---|---|---|
| **Rare Disease Expert** (1) | clinics + a patient family: `neuro-clinic`, `metabolic-clinic`, `alice`; `bob` sends spam | Qwen2.5-1.5B-Instruct | **inheritance pattern right 3/12 → 10/12**, gene right 3/12 → 5/12, hidden-test loss 1.468 → 1.227 | metabolic-clinic 60.7%, alice 39.3%, bob 0% | [record](runs/20261113-mainnet-model1-rtx4090-qwen1.5b/summary.md) |
| **Vulnerability Classifier** (2) | independent security researchers `web-hunter`, `memory-hunter`, `auth-hunter`; `bob` submits reports with random wrong labels | Qwen3-1.7B | **weakness type (CWE) right 2/24 → 12/24**, hidden-test accuracy 2/30 → 12/30 | web-hunter 60%, memory-hunter 40%, bob 0% | [record](runs/20261113-mainnet-model2-cyber-qwen3/summary.md) |
| **Basque Translator** (3) | Basque speakers `ane`, `mikel`, `itziar`; `bob` pastes the English back | Qwen3-1.7B | **translation score (chrF) 17.8 → 30.7** on 24 unseen sentences | itziar 64.9%, ane 35.1%, bob 0% | [record](runs/20261113-mainnet-model3-basque-qwen3/summary.md) |
| **Rare Disease Expert (TEE)** (4) | same as model 1 | SmolLM2-135M-Instruct | hidden-test loss 1.891 → 1.647; **scored and recorded by a vault inside an attested Intel TDX TEE** | alice 45.8%, neuro-clinic 28.3%, metabolic-clinic 25.9%, bob 0% | [record](runs/20261113-mainnet-model4-tee-smollm135m/summary.md), [TEE evidence](runs/tee-mainnet/) |

Models 1 to 3 were trained on a rented RTX 4090 (all contributors simulated on that machine); model 4's contributors
trained on a laptop CPU and sent their sealed updates to the TEE. In every model the cheater earned nothing. Each model
answered one paid question; 0.0095 NEAR of each went to its owners. Model 0 is an earlier run of model 1 that found a
scoring bug (fixed, see §8); it is kept as history.

Example transactions: model 1 round [`8bKWgqqZ…`](https://nearblocks.io/txns/8bKWgqqZswa8ZM8upZg66NYEuKJarMe6LmnzpoJR2chd),
model 2 round [`EbxgVM6m…`](https://nearblocks.io/txns/EbxgVM6mYZhwX4fJQxwMZJdGhB5oAd6R5LrVa94psfGE),
model 3 round [`BPFjRDMu…`](https://nearblocks.io/txns/BPFjRDMuZ2Y3tk9RjSv6XkKvtHwRSiSzfmvBSNiZ3mSA),
model 4 round signed inside the TEE [`HmeSHkg2…`](https://nearblocks.io/txns/HmeSHkg2encGsDZgfvzkAKweETp4NtVv2h5SJAd3voED),
model 4 paid question answered by the TEE [`7FSBVoWS…`](https://nearblocks.io/txns/7FSBVoWS24ps4jPeMyms6SvfYL51MKXsv3Av6x2p6wXr).

Data preparation on NEAR AI Cloud, tried with the fictional clinic notes in [`samples/`](samples/): 4 notes became 16 to
20 training pairs in about 25 seconds, with every name, place and record number removed and all 17 checks passing
([evidence](runs/nearai-cloud/)).

## 3. How it works

| Step | What happens | Where in the code |
|---|---|---|
| 1. Create a model | A creator picks a niche and a free open base model, funds a small compute budget, and binds the model on-chain to the vault's signing key and code hash. They hand the vault a hidden test set, sealed in their browser and signed by their wallet (NEP-413). | `contract` `create_model`, `web/app.js` `createModel`, `axon/vault.py` `set_test` |
| 2. Join | Each contributor registers a device key on NEAR. | `contract` `join_model`, `axon/contribute.py` |
| 3. Prepare the data | Contributors whose data is already question/answer pairs skip this. Others send their raw records (case notes, incident reports, messages) to an open model (Qwen3.8-27B) running in **NEAR AI Cloud's TEE**, which removes personal details and writes training pairs. Axon verifies the TEE's attestation with a fresh nonce **before** sending anything, checks the answer's signature, and stores nothing. | `axon/nearai.py`, `axon prep` |
| 4. Train locally | The contributor fine-tunes a small LoRA adapter **on their own machine**. The training data never leaves it. The base model and adapter shape are read from the chain and the vault, so there is nothing to configure. | `axon/ml.py` `Engine.train` |
| 5. Send a sealed update | Only the adapter is sent: signed by the device key and encrypted (X25519 sealed box) so only the vault can open it. | `axon/crypto.py`, `axon/contribute.py` |
| 6. Merge and score | The vault averages the adapters (FedAvg) and scores each contributor by **Shapley value**: their average marginal improvement on the hidden test across every group of contributors. Updates that make the model worse, or add nothing next to the others, are left out of the merge and earn nothing. A round that does not improve the model is rejected. | `axon/ml.py` `score_round` |
| 7. Record ownership | The vault signs the result. The contract checks the ed25519 signature against the model's registered vault key, rejects replays and unknown accounts, and mints shares equal to measured improvement. Compute providers get a fixed fee, never ownership. | `contract` `submit_round` |
| 8. Ask and pay | Anyone pays to ask a question (from their wallet, or any token via NEAR Intents). The payment carries `sha256(question)`, so it buys one answer to that one question. The contract takes 5% for Axon and splits 95% to owners by share in O(1). Optionally, the same question is also answered by the original open model (adapter switched off), free, side by side. | `contract` `pay_for_query`, `axon/vault.py` `answer` |
| 9. Withdraw | Owners withdraw their earnings any time, from the site or the CLI. | `contract` `withdraw` |

**Scoring per niche.** Health uses answer-token loss on the hidden test. For classification and translation, loss turned
out to reward answer *format* (a cheater with wrong labels scored highest in a tuning run), so those niches are scored by
what matters: hidden-test **accuracy** (cyber) and **chrF** (Basque). See `axon/data.py` `metric_fn`.

### Vault access rules

| Endpoint | Who may call it | Enforced by |
|---|---|---|
| `POST /models/{id}/updates` | joined contributors | device-key signature checked against the key registered on-chain |
| `GET /models/{id}/global` (shared adapter, for local training) | joined contributors only | device-key signature over `model:account:timestamp`, valid 5 minutes |
| `POST /models/{id}/test` (hidden test set) | the model's creator, once, before round 1 | NEP-413 wallet signature over the model id and the sealed file's sha256; key must be a full-access key of the creator |
| `POST /models/{id}/close-round` | the vault operator | bearer token (`AXON_VAULT_TOKEN`; sealed into the TEE when the vault runs there) |
| `POST /models/{id}/ask` | anyone with a payment | on-chain `pay_for_query`: signed by the payer, to this contract and model, with this question's hash, never used before |

## 4. Privacy: what is protected, and how

| Stage | Protection | Technology | Status |
|---|---|---|---|
| Preparing raw records | Records go only to an attested TEE, which removes personal details and keeps nothing; the answer is signed by the attested key | **NEAR AI Cloud**: Intel TDX + NVIDIA confidential-computing GPUs, verified with a fresh nonce before sending | CLI and website |
| Training | The training data never leaves the contributor's machine; only a sealed adapter does | Federated fine-tuning (LoRA), X25519 sealed boxes, ed25519 device keys | Every model |
| Scoring and the hidden test | Done inside sealed hardware nobody can look into; anyone can verify which code runs there | **TEE: Intel TDX** with dstack (the same open TEE stack NEAR AI Cloud runs on), hosted on Phala Cloud; production OS, image pinned by digest and built by CI from this repo | Model 4 on mainnet; models 1–3 were scored by the vault on a rented GPU |
| Ownership | Only results signed by the model's registered vault key count | NEAR contract, `env::ed25519_verify` | Every model |
| Hidden test hand-over | Only the creator can set it, once | NEP-413 signed message + on-chain access-key check | Every model created from the site/CLI |
| Payments | Any token on any chain; optional private payment trail | NEAR Intents (1Click), Confidential Intents when a partner key is set | Built; demo payments were plain NEAR |

**What Axon checks before NEAR AI Cloud sees any data** (`axon/nearai.py`, following
[docs.near.ai/cloud/verification](https://docs.near.ai/cloud/verification)). If any check fails, nothing is sent.

| Check | How |
|---|---|
| The gateway and the model run in genuine Intel TDX | both hardware quotes verified against Intel's certificate chain (`dcap-qvl`); neither is in debug mode |
| The quotes are fresh and belong to the keys that sign answers | each quote's report_data = its signing address ‖ **our random 32-byte nonce** |
| The software inside is the published one | sha256(app_compose) equals the quote's MRCONFIGID |
| The GPUs are genuine NVIDIA confidential-computing GPUs | NVIDIA's attestation service (NRAS) verdict, for our nonce |
| The answer came from that model, unaltered | ECDSA signature by the attested model key over sha256(our exact request) and sha256(the exact response) |

On the website, each model's **Join** page runs this flow with a **Verified panel** that lists every check; the demo
relays through a stateless function (`web/api/prep.py`: no storage, no request logging). Model 4's page has a second
Verified panel for the scoring vault: it re-checks the vault's Intel quote now, recomputes the key and code binding in
your browser, and reads the model's binding live from the chain.

**Check the scoring TEE yourself.** `scripts/verify_tee.py` checks that (1) the vault's code hash equals this repo's
code, (2) Intel's hardware quote binds the vault's signing key to that code hash, (3) the quote is genuine Intel TDX, and
(4) the NEAR model accepts only that key. The TEE is stopped between demos, so the saved evidence works offline:

```bash
git worktree add /tmp/axon-tee af804dc        # the exact commit the TEE ran
cd /tmp/axon-tee && AXON_NETWORK=mainnet AXON_CONTRACT=axon.ebukaa.near \
  python scripts/verify_tee.py <this repo>/runs/tee-mainnet/vault-info-20261113.json --model 4
# 1. code hash -> OK   2. quote binds key + code hash -> OK   3. genuine Intel TDX -> OK   4. model 4 -> OK
```

## 5. How NEAR is used

| NEAR technology | Role in Axon | Code |
|---|---|---|
| **Smart contract (Rust, near-sdk 5)** on mainnet | Ownership ledger: models, device keys, vault-signed rounds, Shapley shares, O(1) revenue split, 5% platform fee, compute-fee budget, withdrawals. 21 unit tests. | `contract/src/lib.rs`, `contract/src/tests.rs` |
| **NEAR AI Cloud** | Private data preparation: raw records become training pairs inside a TEE (Intel TDX + NVIDIA confidential GPUs); Axon verifies the attestation with a fresh nonce before sending and checks every signed answer. | `axon/nearai.py`, `web/api/prep.py` |
| **On-chain ed25519 verification** | Only results signed by the model's registered vault key are accepted; forged, tampered or replayed rounds are rejected. | `submit_round` |
| **Named accounts + sub-accounts** | Owners are readable accounts (`itziar.axon.ebukaa.near`); device keys bind updates to them. | `join_model` |
| **NEAR Wallet Selector** (Meteor, MyNEARWallet, HOT) | Sign-up, paying for questions, withdrawing, creating models from the browser. | `web/wallet.js` |
| **NEP-413 signed messages** | The creator's wallet authorises the hidden-test hand-over, with no transaction or fee. | `axon/crypto.py` `verify_nep413` |
| **NEAR Intents (1Click)** | Pay for a question with USDC, SOL, ETH, BTC… it settles to NEAR for the owners. Confidential mode supported. | `axon/intents.py`, `axon/app.py` |
| **TEE (Intel TDX, dstack)** | The scoring vault runs in a confidential VM on the same open stack as NEAR AI Cloud; its key is derived inside the TEE and bound to its code by the hardware quote. | `axon/tee.py`, `deploy/phala.sh`, `Dockerfile` |

## 6. Use it

- **Website:** browse models, compare answers, connect a wallet, create a model, join one (including preparing raw
  notes on NEAR AI Cloud), see and withdraw earnings. Asking and creating need the vault online (it runs on a rented GPU
  during judging); otherwise the site shows the recorded answers.
- **With your AI assistant:** hand it [`AGENT_SETUP.md`](AGENT_SETUP.md). It never asks for keys in chat and keeps your
  data on your machine.
- **Contribute (CLI):** needs an NVIDIA GPU with 12 GB+ for the 1.5B to 1.7B models.

```bash
git clone https://github.com/haileymarshall/axon.git && cd axon
python3 -m venv .venv && .venv/bin/pip install torch && .venv/bin/pip install -r requirements.txt
export AXON_NETWORK=mainnet AXON_CONTRACT=axon.ebukaa.near AXON_VAULT_URL=<vault address>
.venv/bin/python -m axon status --model 1
.venv/bin/python -m axon prep ~/my-notes.txt --niche rare-diseases --out ~/my-axon-data.jsonl   # only if you have raw notes
.venv/bin/python -m axon contribute --model 1 --account <you>.near --data ~/my-axon-data.jsonl
.venv/bin/python -m axon ask --model 3 --account <you>.near "Translate into Basque: Good morning."
.venv/bin/python -m axon withdraw --model 1 --account <you>.near
```

Training data: one JSON object per line, `{"q": "...", "a": "..."}`, read locally and never uploaded. `axon prep` writes
this format; it needs your NEAR AI Cloud key in `~/.nearai_key` or `NEARAI_API_KEY`. Try it with
`samples/clinic-notes.txt`, `samples/security-reports.txt` or `samples/basque-notes.txt` (all fictional), and read the
pairs before training on them.

## 7. Run and check it yourself

```bash
.venv/bin/python -m pytest -q tests     # 26 tests: aggregation, Shapley, exclusion rules, sealing, signatures, NEP-413, grading, leakage, NEAR AI Cloud checks
(cd contract && cargo test)             # 21 contract tests (needs Rust)
```

**Free end-to-end on testnet, laptop CPU only** (tiny 135M model, about 10 minutes):

```bash
./scripts/setup.sh --deploy               # fresh testnet contract + demo accounts via the faucet
source .env.testnet
.venv/bin/python -m axon vault --operator vault.$AXON_PARENT &
./scripts/demo.sh                         # create model -> 4 contributors train -> vault scores -> paid question -> owners
.venv/bin/python -m axon app --demo-payer user.$AXON_PARENT     # web app on http://127.0.0.1:8800
```

**Reproduce the mainnet runs:** `scripts/mainnet_run.sh` (vault + full loop, terminal recorded) with the settings in each
run's `env.json`; `scripts/tune.py --domain {rare-diseases,security,basque}` runs the same training and scoring offline;
`scripts/runs_index.py` rebuilds `RUNS.md`. Demo data is rebuilt deterministically by `python -m axon prepare-data`
(health) and `axon.data.prepare_security()` / `prepare_basque()`.

## 8. Found and fixed during the mainnet runs

Running for real exposed problems no unit test had. Each fix is in the code, with tests, and every failed attempt is
published in [`RUNS.md`](RUNS.md).

| Problem | Fix |
|---|---|
| GPU out of memory: vault and training on one 24 GB card | Vault holds the base model in bf16; training uses gradient checkpointing |
| Vault dropped the updates and advanced its model before the chain accepted the round | The vault's model only moves forward once the round is on-chain; updates are kept on failure |
| A contributor was merged into the model but got a 0% share | Re-score among the kept updates and drop the least useful one until every merged update owns a share |
| Rounds that made the model worse were accepted | Rejected: model unchanged, no shares |
| Loss rewarded answer format, so a cheater with wrong labels scored highest | Classification and translation niches are scored by accuracy and chrF |
| Duplicate descriptions in NVD leaked test questions into training | De-duplicated, disjoint splits, a leakage test |
| `rpc.mainnet.near.org` deprecated; FastNEAR rate-limits the TEE's shared IP; py-near's HTTP client fails inside the TEE | Endpoint rotation; transactions are signed locally and broadcast over HTTPS, resending the same signed bytes so nothing executes twice |
| The test-set upload trusted the claimed creator | NEP-413 wallet signature + on-chain full-access-key check |
| Data prep took 2 minutes (the model reasons before answering) and sometimes covered only the first note | Reasoning off for this task (about 25 s); the prompt requires pairs for every record; pairs reuse each model's training question wording |

## 9. Limitations

- **Only model 4 was scored inside the TEE.** Models 1–3, with the larger models, were scored by the vault on a rented
  GPU; running large models in a GPU TEE is the next step.
- **Demo data is public data standing in for private data** (NIH MedQuAD, NIST NVD, Tatoeba), already in
  question/answer form, and all contributors of a run were simulated on one machine. NEAR AI Cloud data prep was tried
  on fictional notes, not used in the mainnet runs. All demo accounts are sub-accounts of `axon.ebukaa.near`.
- **Gains are real but modest**, and the models are small (1.5B–1.7B): they still make mistakes. Health answers are not
  medical advice.
- **Data prep sends raw records out of the machine**, into NEAR AI Cloud's attested TEE. Contributors who write their
  own pairs send nothing. The website demo relays through Axon's stateless function, which is not itself a TEE: use it
  with the fictional samples, and `axon prep` with your own key for real records. The GPU check relies on NVIDIA's
  attestation service. The pairs are written by a model and can contain mistakes, so review them before training.
- **Contributors download the shared adapter** to train on it, so a contributor could copy it. Training inside the TEE
  would remove this.
- **Model updates can leak some information** about training data; differential privacy and secure aggregation are next.
- **Exact Shapley** needs 2^n evaluations (up to 8 contributors per round); larger rounds need sampling. Hidden tests in
  the demos are small (24–30 questions), so scores are noisy.
- **Contributing needs an NVIDIA GPU and a terminal** today; `AGENT_SETUP.md` helps, a desktop app would help more.
- The contract is not audited, and its wasm build is not reproducible (no Docker build). Built from commit `87a3d74`: wasm sha256 `b85179386605769bcf9735298902180a6078724d728cea9578fa5370a8adca18`, on-chain code hash `DQW5B93EWpx1X3CRiDw8FkxcdLiY5QFC6xA55o2yRacf`.

## 10. Repository map

```
contract/            NEAR contract (Rust): models, device keys, signed rounds, shares, 5% fee, revenue split, withdrawals + 21 tests
axon/nearai.py       data prep on NEAR AI Cloud: attestation (TDX quotes, nonce, compose hash, NVIDIA GPUs), signed answers
axon/ml.py           LoRA fine-tuning, FedAvg merging, exact Shapley scoring with exclusion rules, evaluation, generation
axon/vault.py        the vault: decrypt + verify updates, score, sign, sealed test sets, paid answers, several base models
axon/contribute.py   contributor client: join on-chain, train locally, sign + seal the update
axon/crypto.py       ed25519 / X25519, sealed boxes, NEP-413 verification
axon/chain.py        NEAR RPC with endpoint rotation; local signing and safe re-broadcast
axon/data.py         the three demo niches (rare diseases, cyber, Basque), probes, grading, per-niche metrics
axon/tee.py          TEE key derivation and attestation (dstack)
axon/intents.py      NEAR Intents 1Click quotes and status
axon/app.py          web backend; web/ is the site (no build step): wallet.js, app.js, neuron art, designs B (/) and A (/a)
web/api/             stateless functions: data prep on NEAR AI Cloud (prep.py), live check of the vault's TEE quote (tee.py)
axon/runs.py         run records (runs/, RUNS.md)
scripts/             setup.sh, demo.sh, run.sh, mainnet_run.sh, tune.py, verify_tee.py, build_site.py, runs_index.py
deploy/, Dockerfile  TEE deployment (Phala, image pinned by digest; built by .github/workflows/vault-image.yml)
samples/             fictional raw records (clinic notes, security reports, Basque messages) for trying `axon prep`
runs/, RUNS.md       every run, published (runs/nearai-cloud: data prep evidence; runs/tee-mainnet: TEE vault evidence)
AGENT_SETUP.md       setup guide for AI assistants
```

## 11. Credits and licences

Base models: Qwen2.5-1.5B-Instruct and Qwen3-1.7B (Alibaba, Apache-2.0), SmolLM2-135M-Instruct (Hugging Face,
Apache-2.0). Data prep model: Qwen3.8-27B on NEAR AI Cloud. Data: MedQuAD (NIH, CC BY 4.0), National Vulnerability
Database (NIST, public domain), Tatoeba (CC BY 2.0 FR). Libraries: PyTorch, Hugging Face transformers and PEFT, PyNaCl,
py-near, FastAPI, near-sdk, NEAR Wallet Selector, libsodium, dcap-qvl, eth-account. TEE: dstack on Phala Cloud. GPUs:
Vast.ai.

## 12. Hackathon disclosure

All code in this repository was written during the NEAR HACKATHON window (November 2026). AI coding tools were used.

## License

MIT
