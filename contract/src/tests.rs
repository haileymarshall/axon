use super::*;
use ed25519_dalek::{Signer, SigningKey};
use near_sdk::test_utils::{get_logs, VMContextBuilder};
use near_sdk::testing_env;

const NEAR: u128 = 1_000_000_000_000_000_000_000_000;
const CODE_HASH: &str = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
const ADAPTER: &str = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc";

fn acct(s: &str) -> AccountId {
    s.parse().unwrap()
}

fn ctx(predecessor: &str, deposit: u128) {
    let mut b = VMContextBuilder::new();
    b.predecessor_account_id(acct(predecessor)).attached_deposit(NearToken::from_yoctonear(deposit));
    testing_env!(b.build());
}

fn combiner() -> SigningKey {
    SigningKey::from_bytes(&[42u8; 32])
}

fn device_key(i: u8) -> String {
    hex::encode(SigningKey::from_bytes(&[i; 32]).verifying_key().to_bytes())
}

fn setup() -> Axon {
    ctx("creator.near", NEAR);
    let mut c = Axon::new();
    c.create_model(
        "Health Assistant".into(),
        "health".into(),
        "Answers health questions".into(),
        "HuggingFaceTB/SmolLM2-135M-Instruct".into(),
        hex::encode(combiner().verifying_key().to_bytes()),
        CODE_HASH.into(),
        U128(NEAR / 100),
        U128(NEAR / 10),
    );
    for (i, n) in ["alice.near", "clinic.near", "bob.near"].iter().enumerate() {
        ctx(n, 0);
        c.join_model(0, device_key(i as u8 + 1));
    }
    c
}

fn payload(round: u32, results: &[(&str, u64)], provider: Option<&str>) -> String {
    serde_json::json!({
        "model_id": 0,
        "round": round,
        "adapter_hash": ADAPTER,
        "base_eval_loss_milli": 2500,
        "eval_loss_milli": 2100,
        "results": results.iter().map(|(a, i)| serde_json::json!({"account": a, "improvement_micro": i.to_string()})).collect::<Vec<_>>(),
        "compute_provider": provider,
    })
    .to_string()
}

fn sign(p: &str) -> String {
    hex::encode(combiner().sign(p.as_bytes()).to_bytes())
}

fn round(c: &mut Axon, n: u32, results: &[(&str, u64)]) {
    let p = payload(n, results, None);
    ctx("relayer.near", 0);
    let _ = c.submit_round(p.clone(), sign(&p));
}

#[test]
fn create_and_join() {
    let c = setup();
    let m = c.get_model(0).unwrap();
    assert_eq!(m.contributors.len(), 3);
    assert_eq!(m.budget.0, NEAR);
    assert_eq!(m.status, ModelStatus::Training);
}

#[test]
#[should_panic(expected = "already a contributor")]
fn cannot_join_twice() {
    let mut c = setup();
    ctx("alice.near", 0);
    c.join_model(0, device_key(9));
}

#[test]
#[should_panic(expected = "key must be 32 bytes")]
fn bad_device_key() {
    let mut c = setup();
    ctx("eve.near", 0);
    c.join_model(0, "abcd".into());
}

#[test]
fn signed_round_mints_shares_by_improvement() {
    let mut c = setup();
    round(&mut c, 1, &[("alice.near", 30_000), ("clinic.near", 70_000), ("bob.near", 0)]);
    let m = c.get_model(0).unwrap();
    assert_eq!(m.total_shares.0, 100_000);
    assert_eq!(m.contributors[0].shares.0, 30_000);
    assert_eq!(m.contributors[1].shares.0, 70_000);
    assert_eq!(m.contributors[2].shares.0, 0, "useless data earns nothing");
    assert_eq!(m.rounds, 1);
    assert_eq!(m.eval_loss_milli, Some(2100));
    assert_eq!(m.adapter_hash.as_deref(), Some(ADAPTER));
    assert!(get_logs().iter().any(|l| l.contains("round_submitted")));
    assert_eq!(c.get_rounds(0, None).len(), 1);
}

#[test]
#[should_panic(expected = "invalid combiner signature")]
fn forged_round_rejected() {
    let mut c = setup();
    let p = payload(1, &[("bob.near", 9_000_000)], None);
    let forger = SigningKey::from_bytes(&[7u8; 32]);
    ctx("bob.near", 0);
    let _ = c.submit_round(p.clone(), hex::encode(forger.sign(p.as_bytes()).to_bytes()));
}

#[test]
#[should_panic(expected = "invalid combiner signature")]
fn tampered_payload_rejected() {
    let mut c = setup();
    let p = payload(1, &[("bob.near", 10)], None);
    let sig = sign(&p);
    let tampered = p.replace("\"10\"", "\"9000000\"");
    ctx("bob.near", 0);
    let _ = c.submit_round(tampered, sig);
}

#[test]
#[should_panic(expected = "unexpected round number")]
fn replayed_round_rejected() {
    let mut c = setup();
    round(&mut c, 1, &[("alice.near", 10)]);
    round(&mut c, 1, &[("alice.near", 10)]);
}

#[test]
#[should_panic(expected = "unknown contributor")]
fn result_for_non_member_rejected() {
    let mut c = setup();
    round(&mut c, 1, &[("eve.near", 10)]);
}

#[test]
fn compute_provider_gets_fee_not_shares() {
    let mut c = setup();
    let p = payload(1, &[("alice.near", 10)], Some("gpu.near"));
    ctx("relayer.near", 0);
    let _ = c.submit_round(p.clone(), sign(&p));
    let m = c.get_model(0).unwrap();
    assert_eq!(m.budget.0, NEAR - NEAR / 10);
    assert!(m.contributors.iter().all(|x| x.account.as_str() != "gpu.near"));
    assert_eq!(c.get_rounds(0, None)[0].fee_paid.0, NEAR / 10);
}

#[test]
fn revenue_split_pro_rata() {
    let mut c = setup();
    round(&mut c, 1, &[("alice.near", 25), ("clinic.near", 25), ("bob.near", 50)]);
    ctx("user.near", NEAR);
    c.pay_for_query(0, Some("intents:usdc@base".into()), Some(ADAPTER.into()));
    let e = |a: &str| c.earnings_of(0, acct(a)).0;
    assert_eq!(e("alice.near"), NEAR / 4);
    assert_eq!(e("clinic.near"), NEAR / 4);
    assert_eq!(e("bob.near"), NEAR / 2);
    let m = c.get_model(0).unwrap();
    assert_eq!((m.queries, m.total_revenue.0), (1, NEAR));
}

#[test]
fn later_shares_do_not_capture_past_revenue() {
    let mut c = setup();
    round(&mut c, 1, &[("alice.near", 100)]);
    ctx("user.near", NEAR);
    c.pay_for_query(0, None, None);
    round(&mut c, 2, &[("clinic.near", 100)]);
    assert_eq!(c.earnings_of(0, acct("alice.near")).0, NEAR);
    assert_eq!(c.earnings_of(0, acct("clinic.near")).0, 0);
    ctx("user.near", NEAR);
    c.pay_for_query(0, None, None);
    assert_eq!(c.earnings_of(0, acct("alice.near")).0, NEAR + NEAR / 2);
    assert_eq!(c.earnings_of(0, acct("clinic.near")).0, NEAR / 2);
}

#[test]
fn revenue_before_shares_goes_to_creator() {
    let mut c = setup();
    ctx("user.near", NEAR);
    c.pay_for_query(0, None, None);
    assert_eq!(c.earnings_of(0, acct("creator.near")).0, NEAR);
}

#[test]
#[should_panic(expected = "deposit below query price")]
fn underpaying_fails() {
    let mut c = setup();
    ctx("user.near", 1);
    c.pay_for_query(0, None, None);
}

#[test]
fn withdraw_zeroes_balance() {
    let mut c = setup();
    round(&mut c, 1, &[("alice.near", 100)]);
    ctx("user.near", NEAR);
    c.pay_for_query(0, None, None);
    ctx("alice.near", 0);
    let _ = c.withdraw(0);
    assert_eq!(c.earnings_of(0, acct("alice.near")).0, 0);
}

#[test]
#[should_panic(expected = "only creator")]
fn only_creator_rotates_combiner() {
    let mut c = setup();
    ctx("bob.near", 0);
    c.set_combiner(0, device_key(5), CODE_HASH.into());
}

#[test]
#[should_panic(expected = "duplicate contributor in round")]
fn duplicate_contributor_in_round_rejected() {
    let mut c = setup();
    round(&mut c, 1, &[("alice.near", 10), ("alice.near", 10)]);
}

#[test]
#[should_panic(expected = "hash must be sha256 hex")]
fn bad_query_hash_rejected() {
    let mut c = setup();
    ctx("user.near", NEAR);
    c.pay_for_query(0, None, Some("not-a-hash".into()));
}

#[test]
fn query_hash_is_logged() {
    let mut c = setup();
    ctx("user.near", NEAR);
    c.pay_for_query(0, None, Some(ADAPTER.into()));
    assert!(get_logs().iter().any(|l| l.contains(ADAPTER)));
}
