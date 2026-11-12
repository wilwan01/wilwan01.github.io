# Site build scripts

Run from the repository root after editing pages or data (order matters):

1. `python3 scripts/update-research-nav.py` — shared research navigation (with section-language marks) on every `ai/` page.
2. `python3 scripts/update-site-meta.py` — canonical, Open Graph, Twitter, hreflang and the home-page WebSite JSON-LD.
3. `python3 scripts/build-search-index.py --as-of YYYY-MM-DD` — `ai/search-index.json` used by `ai/search.html`; use the verified content-build date. Ordinary reruns without `--as-of` retain that date. Candidate profiles and research/draft directories are excluded from formal search results.
4. `python3 scripts/build-sitemap.py` — `sitemap.xml` and `robots.txt` at the repository root.

All scripts are idempotent. `404.html` at the root is the GitHub Pages not-found page.
