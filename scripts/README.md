# Site build scripts

Run from the repository root after editing pages or data (order matters):

1. `python3 scripts/update-research-nav.py` — shared research navigation (with section-language marks) on every `ai/` page.
2. `python3 scripts/update-site-meta.py` — canonical, Open Graph, Twitter, hreflang and the home-page WebSite JSON-LD.
3. `python3 scripts/build-search-index.py --as-of YYYY-MM-DD` — `ai/search-index.json` used by `ai/search.html`; use the verified content-build date. Ordinary reruns without `--as-of` retain that date. Candidate profiles and research/draft directories are excluded from formal search results.
4. `python3 scripts/build-sitemap.py` — `sitemap.xml` and `robots.txt` at the repository root.

All scripts are idempotent. `404.html` at the root is the GitHub Pages not-found page.

## Earnings refresh: mandatory company progression sync

Whenever earnings, a revenue update, guidance, or call evidence is recorded, update the affected company's existing record and review **Company coverage and four-quarter progression** in `ai/earnings/index.html` in the same change. This also applies to historical call-body backfills, not only new quarters.

1. Maintain stable quarter/call/question IDs in `ai/analysts/corpus.json`. Preserve the original four-quarter history and separate primary calls, post-earnings calls and results-only entries. Monthly sales, preliminary releases and long-term guidance do not create quarterly slots; retain their existing financial-refresh disclosures.
2. Review `ai/earnings/coverage-progression.json` against the newly read evidence. Update the affected company's editorial progression only when justified; results-only evidence must retain an explicit unread-call boundary. Keep the evidence cutoff aligned with the corpus, without inventing a new interpretation or advancing incomplete coverage.
3. Run `node ai/earnings/tools/sync-coverage.mjs`, then `node ai/earnings/tools/sync-coverage.mjs --check`. The second command is a required pre-publication gate: stale company rows, counts, source/QA links or progression text must block publication. Run it before building the search index above.
4. Run the applicable refresh validator and verify affected company rows and question deep links in the page. After deployment, check those rows on the public page as well as the dated refresh section. A refresh section alone does not satisfy company-table synchronization.

Responsive review: serve the repository, then open `scripts/fixtures/responsive-check.html`. Select each page and 390/768-pixel viewport; wait for its heading before measuring. This tests CSS layout in a real browser, not touch/device emulation. A wide table may scroll inside its own container without widening the page.
