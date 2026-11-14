"""Website demo of private data prep on NEAR AI Cloud (serverless, stateless).

GET  /api/prep            -> verify NEAR AI Cloud's TEE attestation with a fresh nonce (no data sent)
POST /api/prep {records, niche} -> verify first; only if every check passes, turn the records into training pairs

Keeps nothing: no database, no files, no logging of requests or answers. The records and pairs exist only in memory for
the length of the request and are returned to the browser. The verification code is `axon/nearai.py`, copied here as
`_nearai.py` by `scripts/build_site.py`. Real contributors run `axon prep` on their own machine with their own key, so
their records go from their computer straight to the TEE without passing through this relay.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(__file__))
import _nearai as nearai  # noqa: E402

MAX_CHARS = 8000  # demo relay pays for the calls: keep inputs small


class handler(BaseHTTPRequestHandler):
    def _send(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:  # no request logging
        return

    def do_GET(self) -> None:
        try:
            self._send(200, nearai.attest())
        except Exception as e:  # noqa: BLE001
            self._send(502, {"ok": False, "error": f"{type(e).__name__}: {e}"})

    def do_POST(self) -> None:
        try:
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(min(n, 64_000)) or b"{}")
            records = str(req.get("records") or "").strip()
            niche = req.get("niche") if req.get("niche") in nearai.PROMPTS else "rare-diseases"
            if not records:
                return self._send(400, {"ok": False, "error": "no records"})
            if len(records) > MAX_CHARS:
                return self._send(413, {"ok": False, "error": f"demo limit is {MAX_CHARS} characters; use `axon prep` for more"})
            self._send(200, nearai.prep(records, niche=niche))
        except Exception as e:  # noqa: BLE001
            self._send(502, {"ok": False, "error": f"{type(e).__name__}: {e}"})
        finally:
            records = req = None  # nothing outlives the request
