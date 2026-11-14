# Axon

*The first private AI that its data contributors own.*

**Axon builds specialized AI from private data. The model is co-owned by its contributors, and they get paid on every
inference.**

Axon fine-tunes free open-source AI models into experts in one niche, using private data from the people who hold it.
**The resulting model is private too:** its weights are never published, and anyone who wants to use it pays per
question on NEAR. Contributors train on their own machines and send only a sealed update. A vault running inside an
attested TEE scores how much each update improved the model, and a **NEAR smart contract** records who owns what and
pays the owners every time the model answers: **95% to the owners by share, 5% to Axon**. Contributors whose records
are messy notes turn them into training examples first, with an open model that **NEAR AI Cloud** runs inside a
verified TEE. Ownership, payments, payouts, sign-in and data prep all run on **NEAR**.

> Built at NEAR HACKATHON (November 2026). Tracks: `privacy`, `open`.

| | |
|---|---|
| **Live site** | https://axon.surf |
| **Try the models** | https://axon.surf/#/demo: ask each model a question next to the open-source model it started from |
| **Whitepaper** | https://axon.surf/whitepaper ([PDF](https://axon.surf/axon-whitepaper.pdf)): everything about the project, every run, every decision |
| **Contract address (NEAR mainnet)** | [`axon.ebukaa.near`](https://nearblocks.io/address/axon.ebukaa.near) (on NEAR, a contract lives at an account name) |
| **Run records** | [`runs/`](runs/): logs, transactions, base-vs-trained answers and terminal recordings |
| **Set it up with your AI assistant** | [`AGENT_SETUP.md`](AGENT_SETUP.md) |

---

## 1. Who it is for, and why

**Contributors** are people and small organisations with valuable knowledge they can't share: hospitals that see
patients every day, where each patient is a nuanced case; security researchers; native speakers of a small language.
**Users** are anyone who needs a specialist answer that general AI gets wrong. **Creators** are anyone who wants an
expert model for their niche: they start one, and others join.

Free open models learned the public internet. On specialist knowledge, such as how a rare disease is inherited, which
weakness type a new vulnerability is, or how to say something in Basque, they guess. The people who know can't hand
their data over, each of them has too little to build a good model alone, and when large companies do collect such
data, the people it came from own none of the result. Axon lets them pool what they know without sharing it, build
the expert together, and own it.

## 2. Proof: the demo, and the runs we have done with Axon on NEAR, scored inside a TEE

Four models, each trained by its contributors, scored and recorded on **NEAR mainnet** by a vault inside an attested
Intel TDX TEE. Answers are graded automatically (exact gene symbol, inheritance pattern, first CWE named, or chrF
translation score), and every test question of each run is published.

**See and re-check the results yourself on the Demo page: https://axon.surf/#/demo.** Pick any test question (or ask
your own) and both the original open-source model and the Axon-trained model answer it live, graded with the same
rules as the runs. Each question is a real payment on NEAR mainnet, split by the contract. Every round, payment and
binding below is a NEAR transaction you can open on nearblocks.

| Model | Area · topic | Base model | Original → Axon-trained | Owners | Proof |
|---|---|---|---|---|---|
| **1** (on-chain 9) | Clinical · inheritance pattern and genes for rare diseases | Qwen2.5-1.5B-Instruct | **inheritance right 3/12 → 10/12**, gene 3/12 → 5/12; hidden-test loss 1.456 → 1.228 | metabolic-clinic 61.8%, alice 38.2% (neuro-clinic 0%, bob 0%) | rounds [`7rwzFf68…`](https://nearblocks.io/txns/7rwzFf685GbR6NVUXRLf45pEm3PvQfom5nS7tXdR24T8), [`Fq34bkEi…`](https://nearblocks.io/txns/Fq34bkEix9YEhybUhyPKQCNQtJ1QHVzEQvUPruTCDfMv) · [record](runs/20261114-mainnet-model9-clinical-tee/summary.md) |
| **2** (on-chain 7) | Cybersecurity · vulnerability classification | Qwen3-1.7B | **right weakness type 2/24 → 12/24**; hidden-test accuracy 2/30 → 12/30 | web-hunter 65%, memory-hunter 35% (auth-hunter 0%, bob 0%) | round [`E5u2LEVn…`](https://nearblocks.io/txns/E5u2LEVnRozLhwJmkLN6iYvSrnE3c9JyczyTrN2mGxgo) · [record](runs/20261114-mainnet-model7-cyber-tee/summary.md) |
| **3** (on-chain 8) | Language · Basque native | Qwen3-1.7B | **translation score (chrF) 17.8 → 27.7** on 24 sentences nobody trained on | itziar 63.4%, ane 19.6%, mikel 17.0% (bob 0%) | round [`Fk6wrM2e…`](https://nearblocks.io/txns/Fk6wrM2eUU21nV6mzEtdsydfbTgjQgegEoqE6Tk3Gd1w) · [record](runs/20261114-mainnet-model8-basque-tee/summary.md) |
| **4** (on-chain 4) | Clinical · same topic, small test model | SmolLM2-135M-Instruct | hidden-test loss 1.891 → 1.647 | alice 45.8%, neuro-clinic 28.3%, metabolic-clinic 25.9% (bob 0%) | round [`HmeSHkg2…`](https://nearblocks.io/txns/HmeSHkg2encGsDZgfvzkAKweETp4NtVv2h5SJAd3voED) · [record](runs/20261113-mainnet-model4-tee-smollm135m/summary.md) |

In every run a deliberate cheater (`bob`: spam answers, wrong labels, or English pasted back as "Basque") earned 0%.
Each model answered paid questions on mainnet, and every payment was split by the contract. Per question, the original
model was right where the Axon model was wrong once in 24 questions for model 1 and never for models 2 and 3; the Axon
model was right where the original was wrong 10 times for models 1 and 2.

**NEAR AI Cloud, proven separately.** The data-prep step runs on NEAR AI Cloud: on fictional clinic notes it produced 16
to 20 training pairs in about 25 seconds, with every name, place and record number removed, and all 17 attestation and
signature checks passed ([evidence](runs/nearai-cloud/)). Try it live on any model's Join page on https://axon.surf,
which shows a **Verified** panel with every check. The mainnet runs above used public data that was already in
question/answer form, so they did not need this step.

## 3. Why NEAR

Axon needs four things from a chain, and NEAR provides all of them:

* **Micro-payments on every question.** Each inference is paid on-chain (0.01 NEAR in the demos) and split among the
  owners in the same transaction. NEAR's low fees and fast finality make paying per question practical: a
  `pay_for_query` on mainnet burned 0.00024 NEAR of gas (2.6 Tgas) and settled in seconds.
* **A contract that checks signatures itself.** The contract verifies the vault's ed25519 signature on every round
  (`env::ed25519_verify`), so ownership can only change through results signed inside the TEE.
* **Readable accounts and keys.** Owners are named accounts (`itziar.axon.ebukaa.near`), organisations get
  sub-accounts, contributors register device keys, and creators authorise actions with NEP-413 signed messages, with no
  transaction or fee. Sign-in is a NEAR wallet (Meteor, MyNEARWallet, HOT).
* **Private AI in the same ecosystem.** **NEAR AI Cloud** runs open models inside TEEs (Intel TDX + NVIDIA confidential
  GPUs) with per-request attestation and signed answers. Axon uses it to turn contributors' raw notes into training
  data without exposing them, and its scoring vault runs on **dstack**, the same open TEE stack NEAR AI Cloud is built
  on. **NEAR Intents** lets users pay with any token on any chain and settles to NEAR for the owners.

## 4. How it works

| Step | What happens | Where in the code |
|---|---|---|
| 1. Create a model | A creator picks a niche and a free open base model, funds a small compute budget, and binds the model on-chain to the vault's signing key and code hash. They hand the vault a hidden test set, sealed in their browser and signed by their wallet (NEP-413). | `contract` `create_model`, `web/app.js`, `axon/vault.py` `set_test` |
| 2. Join | Each contributor registers a device key on NEAR. | `contract` `join_model`, `axon/contribute.py` |
| 3. Prepare the data | Contributors whose data is already question/answer pairs skip this. Others send raw records (case notes, incident reports, messages) to an open model (Qwen3.8-27B) running in **NEAR AI Cloud's TEE**, which removes personal details and writes training pairs. Axon verifies the TEE's attestation with a fresh nonce **before** sending anything, checks the answer's signature, and stores nothing. | `axon/nearai.py`, `axon prep` |
| 4. Train locally | The contributor fine-tunes a small LoRA adapter **on their own machine**. The training data never leaves it. The base model and adapter shape are read from the chain and the vault. | `axon/ml.py` `Engine.train` |
| 5. Send a sealed update | Only the adapter is sent, signed by the device key and encrypted (X25519 sealed box) so only the vault can open it. | `axon/crypto.py`, `axon/contribute.py` |
| 6. Merge and score | Inside the TEE, the vault averages the adapters (FedAvg) and scores each contributor by **Shapley value**: their average marginal improvement on the hidden test across every group of contributors. Updates that make the model worse, or add nothing next to the others, are left out and earn nothing. | `axon/ml.py` `score_round` |
| 7. Record ownership | The vault signs the result inside the TEE. The contract checks the ed25519 signature against the model's registered vault key, rejects replays and unknown accounts, and mints shares equal to measured improvement. Compute providers get a fixed fee, never ownership. | `contract` `submit_round` |
| 8. Ask and pay | Anyone pays to ask a question. The payment carries `sha256(question)`, so it buys one answer to that one question. The contract takes 5% for Axon and splits 95% to owners by share. The same question can also be answered by the original open model, side by side. | `contract` `pay_for_query`, `axon/vault.py` `answer` |
| 9. Withdraw | Owners withdraw their earnings any time, from the site or the CLI. | `contract` `withdraw` |

**Scoring per niche.** Clinical uses answer-token loss on the hidden test. For classification and translation, loss
rewarded answer *format* (a cheater with wrong labels scored highest in a tuning run), so those niches are scored by
hidden-test **accuracy** (cybersecurity) and **chrF** (Basque). See `axon/data.py` `metric_fn`.

## 5. Privacy: what is protected, and how

| Stage | Protection | Technology |
|---|---|---|
| Preparing raw records (optional) | Records go only to an attested TEE, which removes personal details and keeps nothing; the answer is signed by the attested key | **NEAR AI Cloud**: Intel TDX + NVIDIA confidential-computing GPUs, attestation verified with a fresh nonce before sending |
| Training | The training data never leaves the contributor's machine; only a sealed adapter does | Federated fine-tuning (LoRA), X25519 sealed boxes, ed25519 device keys |
| Scoring and the hidden test | Done inside sealed hardware nobody can look into, including us; anyone can verify which code runs there | **TEE: Intel TDX with dstack** (the open TEE stack NEAR AI Cloud also runs on), hosted on Phala Cloud; production OS, image pinned by digest and built by CI from this repo; training settings written into the measured configuration |
| Ownership | Only results signed by the model's registered vault key count | NEAR contract, `env::ed25519_verify` |
| Hidden test hand-over | Only the creator can set it, once, sealed so only the TEE can read it | NEP-413 signed message + on-chain access-key check |
| Using the model | Weights are never published; the model answers only paid questions; the question itself never goes on-chain, only its hash | Vault access rules below, `pay_for_query` |

**What Axon checks before NEAR AI Cloud sees any data** (`axon/nearai.py`, following
[docs.near.ai/cloud/verification](https://docs.near.ai/cloud/verification)). If any check fails, nothing is sent.

| Check | How |
|---|---|
| The gateway and the model run in genuine Intel TDX | both hardware quotes verified against Intel's certificate chain (`dcap-qvl`); neither is in debug mode |
| The quotes are fresh and belong to the keys that sign answers | each quote's report_data = its signing address ‖ our random 32-byte nonce |
| The software inside is the published one | sha256(app_compose) equals the quote's MRCONFIGID |
| The GPUs are genuine NVIDIA confidential-computing GPUs | NVIDIA's attestation service (NRAS) verdict, for our nonce |
| The answer came from that model, unaltered | ECDSA signature by the attested model key over sha256(our exact request) and sha256(the exact response) |

**Check the scoring TEE yourself.** `scripts/verify_tee.py` checks that (1) the vault's code hash equals this repo's
code at the commit it ran, (2) Intel's hardware quote binds the vault's signing key to that code hash, (3) the quote is
genuine Intel TDX, and (4) the NEAR model accepts only that key. It works offline from the saved evidence:

```bash
git worktree add /tmp/axon-tee 1012ba3        # the exact commit the TEE ran for models 1-3 (on-chain 9, 7, 8)
cd /tmp/axon-tee && AXON_NETWORK=mainnet AXON_CONTRACT=axon.ebukaa.near \
  python scripts/verify_tee.py <this repo>/runs/tee-mainnet2/vault-info-20261114.json --model 9
# 1. code hash -> OK   2. quote binds key + code hash -> OK   3. genuine Intel TDX -> OK   4. model 9 -> OK
# Model 4: commit af804dc with runs/tee-mainnet/vault-info-20261113.json --model 4
```

Each model page on the site has a **Verified** panel that re-checks the vault's Intel quote now, recomputes the
key-and-code binding in the browser, and reads the model's binding live from NEAR.

### Vault access rules

| Endpoint | Who may call it | Enforced by |
|---|---|---|
| `POST /models/{id}/updates` | joined contributors | device-key signature checked against the key registered on-chain |
| `GET /models/{id}/global` (shared adapter, for local training) | joined contributors only | device-key signature over `model:account:timestamp`, valid 5 minutes |
| `POST /models/{id}/test` (hidden test set) | the model's creator, once, before round 1 | NEP-413 wallet signature over the model id and the sealed file's sha256; key must be a full-access key of the creator |
| `POST /models/{id}/close-round` | the vault operator | bearer token, sealed into the TEE |
| `POST /models/{id}/ask` | anyone with a payment | on-chain `pay_for_query`: signed by the payer, to this contract and model, with this question's hash, never used before |

## 6. How NEAR is used

| NEAR technology | Role in Axon | Code |
|---|---|---|
| **Smart contract (Rust, near-sdk 5)** on mainnet | Ownership ledger: models, device keys, vault-signed rounds, Shapley shares, O(1) revenue split, 5% platform fee, compute-fee budget, withdrawals. 21 unit tests. | `contract/src/lib.rs`, `contract/src/tests.rs` |
| **NEAR AI Cloud** | Private data preparation: raw records become training pairs inside a TEE (Intel TDX + NVIDIA confidential GPUs); Axon verifies the attestation with a fresh nonce before sending and checks every signed answer. | `axon/nearai.py`, `web/api/prep.py` |
| **On-chain ed25519 verification** | Only results signed by the model's registered vault key are accepted; forged, tampered or replayed rounds are rejected. | `submit_round` |
| **Named accounts + sub-accounts** | Owners are readable accounts (`itziar.axon.ebukaa.near`); device keys bind updates to them. | `join_model` |
| **NEAR Wallet Selector** (Meteor, MyNEARWallet, HOT) | Sign-up, paying for questions, withdrawing, creating models from the browser. | `web/wallet.js` |
| **NEP-413 signed messages** | The creator's wallet authorises the hidden-test hand-over, with no transaction or fee. | `axon/crypto.py` `verify_nep413` |
| **NEAR Intents (1Click)** | Pay for a question with USDC, SOL, ETH, BTC; it settles to NEAR for the owners. Built; the demo payments were made in NEAR. | `axon/intents.py`, `axon/app.py` |
| **TEE (Intel TDX, dstack)** | The scoring vault runs in a confidential VM on the same open stack as NEAR AI Cloud; its key is derived inside the TEE and bound to its code by the hardware quote. | `axon/tee.py`, `deploy/phala.sh`, `docker-compose.yml`, `Dockerfile` |

## 7. Use it

- **Website:** browse the models, try them on the Demo page, connect a wallet, see and withdraw earnings, prepare raw
  notes on NEAR AI Cloud from a model's Join page.
- **With your AI assistant:** hand it [`AGENT_SETUP.md`](AGENT_SETUP.md). It never asks for keys in chat and keeps your
  data on your machine.
- **CLI:** contributing needs an NVIDIA GPU with 12 GB+ for the 1.5B to 1.7B models.

```bash
git clone https://github.com/haileymarshall/axon.git && cd axon
python3 -m venv .venv && .venv/bin/pip install torch && .venv/bin/pip install -r requirements.txt
export AXON_NETWORK=mainnet AXON_CONTRACT=axon.ebukaa.near AXON_VAULT_URL=<vault address>
.venv/bin/python -m axon status --model 9
.venv/bin/python -m axon prep ~/my-notes.txt --niche rare-diseases --out ~/my-axon-data.jsonl   # only if you have raw notes
.venv/bin/python -m axon contribute --model 9 --account <you>.near --data ~/my-axon-data.jsonl
.venv/bin/python -m axon ask --model 8 --account <you>.near "Translate into Basque: Good morning."
.venv/bin/python -m axon withdraw --model 9 --account <you>.near
```

Training data: one JSON object per line, `{"q": "...", "a": "..."}`, read locally and never uploaded. `axon prep`
writes this format; it needs your NEAR AI Cloud key in `~/.nearai_key` or `NEARAI_API_KEY`. Try it with the fictional
`samples/clinic-notes.txt`, `samples/security-reports.txt` or `samples/basque-notes.txt`, and read the pairs before
training on them.

## 8. Run and check it yourself

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

**Reproduce a TEE run:** deploy the vault with `deploy/phala.sh <image@sha256:digest>`, create the model with
`axon create-model --base-model …`, seal its hidden test with `axon set-test`, then run `scripts/demo.sh` against the
TEE vault's URL with the settings in the run's `env.json`. `scripts/fetch_adapter.py` downloads a trained adapter the
way a contributor does and checks it against the on-chain hash.

## 9. Found and fixed

Running for real exposed problems no unit test had. Each fix is in the code, with tests where possible.

| Problem | Fix |
|---|---|
| Vault and training on one 24 GB GPU ran out of memory | Vault holds the base model in bf16; training uses gradient checkpointing |
| Vault dropped the updates and advanced its model before the chain accepted the round | The vault's model only moves forward once the round is on-chain; updates are kept on failure |
| A contributor was merged into the model but got a 0% share | Re-score among the kept updates and drop the least useful one until every merged update owns a share |
| Rounds that made the model worse were accepted | Rejected: model unchanged, no shares |
| Loss rewarded answer format, so a cheater with wrong labels scored highest | Classification and translation niches are scored by accuracy and chrF |
| Duplicate descriptions in NVD leaked test questions into training | De-duplicated, disjoint splits, a leakage test |
| `rpc.mainnet.near.org` deprecated; FastNEAR rate-limits the TEE's shared IP; py-near's HTTP client fails inside the TEE | Endpoint rotation; transactions are signed locally and broadcast over HTTPS, resending the same signed bytes so nothing executes twice |
| The test-set upload trusted the claimed creator | NEP-413 wallet signature + on-chain full-access-key check |
| Training settings lived outside the TEE's measurement | Written as literals into the measured compose file |
| `create-model` took the vault's default base model | `--base-model` flag; two models created on the wrong base were closed |
| Scoring a 1.7B model on TEE CPUs outlasts the gateway's request timeout | The vault finishes and records the round itself; `axon round-result` waits for it on-chain |
| Data prep took 2 minutes and sometimes covered only the first note | Reasoning off for this task (about 25 s); the prompt requires pairs for every record |

## 10. Limitations

- **Demo data is public data standing in for private data** (NIH MedQuAD, NIST NVD, Tatoeba), and all contributors of a
  run were simulated on one machine. All demo accounts are sub-accounts of `axon.ebukaa.near`.
- **Live answers on the Demo page are served from a GPU server during judging,** not from the TEE, to keep costs low.
  It serves exactly the model the TEE recorded: each adapter's sha256 equals the hash on NEAR.
- **Gains are real but modest**, and the models are small (1.5B to 1.7B): they still make mistakes. Clinical answers are
  not medical advice.
- **Data prep sends raw records out of the machine**, into NEAR AI Cloud's attested TEE. Contributors who write their
  own pairs send nothing. The website demo relays through a stateless function that is not itself a TEE: use it with
  the fictional samples, and `axon prep` with your own key for real records. The pairs are written by a model, so
  review them before training.
- **Contributors download the shared adapter** to train on it, so a contributor could copy it. Training inside the TEE
  would remove this.
- **Model updates can leak some information** about training data; differential privacy and secure aggregation are next.
- **Exact Shapley** needs 2^n evaluations (up to 8 contributors per round); larger rounds need sampling. Hidden tests are
  small (24 to 30 questions), so scores are noisy.
- **Contributing needs an NVIDIA GPU and a terminal** today; `AGENT_SETUP.md` helps, a desktop app would help more.
- The contract is not audited, and its wasm build is not reproducible (no Docker build). Built from commit `87a3d74`:
  wasm sha256 `b85179386605769bcf9735298902180a6078724d728cea9578fa5370a8adca18`, on-chain code hash
  `DQW5B93EWpx1X3CRiDw8FkxcdLiY5QFC6xA55o2yRacf`.

## 11. Repository map

```
contract/            NEAR contract (Rust): models, device keys, signed rounds, shares, 5% fee, revenue split, withdrawals + 21 tests
axon/nearai.py       data prep on NEAR AI Cloud: attestation (TDX quotes, nonce, compose hash, NVIDIA GPUs), signed answers
axon/ml.py           LoRA fine-tuning, FedAvg merging, exact Shapley scoring with exclusion rules, evaluation, generation
axon/vault.py        the vault: decrypt + verify updates, score, sign, sealed test sets, paid answers, several base models
axon/contribute.py   contributor client: join on-chain, train locally, sign + seal the update
axon/crypto.py       ed25519 / X25519, sealed boxes, NEP-413 verification
axon/chain.py        NEAR RPC with endpoint rotation; local signing and safe re-broadcast
axon/data.py         the three demo niches (rare diseases, cyber, Basque), test questions, grading, per-niche metrics
axon/tee.py          TEE key derivation and attestation (dstack)
axon/intents.py      NEAR Intents 1Click quotes and status
axon/app.py          web backend (paid and free demo questions); web/ is the site
web/api/             stateless functions: data prep on NEAR AI Cloud (prep.py), live check of a vault's TEE quote (tee.py)
scripts/             setup, demo, runs, verify_tee.py, fetch_adapter.py, build_site.py
deploy/, Dockerfile  TEE deployment (Phala, image pinned by digest; built by .github/workflows/vault-image.yml)
samples/             fictional raw records for trying `axon prep`
runs/                every run's record; runs/tee-mainnet*/ hold the TEE evidence
AGENT_SETUP.md       setup guide for AI assistants
```

## 12. Credits and licences

Base models: Qwen2.5-1.5B-Instruct and Qwen3-1.7B (Alibaba, Apache-2.0), SmolLM2-135M-Instruct (Hugging Face,
Apache-2.0). Data prep model: Qwen3.8-27B on NEAR AI Cloud. Data: MedQuAD (NIH, CC BY 4.0), National Vulnerability
Database (NIST, public domain), Tatoeba (CC BY 2.0 FR). Libraries: PyTorch, Hugging Face transformers and PEFT, PyNaCl,
py-near, FastAPI, near-sdk, NEAR Wallet Selector, libsodium, dcap-qvl, eth-account. TEE: dstack on Phala Cloud. GPUs:
Vast.ai.

## 13. Hackathon disclosure

 AI coding assistants were used minimally  during development. Libraries and data used are listed in section 12.

## License

MIT
