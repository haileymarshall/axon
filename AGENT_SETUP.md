# Axon setup guide for AI agents

> **For people:** you don't need to read this. Give this file to your AI assistant (Claude, ChatGPT, Cursor,
> Copilot, any agent that can run terminal commands) and say: *"Help me set up Axon. Follow AGENT_SETUP.md."*
> It will ask what you want to do and walk you through it.

---

## To the agent: what Axon is

Axon lets individuals and small companies fine-tune a free open AI model (e.g. Qwen) into an expert in one
niche, using their private data **without revealing it**. Each contributor trains a small adapter on their own
machine and sends only a sealed update. A vault scores how much each update improved the model. A NEAR smart
contract records who owns what share and splits every paid question: 95% to the owners, 5% to Axon.

Live contract: **`axon.ebukaa.near`** on NEAR **mainnet**. Models on it today:

| id | Model | Niche | Base model |
|---|---|---|---|
| 1 | Rare Disease Expert | `rare-diseases` | Qwen/Qwen2.5-1.5B-Instruct |
| 2 | Vulnerability Classifier | `security` | Qwen/Qwen3-1.7B |
| 3 | Basque Translator | `basque` | Qwen/Qwen3-1.7B |
| 4 | Rare Disease Expert (TEE) | `rare-diseases` | HuggingFaceTB/SmolLM2-135M-Instruct (its vault runs in a TEE) |

(Model 0 is an earlier run kept as history. Run `status` in step 3 to see the current list.)

## Rules you must follow

1. **Never ask the user to paste a private key, seed phrase or API token into the chat.** Keys go into files
   on their machine through the commands below (the NEAR CLI asks for them in the terminal, not in chat).
2. **Their data never leaves their machine.** Do not upload it, paste it into chat, or send it anywhere. Only
   the `contribute` command reads it, locally.
3. **Ask before anything that spends money** (NEAR transactions, renting a GPU). Say how much first.
4. Explain each step in one plain sentence before running it. The user may not be technical.
5. If a step fails, read the error, check the troubleshooting table at the end, and explain what went wrong.

## Step 0: ask the user what they want

Ask one question: **"What would you like to do?"**

| They say | Go to |
|---|---|
| "Try it first, without real money" | **Path E** (testnet, laptop only) |
| "Contribute my data to a model and earn from it" | Steps 1 to 3, then **Path A** |
| "Ask a model a question" | **Path B** (no install needed on the website) |
| "See or withdraw my earnings" | Steps 1 to 3, then **Path D** |
| "Start a new model for my own niche" | Steps 1 to 3, then **Path C** |

## Step 1: check the machine

```bash
python3 --version        # need 3.10 or newer
git --version
nvidia-smi               # an NVIDIA GPU with 12 GB+ memory is needed to train the 1.5B-1.7B models
```

- **No NVIDIA GPU?** They can still do Paths B, D and E. For Path A they can rent one by the hour
  (e.g. an RTX 3090 or 4090 on vast.ai or runpod.io, about $0.15 to $0.40/hour; one contribution takes about 10
  minutes of training). Apple Silicon and CPU-only machines are too slow to train these models.
- Disk: about 10 GB free (the base model downloads once, about 3.5 GB).

## Step 2: install Axon

```bash
git clone https://github.com/haileymarshall/axon.git
cd axon
python3 -m venv .venv
# On a machine WITH an NVIDIA GPU, install the GPU build of PyTorch first:
.venv/bin/pip install torch
# Then the rest:
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q tests      # should end with "passed"
```

Install the NEAR command-line tool (it stores keys safely on this machine):

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/near/near-cli-rs/releases/latest/download/near-cli-rs-installer.sh | sh
near --version
```

## Step 3: connect a NEAR account

The user needs a NEAR **mainnet** account with a little NEAR (0.1 NEAR is plenty for contributing; each
transaction costs about 0.001 NEAR). If they have none, they can create one in a wallet such as
[Meteor](https://wallet.meteorwallet.app), [HOT](https://hot-labs.org) or [MyNEARWallet](https://app.mynearwallet.com)
and buy or receive a little NEAR.

Import it into the NEAR CLI. **The user types their seed phrase or private key into the terminal prompt, not
into chat:**

```bash
near account import-account using-seed-phrase network-config mainnet
# or: near account import-account using-private-key network-config mainnet
```

Choose **"legacy keychain"** when asked where to save. Check it worked (replace with their account):

```bash
ls ~/.near-credentials/mainnet/            # should list <their-account>.json
```

Then set these for every Axon command in this terminal:

```bash
export AXON_NETWORK=mainnet AXON_CONTRACT=axon.ebukaa.near
export AXON_VAULT_URL=<vault address>      # see "Where is the vault?" below
.venv/bin/python -m axon status --model 1  # shows the model, its owners and their earnings
```

**Where is the vault?** The vault holds the models and scores contributions. Its address is shown on the
website's model pages and in the README ("Live vault"). It is only online at certain times (it runs on a rented
GPU). If it is offline, Paths A and B wait until it is back; Path D always works.

## Path A: contribute your data and earn a share

1. **Pick a model** whose niche matches their data (`status --model <id>` for each). Their data must be about
   that niche: data that does not improve the model earns nothing (that is how Axon keeps junk out).
2. **Turn their data into a file** with one JSON object per line: a question and the answer they know is right.
   Keep it on their machine, e.g. `~/my-axon-data.jsonl`:

   ```json
   {"q": "How is Rothmund-Thomson syndrome passed down in families?", "a": "This condition is inherited in an autosomal recessive pattern ..."}
   {"q": "Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.\n\nVulnerability: <description>", "a": "CWE-79: Cross-site Scripting (XSS)."}
   {"q": "Translate into Basque: The train arrived on time.", "a": "Trena garaiz iritsi zen."}
   ```

   Help them convert what they have (CSV, notes, a spreadsheet) with a short local script. Use the **same
   question wording** as the examples above for that model. 100 to 600 good examples is a good size.
3. **Train and send** (about 10 minutes on a GPU; the first run also downloads the base model):

   ```bash
   .venv/bin/python -m axon contribute --model <id> --account <their-account> --data ~/my-axon-data.jsonl
   ```

   This registers a device key on-chain the first time (about 0.001 NEAR), downloads the current shared model,
   **trains on their file locally**, then signs and seals only the adapter (the learned weights, about 70 MB) so
   that only the vault can open it. The base model and adapter shape are picked automatically.
4. **Wait for the round to close.** The model's operator closes rounds; the vault then scores every update on a
   hidden test and records shares on NEAR. Check with `status --model <id>`. A share of `0%` means the data
   did not improve the model next to the others' (it is left out of the model, not merged for free).

## Path B: ask a model a question

- **Website (easiest):** open the Axon site, pick a model, type a question, tick **"Compare with the original
  open model"** to see the free base model's answer next to the Axon-trained one. Pay 0.01 NEAR, or any token
  through NEAR Intents.
- **Terminal:** `.venv/bin/python -m axon ask --model <id> --account <their-account> "Translate into Basque: Good morning."`
  pays 0.01 NEAR on-chain and prints the answer.

## Path C: start a model for a new niche

Creating a model binds it to a running vault's key, so they need a vault (run `python -m axon vault` on a GPU
machine, or ask the Axon team to host it). Then:

```bash
.venv/bin/python -m axon create-model --creator <their-account> --name "My Niche Model" --domain my-niche \
  --description "What it does and who trains it" --price 0.01 --compute-fee 0.02 --budget 0.06
```

It needs a hidden test set for the niche (held only by the vault) and contributors. Point them to the README.

## Path D: check and withdraw earnings

```bash
.venv/bin/python -m axon status --model <id>                              # shares and earnings of every owner
.venv/bin/python -m axon withdraw --model <id> --account <their-account>  # sends their earnings to their wallet
```

## Path E: try everything on testnet, free, on a laptop

Uses a tiny 135M model so it runs on CPU, and free testnet NEAR.

```bash
./scripts/setup.sh --deploy       # creates a fresh testnet contract and demo accounts via the faucet
source .env.testnet
.venv/bin/python -m axon vault --operator vault.$AXON_PARENT &
./scripts/demo.sh                 # 4 contributors train, the vault scores them, a question is paid for
.venv/bin/python -m axon app --demo-payer user.$AXON_PARENT    # web app on http://127.0.0.1:8800
```

## Troubleshooting

| Error | What it means | Fix |
|---|---|---|
| `credentials not found` / `No such file ... .near-credentials` | The account is not imported for this network | Redo step 3; check `AXON_NETWORK` matches (mainnet vs testnet) |
| `NotEnoughBalance` | The account cannot cover gas | Add a little NEAR (0.05 is enough) |
| `vault refused the model download: 403` | The account has not joined, or the clock is off | Run `contribute` again (it joins first); check the computer's time is correct |
| `Connection refused` to the vault | The vault is offline | Wait until it is online (see the website); Path D still works |
| `CUDA out of memory` | GPU too small | Use a GPU with 12 GB+, or close other GPU programs |
| `model is closed` | The model no longer takes contributors | Pick another model |
| `vault rejected update: 400 adapter hash mismatch` | The upload was corrupted | Run `contribute` again |
| Training is extremely slow | No GPU in use (`nvidia-smi` fails or PyTorch is the CPU build) | Reinstall with `.venv/bin/pip install --force-reinstall torch` on a GPU machine |

## Words the user may ask about

- **Base model:** the free open AI model everyone starts from (e.g. Qwen). Nobody owns it.
- **Adapter:** the small set of learned weights that makes the base model an expert. This is what owners own.
- **Vault:** the service that merges and scores updates, designed to run inside a TEE (sealed hardware nobody,
  including the operator, can look into).
- **Shapley score:** a fair way to measure how much each contributor's data improved the model on a hidden test.
- **Share:** a contributor's part of the model, recorded on NEAR. It decides their cut of every paid question.
