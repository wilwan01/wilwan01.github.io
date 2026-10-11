#!/usr/bin/env python3
"""Write sitemap.xml and robots.txt at the repository root from the canonical URL of every ai/ page.

lastmod comes from the file's last git commit date. Redirect stubs, fragments and downloads are excluded.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI = ROOT / "ai"
HOST = "https://wilwan01.github.io"


def lastmod(p):
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(p.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() or "2026-10-11"


urls = [(HOST + "/", lastmod(ROOT / "index.html"))]
for p in sorted(AI.rglob("*.html")):
    rel = p.relative_to(AI).as_posix()
    if rel.startswith(("files/", "architects/research/")):
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    if 'http-equiv="refresh"' in t or "<body" not in t.lower():
        continue
    m = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', t)
    urls.append((m.group(1) if m else f"{HOST}/ai/{rel}", lastmod(p)))
seen, out = set(), []
for u, d in urls:
    if u not in seen:
        seen.add(u)
        out.append(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>")
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(out) + "\n</urlset>\n", encoding="utf-8")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {HOST}/sitemap.xml\n", encoding="utf-8")
print(len(out), "URLs")
