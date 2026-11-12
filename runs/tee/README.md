# Vault in a real TEE (Intel TDX on Phala Cloud)

Deployed 12 Nov 2026. Re-check it yourself: `python scripts/verify_tee.py <vault URL>`.

| Item | Value |
|---|---|
| Vault URL | https://a74f87a6a22388452c31208eb8540c24a2ae5979-8700.dstack-pha1-prod5.phala.network |
| Phala app id | `a74f87a6a22388452c31208eb8540c24a2ae5979` (node prod5, US-WEST-1) |
| Hardware | Intel TDX confidential VM, `tdx.medium` (2 vCPU, 4 GB), $0.119/hr |
| OS image | `dstack-0.6.1`, **production** (not dev: no debug access into the VM) |
| Container image | `ghcr.io/haileymarshall/axon-vault@sha256:e798b0c43cdda05c3a189d2dd55d50b7856417990d78d92e0fdfe700d860bed8`, built by CI from this repo |
| Compose hash (measured by the TEE) | `8d4e012fa220b93eb78dd818d0df63f930b46b52dec17d241c4ce57355ba357e` |
| Vault code hash | `43a864759ba2a1f6…` (equals `code_hash()` of this checkout) |
| Vault signing key | `6c4cc8af19d09530…`, derived inside the TEE by the dstack key manager; it never exists outside |

## Verification result (`attestation-20261112.json`)

```
1. code hash   vault 43a864759ba2a1f6…  this checkout 43a864759ba2a1f6…  -> OK
2. quote binds key 6c4cc8af19d09530… + code hash  -> OK
3. genuine Intel TDX quote (verifier id dc79c199e0cb035b…)  -> OK
ALL CHECKS PASSED
```

Secrets (the operator token and the key of the account that relays results on-chain) were sealed to the TEE at deploy
time with Phala's encrypted environment variables, so the cloud operator never sees them. The first deploy landed on a
dev OS image by default; it was deleted and redeployed on the production image (`deploy/phala.sh` now pins it).
