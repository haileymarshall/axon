# NEAR AI Cloud: private data prep evidence (14 Nov 2026)

- `prep-clinic-notes-20261114.txt`: `python -m axon prep samples/clinic-notes.txt` output, every check listed.
- `clinic-notes-pairs.jsonl`: the training pairs it wrote from the **fictional** notes (no names, places or record numbers).
- `attestation-20261114.json`: a fresh attestation check of `Qwen/Qwen3.8-27B` (gateway + model Intel TDX quotes,
  NVIDIA GPU verdict, nonce, compose hash), as returned by `axon.nearai.attest()`.

Re-run any time with your own key: `python -m axon prep samples/clinic-notes.txt --out /tmp/pairs.jsonl`.
