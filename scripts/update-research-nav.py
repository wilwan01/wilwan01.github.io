#!/usr/bin/env python3
"""Apply the shared AI research navigation to every HTML page, without changing content."""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINKS = (
    ("/ai/index.html", "产品分析"),
    ("/ai/earnings/", "财报分析"),
    ("/ai/analysts/", "分析师训练"),
    ("/ai/hot-chips/", "Hot Chips"),
    ("/ai/architects/", "架构师思想"),
    ("/ai/notes/", "Architecture Notes"),
    ("/ai/bridge/", "技术 × 投资"),
    ("/ai/policy/", "政策与地缘"),
    ("/ai/standards/", "标准与联盟"),
    ("/ai/method/", "方法与术语"),
    ("/ai/search.html", "搜索"),
)
ENGLISH = (
    "Product Analysis", "Earnings Analysis",
    "Analyst Mode", "Hot Chips", "Architect Mode", "Architecture Notes", "Tech x Invest",
    "Policy", "Standards", "Method & Glossary", "Search",
)
# Section language, so readers know before clicking. "both" sections carry no mark.
SECTION_LANG = {
    "/ai/earnings/": "en", "/ai/hot-chips/": "en", "/ai/notes/": "en",
    "/ai/analysts/": "zh", "/ai/architects/": "zh", "/ai/bridge/": "zh",
}
NAV = re.compile(r'<nav\b(?=[^>]*\bclass\s*=\s*[\"\'][^\"\']*\bresearch-nav\b)[^>]*>.*?</nav\s*>', re.I | re.S)
STYLE = re.compile(r'<link\b(?=[^>]*\bhref\s*=\s*[\"\']/ai/research-nav\.css(?:\?[^\"\']*)?[\"\'])[^>]*>', re.I)

def current_section(path):
    url = "/" + path.relative_to(ROOT).as_posix()
    return next((href for href, _ in LINKS[1:] if url.startswith(href)), LINKS[0][0])

def render(path, english=False):
    current = current_section(path)
    links = []
    for (href, zh_label), en_label in zip(LINKS, ENGLISH):
        label = en_label if english else zh_label
        section = SECTION_LANG.get(href)
        extra = ""
        if section == "zh" and english:
            label += " (中文)"
            extra = ' hreflang="zh"'
        elif section == "en" and not english:
            label += " (EN)"
            extra = ' hreflang="en"'
        attrs = ' aria-current="page"' if href == current else ""
        links.append(f'<a href="{href}"{attrs}{extra}>{html.escape(label)}</a>')
    label = 'AI research navigation' if english else 'AI 研究导航'
    theme = 'AI Infrastructure Research' if english else 'AI 基础设施研究'
    brand = f'<span class="research-name">{theme}</span>'
    return f'<nav class="research-nav" aria-label="{label}">' + brand + "".join(links) + '</nav>'

def update(path):
    before = path.read_text(encoding="utf-8")
    after, count = NAV.subn("", before)
    body = re.search(r'<body\b[^>]*>', after, re.I)
    if not body:
        print(f"Skipped (no <body>, treated as a fragment): {path.relative_to(ROOT)}")
        return False
    language = re.search(r'<html\b[^>]*\blang=["\']([^"\']+)', before, re.I)
    english = bool(language and language.group(1).lower().startswith("en"))
    after = after[:body.end()] + render(path, english) + after[body.end():]
    after = STYLE.sub("", after)
    after, head_count = re.subn(r'</head\s*>', '<link rel="stylesheet" href="/ai/research-nav.css?v=20261005-nav-theme"></head>', after, count=1, flags=re.I)
    if head_count != 1:
        raise ValueError(f"Missing head: {path}")
    if after != before:
        path.write_text(after, encoding="utf-8")
    return after != before

if __name__ == "__main__":
    pages = sorted((ROOT / "ai").rglob("*.html"))
    changed = sum(update(path) for path in pages)
    print(f"Shared navigation: {changed} updated / {len(pages)} pages")
