#!/usr/bin/env bash
# Deploy the vault to a Phala Cloud TDX confidential VM.
#   deploy/phala.sh ghcr.io/<owner>/axon-vault@sha256:<digest>
# The compose file is written with the literal image digest, so the TEE's measured compose hash pins the exact code.
# Secrets (operator token, the relaying NEAR account's key) are sealed: encrypted to the TEE, never visible to Phala.
set -euo pipefail
cd "$(dirname "$0")/.."
IMAGE=${1:?usage: deploy/phala.sh <image@sha256:digest>}
[[ "$IMAGE" == *@sha256:* ]] || { echo "pin the image by digest"; exit 1; }
: "${AXON_CONTRACT:?}" "${AXON_OPERATOR:?}"
OUT=deploy/vault-compose.yml
sed "s|\${AXON_VAULT_IMAGE}|$IMAGE|" docker-compose.yml > "$OUT"
ENVF=$(mktemp); chmod 600 "$ENVF"; trap 'rm -f "$ENVF"' EXIT
KEY=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['private_key'])" "$HOME/.near-credentials/${AXON_NETWORK:-testnet}/$AXON_OPERATOR.json")
cat > "$ENVF" <<ENV
AXON_CONTRACT=$AXON_CONTRACT
AXON_NETWORK=${AXON_NETWORK:-testnet}
AXON_OPERATOR=$AXON_OPERATOR
AXON_VAULT_TOKEN=${AXON_VAULT_TOKEN:?set AXON_VAULT_TOKEN}
AXON_NEAR_PRIVATE_KEY=$KEY
ENV
# Production (non-dev) OS image: no debug access into the VM.
npx -y phala@latest deploy --name "${AXON_TEE_NAME:-axon-vault}" --compose "$OUT" --instance-type "${AXON_TEE_TYPE:-tdx.medium}" --image "${AXON_TEE_OS:-dstack-0.6.1}" -e "$ENVF" --wait
