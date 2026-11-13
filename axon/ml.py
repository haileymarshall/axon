"""Model side of Axon: LoRA fine-tuning, update aggregation and contribution scoring.

Every contributor trains a small LoRA adapter on top of the same open base model, starting from
the current global adapter. Only adapter weights ever leave the device - never the data.

The vault combines updates with federated averaging of adapter deltas and scores each contributor
by its Shapley value: its average marginal improvement of hidden-test loss over every possible
group of contributors. Updates that make the model worse are excluded and earn nothing, so junk or
poisoned data cannot buy ownership.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass

import torch
from peft import LoraConfig, get_peft_model, get_peft_model_state_dict, set_peft_model_state_dict
from safetensors.torch import load as st_load
from safetensors.torch import save as st_save
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import CFG

Adapter = dict[str, torch.Tensor]


@dataclass
class Example:
    input_ids: list[int]
    labels: list[int]


class Engine:
    """Holds one base model with a LoRA adapter slot; adapters are swapped in and out."""

    def __init__(self, base_model: str = CFG.base_model, seed: int = 0):
        torch.manual_seed(seed)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tok = AutoTokenizer.from_pretrained(base_model)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        base = AutoModelForCausalLM.from_pretrained(base_model, dtype=getattr(torch, CFG.dtype))
        cfg = LoraConfig(
            r=CFG.lora_rank,
            lora_alpha=CFG.lora_rank * 2,
            lora_dropout=0.0,
            target_modules=CFG.lora_targets.split(","),
            task_type="CAUSAL_LM",
        )
        if CFG.grad_ckpt:
            base.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
            base.enable_input_require_grads()
        self.model = get_peft_model(base, cfg).to(self.device)
        self.initial: Adapter = self.get_adapter()

    # ------------------------------------------------------------- adapters

    def get_adapter(self) -> Adapter:
        return {k: v.detach().cpu().clone() for k, v in get_peft_model_state_dict(self.model).items()}

    def set_adapter(self, adapter: Adapter) -> None:
        set_peft_model_state_dict(self.model, adapter)

    # ------------------------------------------------------------- data

    def encode(self, q: str, a: str) -> Example:
        prompt = self.tok.apply_chat_template([{"role": "user", "content": q}], tokenize=False, add_generation_prompt=True)
        p_ids = self.tok(prompt, add_special_tokens=False)["input_ids"]
        a_ids = self.tok(a + self.tok.eos_token, add_special_tokens=False)["input_ids"]
        ids = (p_ids + a_ids)[: CFG.max_len]
        labels = ([-100] * len(p_ids) + a_ids)[: CFG.max_len]
        return Example(ids, labels)

    def _batch(self, exs: list[Example]):
        n = max(len(e.input_ids) for e in exs)
        pad = self.tok.pad_token_id
        ids = torch.tensor([e.input_ids + [pad] * (n - len(e.input_ids)) for e in exs])
        labels = torch.tensor([e.labels + [-100] * (n - len(e.labels)) for e in exs])
        mask = torch.tensor([[1] * len(e.input_ids) + [0] * (n - len(e.input_ids)) for e in exs])
        return ids.to(self.device), labels.to(self.device), mask.to(self.device)

    # ------------------------------------------------------------- train / eval

    def train(self, rows: list[dict], start: Adapter, steps: int = CFG.local_steps, seed: int = 0, log=None) -> Adapter:
        """Fine-tune locally from `start`; returns the new adapter. Runs on the contributor's device."""
        self.set_adapter(start)
        rng = random.Random(seed)
        exs = [self.encode(r["q"], r["a"]) for r in rows]
        params = [p for p in self.model.parameters() if p.requires_grad]
        opt = torch.optim.AdamW(params, lr=CFG.lr, weight_decay=0.0)
        self.model.train()
        for step in range(steps):
            ids, labels, mask = self._batch(rng.sample(exs, min(CFG.batch_size, len(exs))))
            loss = self.model(input_ids=ids, attention_mask=mask, labels=labels).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            opt.zero_grad()
            if log and (step % 4 == 0 or step == steps - 1):
                log(step, loss.item())
        self.model.eval()
        return self.get_adapter()

    @torch.no_grad()
    def eval_loss(self, rows: list[dict], adapter: Adapter) -> float:
        """Mean per-token loss on answer tokens."""
        self.set_adapter(adapter)
        self.model.eval()
        exs = [self.encode(r["q"], r["a"]) for r in rows]
        total, count = 0.0, 0
        for i in range(0, len(exs), 8):
            ids, labels, mask = self._batch(exs[i: i + 8])
            logits = self.model(input_ids=ids, attention_mask=mask).logits[:, :-1]
            tgt = labels[:, 1:]
            nll = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1), ignore_index=-100, reduction="sum")
            total += float(nll)
            count += int((tgt != -100).sum())
        return total / max(count, 1)

    @torch.no_grad()
    def generate(self, question: str, adapter: Adapter, max_new_tokens: int = 120) -> str:
        self.set_adapter(adapter)
        self.model.eval()
        prompt = self.tok.apply_chat_template([{"role": "user", "content": question}], tokenize=False, add_generation_prompt=True)
        ids = self.tok(prompt, return_tensors="pt", add_special_tokens=False).to(self.device)
        out = self.model.generate(
            **ids, max_new_tokens=max_new_tokens, do_sample=False, repetition_penalty=1.15, use_cache=True,
            pad_token_id=self.tok.pad_token_id,
        )
        return self.tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()


# ----------------------------------------------------------------- aggregation & scoring


def aggregate(base: Adapter, updates: list[Adapter]) -> Adapter:
    """Merge contributors' adapters.

    "mean" (FedAvg) averages every tensor. With LoRA (W + B·A) and contributors holding different knowledge, that
    scales each contributor's change down to ~1/n, so specialist facts get washed out. "lora-sum" (default) averages
    A (which barely moves from its shared start) and adds up the B changes, so B·A ≈ base + the sum of every
    contributor's own change: each one's knowledge survives the merge. Shapley scoring still checks the result.
    """
    if not updates:
        return {k: v.clone() for k, v in base.items()}
    n = len(updates)
    if CFG.merge == "mean":
        return {k: base[k] + sum(u[k] - base[k] for u in updates) / n for k in base}
    return {k: base[k] + sum(u[k] - base[k] for u in updates) / (1 if "lora_B" in k else n) for k in base}


@dataclass
class RoundScore:
    global_adapter: Adapter
    base_loss: float
    new_loss: float
    improvement: dict[str, float]  # each contributor's Shapley share of the test-loss improvement (nats)
    excluded: list[str]


def shapley(players: list[str], value) -> dict[str, float]:
    """Exact Shapley values: each player's average marginal contribution over all coalitions."""
    n = len(players)
    out = {p: 0.0 for p in players}
    for p in players:
        others = [q for q in players if q != p]
        for mask in range(1 << len(others)):
            s = frozenset(q for i, q in enumerate(others) if mask >> i & 1)
            weight = math.factorial(len(s)) * math.factorial(n - len(s) - 1) / math.factorial(n)
            out[p] += weight * (value(s | {p}) - value(s))
    return out


def score_round(engine: Engine, test: list[dict], base: Adapter, updates: dict[str, Adapter], log=print) -> RoundScore:
    """Score contributors by Shapley value of test-loss improvement.

    v(S) = loss(base) - loss(merge of the updates in S). Contributors with Shapley value <= 0 made the
    model worse and are excluded; values are then recomputed over the kept set, so the shares minted
    in a round add up exactly to the improvement of the merged model (Shapley efficiency).
    Exact computation needs 2^n evaluations; fine for small rounds (Monte Carlo sampling scales it).
    """
    names = sorted(updates)
    if len(names) > 8:
        raise ValueError("exact Shapley scoring supports up to 8 updates per round")
    cache: dict[frozenset, float] = {}
    base_loss = engine.eval_loss(test, base)

    def value(s: frozenset) -> float:
        if s not in cache:
            cache[s] = base_loss - engine.eval_loss(test, aggregate(base, [updates[n] for n in sorted(s)])) if s else 0.0
        return cache[s]

    log(f"  base loss {base_loss:.4f}; scoring {len(names)} updates over {2 ** len(names) - 1} coalitions")
    first = shapley(names, value)
    keep = [n for n in names if first[n] > 0]
    excluded = [n for n in names if n not in keep]
    for n in names:
        log(f"  {n:<40} shapley {first[n]:+.4f}{'   -> excluded (made the model worse)' if n in excluded else ''}")
    # Re-score among the kept updates and drop anyone who no longer adds value, until every update in the
    # merged model has a positive share: you are in the model if and only if you own part of it.
    final = shapley(keep, value) if keep else {}
    while keep and any(final[n] <= 0 for n in keep):
        n = min(keep, key=lambda k: final[k])  # drop the least useful one, then re-score the rest
        log(f"  {n:<40} re-scored {final[n]:+.4f} with the others   -> excluded (adds nothing on top of them)")
        keep.remove(n)
        excluded.append(n)
        final = shapley(keep, value) if keep else {}
    if keep and value(frozenset(keep)) <= 0:
        # The kept updates help one by one but not together: the round is rejected and the model stays as it was.
        log("  merged update does not improve the hidden test -> round rejected, model unchanged, no shares")
        excluded, keep, final = list(names), [], {}
    excluded = sorted(excluded)
    merged = aggregate(base, [updates[n] for n in keep])
    new_loss = base_loss - value(frozenset(keep))
    improvement = {n: final.get(n, 0.0) for n in names}
    return RoundScore(merged, base_loss, new_loss, improvement, excluded)


# ----------------------------------------------------------------- serialization


def adapter_bytes(adapter: Adapter) -> bytes:
    return st_save({k: v.contiguous() for k, v in sorted(adapter.items())})


def adapter_from_bytes(blob: bytes) -> Adapter:
    return st_load(blob)


def adapter_hash(adapter: Adapter) -> str:
    return hashlib.sha256(adapter_bytes(adapter)).hexdigest()
