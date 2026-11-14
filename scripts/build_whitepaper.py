"""Render WHITEPAPER.md to web/whitepaper.html (served at /whitepaper), in the site's design.

    python scripts/build_whitepaper.py
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Axon Whitepaper</title>
<meta name="description" content="Axon: specialized AI built from private data, co-owned by its contributors, paid on every inference. Design, privacy model, NEAR contract and every mainnet run.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sofia+Sans+Condensed:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/b/style.css">
<style>
  .paper { max-width: 900px; margin: 0 auto; padding: 120px 24px 80px; }
  .paper h1 { font: 300 clamp(44px, 6vw, 84px)/1 var(--display); margin: 0 0 18px; }
  .paper h2 { font: 300 clamp(30px, 3.4vw, 44px)/1.05 var(--display); margin: 64px 0 16px; padding-top: 24px; border-top: 1px solid var(--line); }
  .paper h3 { font: 500 22px/1.2 var(--display); margin: 34px 0 10px; }
  .paper p, .paper li { color: var(--dim); }
  .paper strong, .paper b { color: var(--ink); }
  .paper a { color: var(--ink); }
  .paper table { margin: 14px 0 22px; display: block; overflow-x: auto; }
  .paper td, .paper th { vertical-align: top; }
  .paper pre { background: var(--fill); border: 1px solid var(--line); padding: 14px; overflow-x: auto; font: 12.5px/1.5 var(--mono); }
  .paper hr { border: 0; border-top: 1px solid var(--line); margin: 36px 0; }
  .paper code { word-break: break-word; }
  .paper .back { font: 600 12px var(--mono); letter-spacing: .1em; text-transform: uppercase; text-decoration: none; }
</style>
</head>
<body>
<header class="top">
  <nav>
    <a href="/#/models">Models</a>
    <a href="/#/contribute">Contribute</a>
    <a href="/#/demo">Demo</a>
    <a href="/whitepaper" class="on">Whitepaper</a>
    <a href="/#/how">How it works</a>
  </nav>
  <a class="brand" href="/#/">Axon<small>co-owned AI</small></a>
  <div class="right"><a class="btn top-cta" href="/#/demo">Try the models</a></div>
</header>
<main class="paper">
<a class="back" href="/">← axon.surf</a>
"""
FOOT = """
</main>
<footer class="foot"><span>Built on NEAR · NEAR AI Cloud</span><span>Contract <a href="https://nearblocks.io/address/axon.ebukaa.near" target="_blank" rel="noopener">axon.ebukaa.near</a></span></footer>
</body>
</html>
"""


def main() -> None:
    md = (ROOT / "WHITEPAPER.md").read_text()
    html = markdown.markdown(md, extensions=["tables", "fenced_code", "toc", "sane_lists"])
    # Repository paths become links to the public repo.
    repo = "https://github.com/haileymarshall/axon/tree/master/"
    html = re.sub(r"<code>(runs/[^<\s]+?/?)</code>", lambda m: f'<a href="{repo}{m.group(1)}"><code>{m.group(1)}</code></a>', html)
    html = re.sub(r'href="(?!https?:|#|/)([^"]+)"', lambda m: f'href="{repo}{m.group(1)}"', html)
    html = html.replace("<a href=\"https://", "<a target=\"_blank\" rel=\"noopener\" href=\"https://")
    # Contents entries link to their sections (section headings in order, after "Contents").
    ids = re.findall(r'<h2 id="([^"]+)">', html)
    ids = [i for i in ids if i != "contents"]
    m = re.search(r'(<h2 id="contents">Contents</h2>\s*<ol>)(.*?)(</ol>)', html, flags=re.S)
    if m:
        items = re.findall(r"<li>(.*?)</li>", m.group(2), flags=re.S)
        links = "".join(f'<li><a href="#{i}">{t}</a></li>' for t, i in zip(items, ids))
        html = html[:m.start()] + m.group(1) + links + m.group(3) + html[m.end():]
    (ROOT / "web" / "whitepaper.html").write_text(HEAD + html + FOOT)
    print(f"web/whitepaper.html ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
