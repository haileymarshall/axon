//! Axon contract: ownership ledger for AI models trained together on private data.
//!
//! Lifecycle of a model:
//!   1. `create_model`  - a creator defines a model (base model, domain, query price), registers the
//!                        public key of the sealed combiner (the TEE that merges and scores updates),
//!                        and deposits a training budget used to pay compute fees.
//!   2. `join_model`    - a contributor registers a device key. Raw data never leaves the contributor's
//!                        device; only signed, encrypted model updates do.
//!   3. `submit_round`  - after each training round the sealed combiner publishes a payload signed with
//!                        its key: the new adapter hash, the evaluation loss on a hidden test set, and
//!                        each contributor's measured improvement. The contract verifies the signature
//!                        and mints ownership shares equal to measured improvement. Compute providers
//!                        receive a fixed fee from the budget, not ownership.
//!   4. `pay_for_query` - users pay to query the model. Revenue is split pro-rata to share holders
//!                        with a reward-per-share accumulator (O(1) per payment).
//!   5. `withdraw`      - owners pull their earnings.
//!
//! Copyright (c) 2026 Axon contributors. MIT License.

use near_sdk::json_types::{U128, U64};
use near_sdk::serde_json;
use near_sdk::store::Vector;
use near_sdk::{
    env, near, require, AccountId, BorshStorageKey, NearToken, PanicOnDefault, Promise, PromiseOrValue,
};

/// Fixed-point scale for the reward-per-share accumulator.
const ACC_SCALE: u128 = 1_000_000_000;
const MAX_CONTRIBUTORS: usize = 100;
/// Upper bound on shares a single result may mint (1.0 nats of loss improvement = 1_000_000).
const MAX_IMPROVEMENT_MICRO: u64 = 10_000_000;

#[near]
#[derive(BorshStorageKey)]
enum StorageKey {
    Models,
    Rounds,
}

#[near(serializers = [borsh, json])]
#[derive(Clone, Debug, PartialEq)]
pub enum ModelStatus {
    Training,
    Closed,
}

#[near(serializers = [borsh, json])]
#[derive(Clone, Debug)]
pub struct Contributor {
    pub account: AccountId,
    /// ed25519 public key (hex) the contributor's device signs updates with.
    pub device_key: String,
    pub shares: U128,
    pub rounds: u32,
    /// Improvement measured in the contributor's latest round (micro-nats of eval loss).
    pub last_improvement_micro: U64,
    /// Settled, not yet withdrawn (yoctoNEAR).
    pub pending: U128,
    /// shares * acc_per_share at last settlement.
    pub reward_debt: U128,
    pub joined_at: U64,
}

#[near(serializers = [borsh, json])]
#[derive(Clone, Debug)]
pub struct Model {
    pub id: u64,
    pub name: String,
    pub domain: String,
    pub description: String,
    /// Open base model being fine-tuned, e.g. "HuggingFaceTB/SmolLM2-135M-Instruct".
    pub base_model: String,
    pub creator: AccountId,
    /// ed25519 public key (hex) of the sealed combiner. Only payloads signed by it are accepted.
    pub combiner_key: String,
    /// Hash of the combiner code/image the key is bound to (attestation reference).
    pub combiner_code_hash: String,
    pub query_price: U128,
    /// Fixed fee paid to the compute provider of each round (from `budget`).
    pub compute_fee: U128,
    pub budget: U128,
    pub status: ModelStatus,
    pub rounds: u32,
    pub adapter_hash: Option<String>,
    pub base_eval_loss_milli: Option<u32>,
    pub eval_loss_milli: Option<u32>,
    pub contributors: Vec<Contributor>,
    pub total_shares: U128,
    pub acc_per_share: U128,
    pub total_revenue: U128,
    pub queries: u64,
    /// Revenue received before any shares existed; claimable by the creator.
    pub creator_pending: U128,
    pub created_at: U64,
}

#[near(serializers = [borsh, json])]
#[derive(Clone, Debug)]
pub struct RoundResult {
    pub account: AccountId,
    pub improvement_micro: U64,
    pub shares: U128,
}

#[near(serializers = [borsh, json])]
#[derive(Clone, Debug)]
pub struct Round {
    pub model_id: u64,
    pub round: u32,
    pub adapter_hash: String,
    pub eval_loss_milli: u32,
    pub results: Vec<RoundResult>,
    pub compute_provider: Option<AccountId>,
    pub fee_paid: U128,
    pub timestamp: U64,
}

/// Payload signed by the sealed combiner. Sent as a JSON string so the signature covers exact bytes.
#[near(serializers = [json])]
pub struct RoundPayload {
    pub model_id: u64,
    pub round: u32,
    pub adapter_hash: String,
    pub base_eval_loss_milli: u32,
    pub eval_loss_milli: u32,
    pub results: Vec<PayloadResult>,
    pub compute_provider: Option<AccountId>,
}

#[near(serializers = [json])]
pub struct PayloadResult {
    pub account: AccountId,
    pub improvement_micro: U64,
}

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Axon {
    models: Vector<Model>,
    rounds: Vector<Round>,
}

fn emit(event: &str, data: serde_json::Value) {
    env::log_str(&format!(
        "EVENT_JSON:{}",
        serde_json::json!({"standard": "axon", "version": "1.0.0", "event": event, "data": [data]})
    ));
}

fn hex_decode(s: &str) -> Option<Vec<u8>> {
    if s.len() % 2 != 0 {
        return None;
    }
    (0..s.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&s[i..i + 2], 16).ok())
        .collect()
}

fn require_key(hex: &str) -> [u8; 32] {
    let bytes = hex_decode(hex).unwrap_or_else(|| env::panic_str("key must be hex"));
    bytes.try_into().unwrap_or_else(|_| env::panic_str("key must be 32 bytes"))
}

fn require_hash(s: &str) {
    require!(s.len() == 64 && hex_decode(s).is_some(), "hash must be sha256 hex");
}

impl Contributor {
    fn accrued(&self, acc: u128) -> u128 {
        self.shares.0 * acc / ACC_SCALE - self.reward_debt.0
    }
}

#[near]
impl Axon {
    #[init]
    pub fn new() -> Self {
        Self { models: Vector::new(StorageKey::Models), rounds: Vector::new(StorageKey::Rounds) }
    }

    // ------------------------------------------------------------------ models

    /// Create a model. The attached deposit becomes its training budget (pays compute fees).
    #[payable]
    #[allow(clippy::too_many_arguments)]
    pub fn create_model(
        &mut self,
        name: String,
        domain: String,
        description: String,
        base_model: String,
        combiner_key: String,
        combiner_code_hash: String,
        query_price: U128,
        compute_fee: U128,
    ) -> u64 {
        require!(!name.is_empty() && name.len() <= 64, "bad name");
        require!(domain.len() <= 64 && base_model.len() <= 128 && description.len() <= 500, "field too long");
        require_key(&combiner_key);
        require_hash(&combiner_code_hash);
        let id = self.models.len() as u64;
        let creator = env::predecessor_account_id();
        emit("model_created", serde_json::json!({"model_id": id, "creator": creator, "name": name}));
        self.models.push(Model {
            id,
            name,
            domain,
            description,
            base_model,
            creator,
            combiner_key: combiner_key.to_lowercase(),
            combiner_code_hash: combiner_code_hash.to_lowercase(),
            query_price,
            compute_fee,
            budget: U128(env::attached_deposit().as_yoctonear()),
            status: ModelStatus::Training,
            rounds: 0,
            adapter_hash: None,
            base_eval_loss_milli: None,
            eval_loss_milli: None,
            contributors: vec![],
            total_shares: U128(0),
            acc_per_share: U128(0),
            total_revenue: U128(0),
            queries: 0,
            creator_pending: U128(0),
            created_at: U64(env::block_timestamp_ms()),
        });
        id
    }

    /// Anyone can top up a model's training budget.
    #[payable]
    pub fn fund_training(&mut self, model_id: u64) {
        let amount = env::attached_deposit().as_yoctonear();
        require!(amount > 0, "attach a deposit");
        let m = self.model_mut(model_id);
        m.budget = U128(m.budget.0 + amount);
        emit("training_funded", serde_json::json!({"model_id": model_id, "amount": amount.to_string()}));
    }

    /// Register as a contributor with the ed25519 key your device signs updates with.
    pub fn join_model(&mut self, model_id: u64, device_key: String) {
        require_key(&device_key);
        let account = env::predecessor_account_id();
        let m = self.model_mut(model_id);
        require!(m.status == ModelStatus::Training, "model is closed");
        require!(m.contributors.len() < MAX_CONTRIBUTORS, "model is full");
        require!(!m.contributors.iter().any(|c| c.account == account), "already a contributor");
        m.contributors.push(Contributor {
            account: account.clone(),
            device_key: device_key.to_lowercase(),
            shares: U128(0),
            rounds: 0,
            last_improvement_micro: U64(0),
            pending: U128(0),
            reward_debt: U128(0),
            joined_at: U64(env::block_timestamp_ms()),
        });
        emit("contributor_joined", serde_json::json!({"model_id": model_id, "account": account}));
    }

    /// Creator rotates the combiner key (e.g. after redeploying the TEE image).
    pub fn set_combiner(&mut self, model_id: u64, combiner_key: String, combiner_code_hash: String) {
        require_key(&combiner_key);
        require_hash(&combiner_code_hash);
        let caller = env::predecessor_account_id();
        let m = self.model_mut(model_id);
        require!(caller == m.creator, "only creator");
        m.combiner_key = combiner_key.to_lowercase();
        m.combiner_code_hash = combiner_code_hash.to_lowercase();
    }

    pub fn close_model(&mut self, model_id: u64) {
        let caller = env::predecessor_account_id();
        let m = self.model_mut(model_id);
        require!(caller == m.creator, "only creator");
        m.status = ModelStatus::Closed;
    }

    // ------------------------------------------------------------------ rounds

    /// Publish a training round. `payload` is the exact JSON the combiner signed; `signature` is
    /// its ed25519 signature (hex). Anyone may relay it; only the signature matters.
    pub fn submit_round(&mut self, payload: String, signature: String) -> PromiseOrValue<u32> {
        let p: RoundPayload =
            serde_json::from_str(&payload).unwrap_or_else(|_| env::panic_str("payload is not valid JSON"));
        let sig: [u8; 64] = hex_decode(&signature)
            .and_then(|b| b.try_into().ok())
            .unwrap_or_else(|| env::panic_str("signature must be 64 hex bytes"));
        require_hash(&p.adapter_hash);

        let model_id = p.model_id;
        let m = self.model_mut(model_id);
        require!(m.status == ModelStatus::Training, "model is closed");
        let key = require_key(&m.combiner_key);
        require!(env::ed25519_verify(&sig, payload.as_bytes(), &key), "invalid combiner signature");
        require!(p.round == m.rounds + 1, "unexpected round number");

        let acc = m.acc_per_share.0;
        let mut results = Vec::with_capacity(p.results.len());
        let mut minted: u128 = 0;
        for (i, r) in p.results.iter().enumerate() {
            require!(r.improvement_micro.0 <= MAX_IMPROVEMENT_MICRO, "improvement out of range");
            require!(!p.results[..i].iter().any(|o| o.account == r.account), "duplicate contributor in round");
            let c = m
                .contributors
                .iter_mut()
                .find(|c| c.account == r.account)
                .unwrap_or_else(|| env::panic_str("result for unknown contributor"));
            let shares = r.improvement_micro.0 as u128;
            // settle earnings at the old share balance, then grow shares
            c.pending = U128(c.pending.0 + c.accrued(acc));
            c.shares = U128(c.shares.0 + shares);
            c.reward_debt = U128(c.shares.0 * acc / ACC_SCALE);
            c.rounds += 1;
            c.last_improvement_micro = r.improvement_micro;
            minted += shares;
            results.push(RoundResult { account: r.account.clone(), improvement_micro: r.improvement_micro, shares: U128(shares) });
        }
        m.total_shares = U128(m.total_shares.0 + minted);
        m.rounds = p.round;
        m.adapter_hash = Some(p.adapter_hash.to_lowercase());
        m.eval_loss_milli = Some(p.eval_loss_milli);
        if m.base_eval_loss_milli.is_none() {
            m.base_eval_loss_milli = Some(p.base_eval_loss_milli);
        }

        // Compute providers earn a fixed fee from the budget, never ownership.
        let fee_paid = if p.compute_provider.is_some() && m.compute_fee.0 > 0 && m.budget.0 >= m.compute_fee.0 {
            m.budget = U128(m.budget.0 - m.compute_fee.0);
            m.compute_fee.0
        } else {
            0
        };

        emit(
            "round_submitted",
            serde_json::json!({"model_id": model_id, "round": p.round, "eval_loss_milli": p.eval_loss_milli, "shares_minted": minted.to_string(), "compute_fee_paid": fee_paid.to_string()}),
        );
        self.rounds.push(Round {
            model_id,
            round: p.round,
            adapter_hash: p.adapter_hash.to_lowercase(),
            eval_loss_milli: p.eval_loss_milli,
            results,
            compute_provider: p.compute_provider.clone(),
            fee_paid: U128(fee_paid),
            timestamp: U64(env::block_timestamp_ms()),
        });

        match (p.compute_provider, fee_paid) {
            (Some(provider), fee) if fee > 0 => {
                PromiseOrValue::Promise(Promise::new(provider).transfer(NearToken::from_yoctonear(fee)))
            }
            _ => PromiseOrValue::Value(p.round),
        }
    }

    // ------------------------------------------------------------------ revenue

    /// Pay for one query. `source` records the payment origin (e.g. "intents:usdc@base") for audit.
    /// `query_hash` is sha256(question) in hex: it binds the payment to one question, so a payment
    /// seen on-chain cannot be reused by someone else to ask a different question.
    #[payable]
    pub fn pay_for_query(&mut self, model_id: u64, source: Option<String>, query_hash: Option<String>) {
        if let Some(h) = &query_hash {
            require_hash(h);
        }
        let amount = env::attached_deposit().as_yoctonear();
        let payer = env::predecessor_account_id();
        let m = self.model_mut(model_id);
        require!(amount >= m.query_price.0, "deposit below query price");
        if m.total_shares.0 == 0 {
            m.creator_pending = U128(m.creator_pending.0 + amount);
        } else {
            m.acc_per_share = U128(m.acc_per_share.0 + amount * ACC_SCALE / m.total_shares.0);
        }
        m.total_revenue = U128(m.total_revenue.0 + amount);
        m.queries += 1;
        emit(
            "query_paid",
            serde_json::json!({"model_id": model_id, "payer": payer, "amount": amount.to_string(), "source": source, "query_hash": query_hash}),
        );
    }

    /// Withdraw all of the caller's earnings from a model.
    pub fn withdraw(&mut self, model_id: u64) -> Promise {
        let who = env::predecessor_account_id();
        let m = self.model_mut(model_id);
        let mut amount = 0u128;
        if who == m.creator {
            amount += m.creator_pending.0;
            m.creator_pending = U128(0);
        }
        let acc = m.acc_per_share.0;
        if let Some(c) = m.contributors.iter_mut().find(|c| c.account == who) {
            amount += c.pending.0 + c.accrued(acc);
            c.pending = U128(0);
            c.reward_debt = U128(c.shares.0 * acc / ACC_SCALE);
        }
        require!(amount > 0, "nothing to withdraw");
        emit("withdrawn", serde_json::json!({"model_id": model_id, "account": who, "amount": amount.to_string()}));
        Promise::new(who).transfer(NearToken::from_yoctonear(amount))
    }

    // ------------------------------------------------------------------ views

    pub fn get_model(&self, model_id: u64) -> Option<Model> {
        self.models.get(model_id as u32).cloned()
    }

    pub fn get_models(&self, from_index: Option<u64>, limit: Option<u64>) -> Vec<Model> {
        let from = from_index.unwrap_or(0) as u32;
        let limit = limit.unwrap_or(20).min(50) as u32;
        (from..self.models.len().min(from.saturating_add(limit)))
            .filter_map(|i| self.models.get(i).cloned())
            .collect()
    }

    /// Withdrawable balance (yoctoNEAR) of `account` in `model_id`.
    pub fn earnings_of(&self, model_id: u64, account: AccountId) -> U128 {
        let m = self.model_ref(model_id);
        let mut total = if account == m.creator { m.creator_pending.0 } else { 0 };
        if let Some(c) = m.contributors.iter().find(|c| c.account == account) {
            total += c.pending.0 + c.accrued(m.acc_per_share.0);
        }
        U128(total)
    }

    /// Rounds of a model, oldest first.
    pub fn get_rounds(&self, model_id: u64, limit: Option<u64>) -> Vec<Round> {
        let limit = limit.unwrap_or(50).min(200) as usize;
        let mut v: Vec<Round> =
            (0..self.rounds.len()).rev().filter_map(|i| self.rounds.get(i)).filter(|r| r.model_id == model_id).take(limit).cloned().collect();
        v.reverse();
        v
    }

    // ------------------------------------------------------------------ internal

    fn model_ref(&self, id: u64) -> &Model {
        self.models.get(id as u32).unwrap_or_else(|| env::panic_str("no such model"))
    }

    fn model_mut(&mut self, id: u64) -> &mut Model {
        self.models.get_mut(id as u32).unwrap_or_else(|| env::panic_str("no such model"))
    }
}

#[cfg(test)]
mod tests;
