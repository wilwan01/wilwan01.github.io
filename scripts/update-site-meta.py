#!/usr/bin/env python3
"""Add Open Graph / Twitter / hreflang metadata (and a WebSite JSON-LD on the two home pages) to every ai/ page.

Idempotent: the generated block sits between <!--site-meta--> markers and is replaced on each run.
Pages without <head> (fragments) and redirect stubs are skipped. A canonical link is added if missing.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI = ROOT / "ai"
BASE = "https://wilwan01.github.io/ai/"
SITE = "AI Infrastructure Research · AI 基础设施研究"
BLOCK = re.compile(r"\s*<!--site-meta-->.*?<!--/site-meta-->", re.S)


def canonical_for(rel):
    if rel.endswith("/index.html"):
        return BASE + rel[: -len("index.html")]
    return BASE + rel


def alt_pair(rel):
    m = re.match(r"(.+)-(zh|en)\.html$", rel)
    if m and (AI / f"{m.group(1)}-{'en' if m.group(2) == 'zh' else 'zh'}.html").exists():
        return {m.group(2): rel, ("en" if m.group(2) == "zh" else "zh"): f"{m.group(1)}-{'en' if m.group(2) == 'zh' else 'zh'}.html"}
    if rel == "index.html" and (AI / "index-en.html").exists():
        return {"zh": "index.html", "en": "index-en.html"}
    if rel == "index-en.html":
        return {"zh": "index.html", "en": "index-en.html"}
    return None


def update(path):
    rel = path.relative_to(AI).as_posix()
    if rel.startswith("files/"):
        return False
    text = path.read_text(encoding="utf-8")
    if 'http-equiv="refresh"' in text or not re.search(r"</head\s*>", text, re.I):
        return False
    text = BLOCK.sub("", text)
    title = html.unescape(re.sub(r"\s+", " ", (re.search(r"<title>(.*?)</title>", text, re.S) or [None, ""])[1])).strip()
    dm = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', text) or re.search(r'<meta[^>]+content="([^"]*)"[^>]+name="description"', text)
    desc = html.unescape(dm.group(1)) if dm else title
    lang = (re.search(r'<html[^>]*lang="([^"]+)"', text) or [None, "en"])[1].lower()
    cm = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', text)
    url = cm.group(1) if cm else canonical_for(rel)
    q = lambda s: html.escape(s, quote=True)
    parts = [
        f'<meta property="og:site_name" content="{q(SITE)}">', '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{q(title)}">', f'<meta property="og:description" content="{q(desc)}">',
        f'<meta property="og:url" content="{q(url)}">', f'<meta property="og:locale" content="{"zh_CN" if lang.startswith("zh") else "en_US"}">',
        '<meta name="twitter:card" content="summary">', f'<meta name="twitter:title" content="{q(title)}">', f'<meta name="twitter:description" content="{q(desc)}">',
    ]
    pair = alt_pair(rel)
    if pair:
        parts.append(f'<link rel="alternate" hreflang="zh-CN" href="{canonical_for(pair["zh"])}">')
        parts.append(f'<link rel="alternate" hreflang="en" href="{canonical_for(pair["en"])}">')
        parts.append(f'<link rel="alternate" hreflang="x-default" href="{canonical_for(pair["zh"])}">')
    if rel in ("index.html", "index-en.html"):
        ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "AI Infrastructure Research", "url": BASE,
              "inLanguage": ["zh-CN", "en"],
              "potentialAction": {"@type": "SearchAction", "target": BASE + "search.html?q={search_term_string}", "query-input": "required name=search_term_string"}}
        parts.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>")
    block = "\n<!--site-meta-->" + "".join(parts) + "<!--/site-meta-->"
    if not cm:
        block = f'\n<link rel="canonical" href="{url}">' + block
    new = re.sub(r"</head\s*>", lambda m: block + "</head>", text, count=1, flags=re.I)
    if new != text:
        path.write_text(new, encoding="utf-8")
    return new != text


if __name__ == "__main__":
    pages = sorted(AI.rglob("*.html"))
    print(f"Site metadata: {sum(update(p) for p in pages)} updated / {len(pages)} files")
