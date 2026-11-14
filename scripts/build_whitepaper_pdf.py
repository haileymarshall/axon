"""Print web/whitepaper.html to web/axon-whitepaper.pdf (A4, print layout) with headless Chromium.

    python scripts/build_whitepaper_pdf.py    # serves web/ locally for the duration of the print
"""

import asyncio, functools, http.server, os, threading
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"


class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith("/static/"):
            path = path[len("/static"):]
        return super().translate_path(path)

    def log_message(self, *a):
        pass


async def main() -> None:
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(WEB)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto(f"http://127.0.0.1:{srv.server_port}/whitepaper.html", wait_until="networkidle")
        await pg.emulate_media(media="print")
        tmp = WEB / "axon-whitepaper.tmp.pdf"
        await pg.pdf(path=str(tmp), format="A4", print_background=True, display_header_footer=True,
                     header_template="<div></div>",
                     footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#6a72a8">Axon Whitepaper · axon.surf · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                     margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        os.replace(tmp, WEB / "axon-whitepaper.pdf")
        await b.close()
    srv.shutdown()
    print(f"web/axon-whitepaper.pdf ({(WEB / 'axon-whitepaper.pdf').stat().st_size // 1024} KB)")


asyncio.run(main())
