# Trader module — 2026-11-15

Status: implementation reviewed locally; publication awaits approval.

Scope: 8 trader profiles, 8 transferable capabilities, 6 conditional compute-finance structures, searchable/filterable profiles, stable profile links, and a synthetic supplier hedge calculator. Added links to Chinese/English research homes, analyst and architect navigation, plus site search. Navigation/home/search generators updated to preserve the addition.

Evidence: adapted from Compute_Derivatives_Trader_Playbook_2026-11-14.html. The 18-source manifest and original coverage limits are in catalog.json. Historical inspection statements in the original report describe the November 14 research, not a new full audit. November 15 spot checks: Columbia Arnold interview page, Cboe Sinclair article and CME Compute Futures page. CME still says pending regulatory review; no current liquidity, executable quotes or realized alpha established. No private vendor or internal measurement data imported.

Validation: JavaScript syntax checks passed. Three synthetic cash-flow identities verified with absolute tolerance below $0.0000001 (binary floating-point rounding); displayed USD rounded to cents. Unique IDs, all local anchors, all profile-to-source references and four navigation entry points checked. Browser check: Thorp search returns 1/8 and expands; volume-halving preset returns $255,500 total, -$109,500 basis and -$365,000 quantity mismatch. Narrow viewport visually inspected. This is not an independent external review; no market backtest or trade executed. Full repository build and broad regression suite not run in the partial local checkout.

Decision: prioritize basis and business hedging; keep relative-value and option structures conditional. Open questions: matched transaction data, execution depth, benchmark methodology, credit and margin timing. Next discriminating action: compare no hedge, simple hedge and basis-adjusted hedge on matched executable prices and business exposures.

Permitted destination: proposed change to wilwan01/wilwan01.github.io/ai/. No merge or production publication before explicit approval.
