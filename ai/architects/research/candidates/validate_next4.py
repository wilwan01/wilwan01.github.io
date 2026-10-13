#!/usr/bin/env python3
"""Validate the next-four candidate dossier; this does not validate the site."""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def validate(path: Path) -> dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["scope"] == "candidate-research-only"
    assert data["catalogChanged"] is False
    assert data["admissionState"] == "not-admitted"
    works = {work["workId"]: work for work in data["works"]}
    assert len(works) == len(data["works"]), "Duplicate workId"
    records = data["records"]
    assert len({r["candidateId"] for r in records}) == len(records)
    assert {r["name"] for r in records} == {"梁军", "单天逸", "张亚林", "赵立东"}
    required = ("title", "authors", "url", "type", "locator", "contentStatus", "attribution", "independenceKey")
    excluded_urls = {x.get("url") for x in data["excludedEvidence"]}
    for work in works.values():
        assert all(work.get(key) for key in required), work["workId"]
        assert work["url"].startswith("https://")
        assert work["url"] not in excluded_urls
        assert work["accessStatus"] in {"direct-page-reviewed", "indexed-text-only"}
        if work["mechanismBody"]:
            assert work["substantive"] and work["mechanism"]
        if work["countsTowardGate"]:
            assert work["primary"] and work["substantive"]
            assert work["accessStatus"] == "direct-page-reviewed"
    counts = Counter(r["disposition"] for r in records)
    for record in records:
        assert len(record["workIds"]) == len(set(record["workIds"]))
        selected = [works[wid] for wid in record["workIds"]]
        eligible = [w for w in selected if w["countsTowardGate"]]
        keys = [w["independenceKey"] for w in eligible]
        assert len(keys) == len(set(keys)), record["name"]
        priors = [p for w in eligible for p in w.get("priorityAnchors", [])]
        assert len(priors) == len(set(priors)), "Overlapping priority anchors"
        meets = len(set(keys)) >= 2 and any(w["mechanismBody"] for w in eligible)
        assert record["gatePassed"] == meets, record["name"]
        assert record["admitted"] is False
        assert record["remaining"]
        if record.get("roleAsOf"):
            assert record["roleAsOf"]["sourceWorkId"] in record["workIds"]
        if record["editorialChallenge"]:
            assert record["challengeOrigin"] == "editorial-proposal-not-attributed-quote"
    expected = {
        "candidates": len(records),
        "priorityTechnicalFollowup": counts["priority-technical-followup"],
        "systemScopeReview": counts["system-scope-review"],
        "deferredAttribution": counts["deferred-attribution"],
        "gatePassed": sum(r["gatePassed"] for r in records),
        "newCatalogProfiles": sum(r["admitted"] for r in records),
    }
    assert data["counts"] == expected
    assert data["validation"]["fullSiteValidation"] == "not-run"
    return {**expected, "distinctWorks": len(works)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", nargs="?", type=Path,
                        default=Path(__file__).with_name("2026-10-13-china-ai-next4.json"))
    args = parser.parse_args()
    try:
        result = validate(args.dossier)
    except (AssertionError, KeyError, ValueError, OSError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: candidate dossier only; " + json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
