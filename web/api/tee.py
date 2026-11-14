"""Re-verify the Axon TEE vault's saved Intel TDX quote right now (serverless, stateless).

POST /api/tee {quote} -> {status, report_data, debug}. The browser then checks itself that report_data commits to
sha256(vault key || vault code hash) and that the NEAR contract binds model 4 to that key. Keeps nothing.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(__file__))
import _nearai as nearai  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:
        return

    def do_POST(self) -> None:
        try:
            n = int(self.headers.get("Content-Length") or 0)
            quote = str(json.loads(self.rfile.read(min(n, 64_000)) or b"{}").get("quote") or "")
            q = nearai._verify_quote(quote)
            out = {"ok": True, "status": q["status"], "advisories": q["advisories"], "report_data": q["td"]["report_data"],
                   "debug": bool(bytes.fromhex(q["td"]["td_attributes"])[0] & 1)}
            code = 200
        except Exception as e:  # noqa: BLE001
            out, code = {"ok": False, "error": f"{type(e).__name__}: {e}"}, 502
        body = json.dumps(out).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
