# Site build scripts

Run from the repository root after editing pages or data (order matters):

1. `python3 scripts/update-research-nav.py` — shared research navigation (with section-language marks) on every `ai/` page.
2. `python3 scripts/update-site-meta.py` — canonical, Open Graph, Twitter, hreflang and the home-page WebSite JSON-LD.
3. `python3 scripts/build-search-index.py` — `ai/search-index.json` used by `ai/search.html`.
4. `python3 scripts/build-sitemap.py` — `sitemap.xml` and `robots.txt` at the repository root.

All scripts are idempotent. `404.html` at the root is the GitHub Pages not-found page.
