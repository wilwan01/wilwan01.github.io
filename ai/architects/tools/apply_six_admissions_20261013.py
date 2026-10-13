#!/usr/bin/env python3
"""Apply the six admissions approved on 2026-10-13 without rebuilding the catalog.

Use --check for a dry run. The existing seven records must be present; no new
identity is created. Yan Xie and every unrelated profile are preserved exactly.
Technical-work/body-review flags originate in the existing reviewed records.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from urllib.parse import urlparse

DATE = "2026-10-13"
ROLES = {
    "heng-liao": "DaVinci 软硬件架构负责人；AI 系统互连与低精度计算共同贡献者",
    "shouyi-yin": "可重构 AI 处理器研究与架构贡献者",
    "peng-ouyang": "Thinker／可重构神经网络处理器架构贡献者",
    "xinyu-niu": "可重构计算与编译／编程协同设计贡献者",
    "kuen-hung-tsoi": "可重构加速器／数据流与编程体系贡献者",
    "yang-jiao-hanguang": "含光 800 技术报告人；NPU 并行系统与互连共同贡献者",
}
SOURCE_URLS = {
    "liao-ub-mesh": "https://arxiv.org/abs/2503.20377",
    "liao-hifloat4": "https://arxiv.org/abs/2602.11287",
    "niu-session-types": "https://mrg.cs.ox.ac.uk/publications/session-types-towards-safe-and-fast-reconfigurable-programming/",
    "tsoi-session-types": "https://mrg.cs.ox.ac.uk/publications/session-types-towards-safe-and-fast-reconfigurable-programming/",
}
BOUNDARIES = {
    "heng-liao": "共同署名不等于独立发明；UB-Mesh、HiFloat4 与 DaVinci 职责分别归属，不把一篇作品外推为整个产品的个人设计。",
    "shouyi-yin": "共同作品如实标注；不根据职务推断与欧阳鹏的模块分工。ELearn 仅核验题名及作者，不计入本次两项实质作品门槛。",
    "peng-ouyang": "Thinker 与具名专利支持共同贡献，不外推为清微后续全部型号的唯一主架构师。",
    "xinyu-niu": "研究机制不等于 CAISA 商业产品已实现特性；不把共同作品的编译器贡献独占归给牛昕宇。",
    "kuen-hung-tsoi": "Remarn 研究与 CAISA 商业产品分开；不把共同作品的全部硬件贡献独占归给蔡权雄。",
    "yang-jiao-hanguang": "保留历史项目归属，不推断中文姓名或现任雇主；专利申请不等于授权专利，也不能证明方案用于含光 800。",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def records(catalog: dict) -> list[dict]:
    for key in ("profiles", "records", "people"):
        if isinstance(catalog.get(key), list):
            return catalog[key]
    raise ValueError("Catalog has no supported profile collection")


def admission(profile: dict) -> str:
    return profile.get("evidence", {}).get("admission", {}).get("status", profile.get("status", "candidate"))


def migrate(catalog: dict) -> tuple[dict, dict]:
    before = copy.deepcopy(catalog)
    result = copy.deepcopy(catalog)
    old_profiles = records(before)
    profiles = records(result)
    ids = [p.get("id") for p in profiles]
    require(all(ids) and len(ids) == len(set(ids)), "Missing or duplicate profile ids")
    old = {p["id"]: p for p in old_profiles}
    by_id = {p["id"]: p for p in profiles}
    require(set(ROLES) | {"yan-xie"} <= set(by_id), "An approved target is missing; refusing to add/guess identities")
    admitted_delta = 0
    candidate_delta = 0
    historical_delta = 0
    report = {"date": DATE, "promoted": [], "unchanged_pending": "yan-xie", "created_profiles": 0}

    for pid, role in ROLES.items():
        p = by_id[pid]
        previous = old[pid]
        prior_admission = admission(previous)
        require(prior_admission in {"candidate", "needs_more_evidence", "admitted", "historical", "active"}, f"Unexpected state for {pid}")
        evidence = p.setdefault("evidence", {})
        works = evidence.get("technical_works", [])
        require(isinstance(works, list) and works, f"No reviewed works for {pid}")
        qualifying = [w for w in works if w.get("is_distinct_work", True) and w.get("id") and w.get("id") != "elearn"]
        distinct = {w["id"] for w in qualifying}
        require(len(distinct) >= 2, f"Fewer than two substantive works for {pid}")
        require(any(w.get("body_reviewed") is True for w in qualifying), f"No body-reviewed work for {pid}")
        sources = evidence.get("sources", [])
        require(isinstance(sources, list), f"Unsupported evidence source structure: {pid}")
        for source in sources:
            sid = source.get("id")
            if sid in SOURCE_URLS:
                source["url"] = SOURCE_URLS[sid]
            if sid == "yin-elearn":
                # Retain prior metadata-only evidence; never upgrade its review flag.
                source["verification_status"] = "title_and_authors_verified"
        for work in works:
            if work.get("id") == "elearn":
                require(work.get("body_reviewed") is not True, "ELearn must remain metadata-only")
        status = "historical" if pid == "yang-jiao-hanguang" else "active"
        p["status"] = status
        p["primary_role"] = role
        p["updated"] = DATE
        identity = p.setdefault("identity", {})
        identity["status"] = status
        identity["primary_role"] = role
        if pid == "yang-jiao-hanguang":
            identity["historical"] = True
            require(not p.get("nameZh"), "Do not guess Yang Jiao's Chinese name")
            require(any(w.get("work_type", w.get("type")) == "patent_application" or "us20230185749a1" == w.get("id", "").lower() for w in works), "Patent application identity is missing")
        if pid in {"xinyu-niu", "kuen-hung-tsoi"}:
            p["org"] = ["Imperial College London (historical research affiliation)"]
        evidence.setdefault("admission", {}).update({
            "status": "admitted", "work_count": len(distinct), "body_reviewed": True,
            "reason": "两项或以上不同的实质技术作品，至少一项正文机制核验；按共同贡献及历史归属边界收录。" + BOUNDARIES[pid],
        })
        p.setdefault("knowledge_status", {}).update({"profile": "admitted", "mechanism": "body_reviewed"})
        p.setdefault("synthesis", {}).update({"one_line": role, "verification_status": "admitted"})
        if prior_admission not in {"admitted", "historical", "active"}:
            admitted_delta += 1
            if previous.get("status") == "candidate":
                candidate_delta += 1
            if status == "historical" and previous.get("status") != "historical":
                historical_delta += 1
        report["promoted"].append({"id": pid, "status": status, "substantive_work_count": len(distinct), "boundary": BOUNDARIES[pid]})

    queue = result.get("candidate_queue")
    require(isinstance(queue, list), "Missing candidate queue; refusing to guess its structure")
    result["candidate_queue"] = [row for row in queue if row.get("id") not in ROLES]
    meta = result.setdefault("meta", {})
    for key, delta in (("admitted_count", admitted_delta), ("candidate_count", -candidate_delta), ("history_count", historical_delta)):
        if key in meta:
            require(isinstance(meta[key], int) and meta[key] + delta >= 0, f"Invalid count {key}")
            meta[key] += delta
    if "profile_count" in meta:
        require(meta["profile_count"] == len(profiles), "Existing profile_count does not match the collection")
    # Prior validation results describe the previous catalog, not this migration.
    if result != before:
        require(isinstance(result.get("version"), int), "Unsupported catalog version")
        result["version"] += 1
        result["updated"] = DATE
        if "last_validation" in meta:
            meta["last_validation"] = {key: "pending" for key in meta["last_validation"]}
    require([p["id"] for p in profiles] == [p["id"] for p in old_profiles], "Identity/order changed")
    for pid, original in old.items():
        if pid not in ROLES:
            require(by_id[pid] == original, f"Unrelated or pending profile modified: {pid}")
    require(admission(by_id["yan-xie"]) not in {"admitted", "historical", "active"}, "Yan Xie must remain pending")
    report.update({"profile_count": len(profiles), "net_new_admissions": admitted_delta, "changed": result != before})
    return result, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "catalog.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    result, report = migrate(catalog)
    if not args.check and result != catalog:
        args.catalog.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
