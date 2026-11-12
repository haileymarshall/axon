#!/usr/bin/env bash
# End-to-end Axon demo on NEAR testnet:
#   create a model -> 4 contributors train locally on private data -> vault scores them (Shapley)
#   -> ownership recorded on-chain -> a user pays for a question -> owners earn.
#
# Prereqs: ./scripts/setup.sh done, vault running (`python -m axon vault --operator $OPERATOR`).
# Env: AXON_CONTRACT (contract account), AXON_PARENT (account the demo sub-accounts live under).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
: "${AXON_CONTRACT:?set AXON_CONTRACT}"
P=${AXON_PARENT:-$AXON_CONTRACT}
ROUNDS=${ROUNDS:-2}

echo "== 1. create the model (bound to the vault's key + code hash)"
if [[ -n "${MODEL:-}" ]]; then echo "reusing model $MODEL"; else
MODEL=$($PY -m axon create-model --creator "$P" --name "Health Assistant" --domain health \
  --description "Answers everyday health questions. Trained by people and clinics on their own private health data." \
  --price 0.01 --compute-fee 0.02 --budget 0.2 | awk '/model/{print $2}'); fi
echo "model id: $MODEL"

for r in $(seq 1 "$ROUNDS"); do
  echo "== 2.$r contributors train locally and send sealed updates (round $r)"
  for who in alice heart-clinic onco-clinic bob; do
    $PY -m axon contribute --model "$MODEL" --account "$who.$P" --data "data/contributors/$who.jsonl"
  done
  echo "== 3.$r vault merges, scores (Shapley) and records ownership on NEAR"
  $PY -m axon close-round --model "$MODEL" --compute-provider "gpu.$P"
done

echo "== 4. a user pays for a question; the payment is split among owners"
$PY -m axon ask --model "$MODEL" --account "user.$P" "What are the symptoms of type 2 diabetes?"

echo "== 5. who owns the model, and what they earned"
$PY -m axon status --model "$MODEL"
