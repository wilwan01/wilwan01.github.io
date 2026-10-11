#!/usr/bin/env python3
"""Build ai/search-index.json for the client-side site search (ai/search.html).

Entries: {t: title, u: url, s: section, x: searchable text, l: language}.
Run from anywhere:  python3 scripts/build-search-index.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI = ROOT / "ai"
out = []


def add(t, u, s, x="", l="bi"):
    t = re.sub(r"\s+", " ", str(t or "")).strip()
    if not t:
        return
    out.append({"t": t, "u": u, "s": s, "x": re.sub(r"\s+", " ", str(x or "")).strip()[:400], "l": l})


def clean(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def load(p):
    return json.loads((AI / p).read_text(encoding="utf-8"))


# --- pages and report section headings
SECTION_OF = {"architects": "architects", "analysts": "analysts", "bridge": "bridge", "earnings": "earnings",
              "hot-chips": "hotchips", "notes": "notes", "policy": "policy", "standards": "standards", "method": "method"}
for f in sorted(AI.rglob("*.html")):
    rel = f.relative_to(AI).as_posix()
    if re.match(r"notes/[a-z]\d+\.html$", rel):
        continue  # covered by the notes catalog entries below
    if rel.startswith("files/") or rel.endswith("/index.html") and (AI / rel.replace("/index.html", ".html")).exists():
        continue
    h = f.read_text(encoding="utf-8", errors="replace")
    if 'http-equiv="refresh"' in h:
        continue
    title = clean((re.search(r"<title>(.*?)</title>", h, re.S) or [None, ""])[1])
    desc = (re.search(r'name="description"\s+content="([^"]*)"', h) or re.search(r'content="([^"]*)"\s+name="description"', h) or [None, ""])[1]
    lang = (re.search(r'<html[^>]*lang="([^"]*)"', h) or [None, "en"])[1][:2]
    top = rel.split("/")[0] if "/" in rel else "reports"
    sec = SECTION_OF.get(top, "reports")
    url = "/ai/" + rel.replace("index.html", "")
    add(title, url, sec if sec != "reports" else "reports", html.unescape(desc), "zh" if lang == "zh" else "en")
    if sec == "reports" and re.match(r"[a-z0-9]+-(en|zh)\.html$", rel):
        for m in re.finditer(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', h, re.S):
            add(clean(m.group(2)), f"{url}#{m.group(1)}", "reports", title, "zh" if lang == "zh" else "en")

# --- architects
for p in load("architects/catalog.json")["profiles"]:
    add(p["name"], f"/ai/architects/#{p['id']}", "architects", f"{p['field']} {p['core']}", "zh")
# --- analyst thought atlas and candidate cohort
atlas = load("analysts/thought-atlas.json")
for p in atlas["profiles"]:
    add(p["name"], f"/ai/analysts/thoughts.html?profile={p['id']}#map", "analysts", f"{p.get('role','')} {p.get('scope','')}", "zh")
try:
    for c in load("analysts/candidate-pipeline.json")["candidates"]:
        add(c["name"], "/ai/analysts/thoughts.html#candidates", "analysts", f"{c.get('firm','')} {c.get('focus','')}", "zh")
except Exception:
    pass
# --- earnings ledger
for q in load("analysts/corpus.json")["ledger"]:
    add(f"{q['company']} {q['quarter']} · {q['ask']}", f"/ai/earnings/#{q['id']}", "earnings", f"{q['id']} {q.get('theme','')} {q.get('analyst','')}", "en")
# --- notes
for n in load("notes/catalog.json")["available"]:
    add(n["title"], f"/ai/notes/{n['id'].lower()}.html", "notes", n.get("topic", ""), "en")
# --- Hot Chips patterns
for y in range(2017, 2027):
    p = AI / f"hot-chips/{y}.html"
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")
    i = t.find("<h2>Patterns in the reviewed Q&amp;A</h2>")
    j = t.find("<h2>", i + 10)
    for m in re.finditer(r"<h3>(.*?)</h3><p>(.*?)</p>", t[i:j], re.S):
        add(f"Hot Chips {y} · {clean(m.group(1))}", f"/ai/hot-chips/{y}.html", "hotchips", clean(m.group(2)), "en")
# --- bridge, policy, standards, glossary
for c in load("bridge/bridge.json")["cards"]:
    add(f"{c['id']} · {c['topic']}", f"/ai/bridge/#{c['id']}", "bridge", " ".join(c.get("architect_followups", [])), "zh")
for e in load("policy/policy.json")["events"]:
    add(f"{e['id']} · {e['title']['en']} / {e['title']['zh']}", f"/ai/policy/#{e['id']}", "policy", f"{e['date']} {e['summary']['en']} {e['summary']['zh']}", "bi")
for i in load("standards/standards.json")["items"]:
    add(f"{i['id']} · {i['name']} ({i['org']})", f"/ai/standards/#{i['id']}", "standards", f"{i['date']} {i['summary']['en']} {i['summary']['zh']}", "bi")
for t in load("method/glossary.json")["terms"]:
    add(f"{t['en']} / {t['zh']}", f"/ai/method/glossary.html#{t['id']}", "glossary", f"{t['def_en']} {t['def_zh']}", "bi")

(AI / "search-index.json").write_text(json.dumps({"built": "2026-10-11", "count": len(out), "entries": out}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(out), "entries,", (AI / "search-index.json").stat().st_size // 1024, "KB")
