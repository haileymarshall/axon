#!/usr/bin/env bash
# One-time setup: Python env, demo data, and (optionally) a fresh testnet deployment.
#   ./scripts/setup.sh            -> env + data only (use the already-deployed contract)
#   ./scripts/setup.sh --deploy   -> also create testnet accounts via faucet and deploy the contract
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -m axon prepare-data

if [[ "${1:-}" == "--deploy" ]]; then
  command -v near >/dev/null || { echo "install near CLI: https://github.com/near/near-cli-rs"; exit 1; }
  P="axon-$(date +%s | tail -c 7).testnet"
  near account create-account sponsor-by-faucet-service "$P" autogenerate-new-keypair save-to-legacy-keychain network-config testnet create
  (cd contract && cargo near build non-reproducible-wasm)
  near contract deploy "$P" use-file contract/target/near/axon_contract.wasm with-init-call new json-args '{}' \
    prepaid-gas '30 Tgas' attached-deposit '0 NEAR' network-config testnet sign-with-legacy-keychain send
  for n in alice heart-clinic onco-clinic bob gpu user vault; do
    near account create-account fund-myself "$n.$P" '0.3 NEAR' autogenerate-new-keypair save-to-legacy-keychain \
      sign-as "$P" network-config testnet sign-with-legacy-keychain send
  done
  echo "export AXON_CONTRACT=$P AXON_PARENT=$P" | tee .env.testnet
fi
