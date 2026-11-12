# Axon

**Train AI together on private data. Own what it becomes.**

Big Tech trains AI on people's data for free. Axon lets people and organisations train a model *together*
without ever sharing their data, gives each of them ownership of the model in proportion to how much their
data actually improved it, and pays them automatically every time the model is used. Ownership, scoring
proofs and payouts live on **NEAR**; payments come from **any token on any chain via NEAR Intents**.

> Built at NEAR HACKATHON (1 to 14 Nov 2026). Tracks: `privacy`, `open`.

---

## 1. The problem

The data that would make AI useful for health, finance, law or science is locked in silos:
a clinic has 200 cases of a disease, a person has years of their own health records, a lab has its failed
experiments. Nobody can share it (privacy law, competition, trust), so:

* each holder has too little data to train a good model alone,
* the people whose data creates the value never own any of the result,
* the models that do get built are owned by the few companies that can hoover up data.

## 2. What Axon does

| Step | What happens | Where |
|---|---|---|
| 1. Create a model | A creator picks an open base model and a topic, funds a compute budget, and binds the model on-chain to the vault's signing key and code hash. | `contract` `create_model` |
| 2. Join | Each contributor registers a device key on NEAR (`join_model`). | `contract`, `axon/contribute.py` |
| 3. Train locally | The contributor fine-tunes the current shared model (a LoRA adapter) **on their own machine**. Raw data never leaves it. | `axon/ml.py` `Engine.train` |
| 4. Send a sealed update | Only the adapter is sent, **signed** by the device key and **encrypted** (X25519 sealed box) so only the vault can open it. | `axon/crypto.py` |
| 5. Merge and score | The vault (designed to run in a TEE) merges updates (federated averaging) and scores each contributor by its **Shapley value**: its average marginal improvement on a **hidden test set** across every possible group of contributors. Updates that make the model worse are dropped and earn nothing. | `axon/ml.py` `score_round` |
| 6. Record ownership | The vault signs the round result; the contract verifies the ed25519 signature against the registered key, rejects replays, and mints ownership shares equal to measured improvement. GPU providers get a fixed fee, **not** ownership. | `contract` `submit_round` |
| 7. Use and pay | Anyone asks the model a question and pays with any token via **NEAR Intents** (or NEAR directly). The payment carries `sha256(question)`, so it buys an answer to that one question only. It goes to the contract and is split pro-rata to owners in O(1). | `axon/intents.py`, `contract` `pay_for_query` |
| 8. Withdraw | Owners withdraw their earnings at any time. | `contract` `withdraw` |

The model itself stays inside the vault and is only reachable through paid queries, so it cannot be copied
for free; only its hash is public.

### Vault access rules

| Endpoint | Who may call it | Enforced by |
|---|---|---|
| `POST /models/{id}/updates` | joined contributors | device-key signature checked against the key registered on-chain |
| `GET /models/{id}/global` (shared adapter, for local training) | joined contributors only | device-key signature over `model:account:timestamp`, valid 5 minutes |
| `POST /models/{id}/close-round` | the vault operator | bearer token (`AXON_VAULT_TOKEN`) |
| `POST /models/{id}/ask` | anyone with a payment | on-chain `pay_for_query` tx: signed by the payer, to this contract and model, with this question's hash, never used before (reserved atomically) |

## 3. How NEAR is used

| NEAR technology | Role in Axon | Code |
|---|---|---|
| **Smart contract (Rust, near-sdk 5)** | Ownership ledger: models, contributors' device keys, signed rounds, shares, revenue accumulator, compute-fee budget, withdrawals. 18 unit tests. | `contract/src/lib.rs`, `contract/src/tests.rs` |
| **On-chain ed25519 verification** (`env::ed25519_verify`) | Only results signed by the model's registered vault key are accepted; a tampered or forged payload is rejected. | `submit_round` |
| **Named accounts** | Owners are human-readable accounts (`alice.…testnet`); device keys bind updates to them. | `join_model` |
| **NEAR Intents (1Click API)** | Pay for a query with USDC on Base/Solana/Arbitrum/Ethereum, SOL, ETH, BTC or NEAR; it settles as wNEAR to the Axon treasury, which records it on-chain with its cross-chain origin. | `axon/intents.py`, `axon/app.py` |
| **Confidential Intents** | Supported via `confidentiality: basic` when a 1Click partner key is set (`AXON_INTENTS_JWT`), so payment trails stay private. | `axon/intents.py` |
| **TEE / Shade Agent pattern** | The vault is the component meant to run in a TEE: the contract trusts only its key, which is bound to `combiner_code_hash` (the hash of the vault's code). See §7 for current status. | `axon/vault.py` |

## 4. Try it (laptop, CPU only, about 25 minutes for the full loop)

Requires Python 3.10+, about 3 GB of RAM and internet access (downloads a 135M-parameter open model and the demo data).

```bash
git clone <this repo> axon && cd axon
./scripts/setup.sh                     # venv + deps + demo data (data/contributors/*.jsonl, data/vault/test.jsonl)
.venv/bin/python -m pytest -q tests    # 10 tests, about 10 s
(cd contract && cargo test)            # 18 contract tests (needs Rust)
```

**Run the whole loop against the deployed testnet contract** (needs testnet accounts; `./scripts/setup.sh --deploy`
creates a fresh contract and the 7 demo accounts through the faucet and prints the env to export):

```bash
source .env.testnet                                   # AXON_CONTRACT=..., AXON_PARENT=...
.venv/bin/python -m axon vault --operator vault.$AXON_PARENT &     # the sealed combiner
./scripts/demo.sh                                     # create model -> 2 rounds x 4 contributors -> paid question -> owners
.venv/bin/python -m axon app --demo-payer user.$AXON_PARENT        # web app on http://127.0.0.1:8800
```

**What you should see**

* `close-round` prints each contributor's Shapley score. **bob** (who submits word-salad spam) gets `0`
  shares and is excluded from the merged model; alice and the two clinics split ownership.
* The hidden-test loss goes down every round (shown on the model page chart).
* `axon ask` pays 0.01 NEAR on-chain and returns an answer from the vault; `axon status` shows each owner's
  earnings increase in proportion to their shares.
* In the web app: the **Models** page shows the live model; its page shows owners, the ownership bar, loss curve,
  rounds, and lets you ask a question paid in testnet NEAR or via NEAR Intents.

**Deployed (testnet):** contract `axon-hq-56501.testnet`
([explorer](https://testnet.nearblocks.io/address/axon-hq-56501.testnet)).

### GPU mode

Same code, bigger model and longer training, for better answers:

```bash
AXON_BASE_MODEL=Qwen/Qwen2.5-1.5B-Instruct AXON_LOCAL_STEPS=60 AXON_MAX_LEN=384 python -m axon vault ...
```

### Published training runs

Every training run is recorded and published in [`RUNS.md`](RUNS.md), each with its own folder in `runs/`:
hardware (GPU model from `nvidia-smi`), config, the full log, per-round hidden-test loss, each contributor's Shapley
shares, on-chain transaction hashes, and the same questions answered by the base model and by the Axon-trained model.

```bash
./scripts/run.sh          # runs the demo loop and writes runs/<date>-<device>/ + a row in RUNS.md
```

## 5. Repository map

```
contract/          NEAR contract (Rust): ownership, signed rounds, revenue split, withdrawals + tests
axon/ml.py         LoRA fine-tuning, federated averaging, exact Shapley scoring, evaluation, generation
axon/vault.py      the sealed combiner service (decrypt, verify, score, sign, answer paid queries)
axon/contribute.py contributor client (join on-chain, train locally, sign + seal the update)
axon/crypto.py     ed25519 device/vault keys, X25519 sealed boxes
axon/chain.py      NEAR RPC views + signed function calls
axon/intents.py    NEAR Intents 1Click quotes and status (incl. confidential mode)
axon/app.py        web app backend; web/ is the front end (no build step)
axon/runs.py       published run records (runs/, RUNS.md)
axon/data.py       demo data: MedQuAD (NIH health Q&A, CC BY 4.0) split into private contributor files
scripts/           setup.sh, demo.sh, run.sh (recorded run)
runs/, RUNS.md     every training run, published
tests/             Python tests (aggregation, Shapley, sealing, signatures)
```

## 6. Demo scenario

The platform is general (any group with private data: banks pooling fraud signals, exchanges pooling scam
reports, labs pooling compound results). The demo shows one concrete case, a **user-owned health assistant**:

| Contributor | Private data (simulated from public MedQuAD) | Expected outcome |
|---|---|---|
| alice (a person) | diabetes questions and answers | earns shares |
| heart-clinic | cardiology Q&A | earns shares |
| onco-clinic | oncology Q&A | earns shares |
| bob | spam: real questions with word-salad answers | 0 shares, excluded |

The hidden test set mixes all three topics and exists only inside the vault.

## 7. Honest limitations (v0)

* **TEE:** the vault runs as a normal process in this repo; its attestation is self-reported
  (`attestation.mode = "local"`). The contract already enforces "only the registered key, bound to this code
  hash", which is the check a Shade Agent / confidential-VM deployment plugs into.
* **Weights reach contributors:** contributors download the current shared adapter to train on it. Fine for
  members; a production version would train inside TEEs too.
* **Update leakage:** model updates can leak some information about training data. Next step: differential privacy noise
  on updates and secure aggregation inside the TEE.
* **Scale:** exact Shapley needs 2^n evaluations per round (n ≤ 8 here); larger rounds need Monte Carlo
  Shapley.
* **Toy model:** laptop mode uses a 135M model so judges can run it on CPU; answers are not medical advice.
* **Testnet + Intents:** Intents only runs on mainnet. On testnet, an Intents payment settles to the treasury on
  mainnet and the treasury records it on the testnet contract; on a mainnet deployment both are on one chain.

## 8. Hackathon disclosure

All code in this repository was written during the NEAR HACKATHON window (November 2026). Third-party
libraries: PyTorch, Hugging Face transformers and PEFT, PyNaCl, py-near, FastAPI, near-sdk. Base model:
SmolLM2-135M-Instruct (Apache-2.0). Data: MedQuAD (CC BY 4.0). AI coding tools were used.

## License

MIT
