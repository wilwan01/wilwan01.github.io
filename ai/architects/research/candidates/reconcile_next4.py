#!/usr/bin/env python3
"""Rebuild the next-four result on the pinned concurrent upstream revision.

The initial integrate_next4.py is preserved as a replay of the original 378
baseline. This reconciliation is the final replay after concurrent publication.
Neither script pushes changes or asserts successful deployment.
"""
from __future__ import annotations
import hashlib
import json
import runpy
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parents[1]
UPSTREAM = 'e2a3b985455dcf15a1abc36251efdda9eac74844'
ORIGINAL = '7e4d1a5626fd91bc2152a1bd0e7ec192c1d810fb'
BATCH = '2026-10-13-next4-followthrough'
BATCH_PATH = f'research/batches/{BATCH}.json'
PID = 'jun-liang-cambricon'


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(['git', 'show', f'{UPSTREAM}:ai/architects/{path}'], cwd=REPO)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def save(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def normalize(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s).casefold() if c.isalnum())


def reconcile() -> dict:
    original = runpy.run_path(str(Path(__file__).with_name('integrate_next4.py')), run_name='next4_original_definitions')
    profile = original['PROFILE']
    candidates = original['CANDIDATES']
    raw = git_bytes('catalog.json')
    cat = json.loads(raw)
    upstream_profiles = {p['id']: p for p in cat['profiles']}
    assert len(cat['profiles']) == len(upstream_profiles) == 386, 'Unexpected pinned upstream'
    assert PID not in upstream_profiles
    current = load(ROOT/'catalog.json')
    current_profiles = {p['id']: p for p in current['profiles']}
    assert set(current_profiles) in (set(upstream_profiles), set(upstream_profiles)|{PID}), 'Unexpected concurrent profile edits'
    for pid, p in upstream_profiles.items():
        assert current_profiles[pid] == p, f'Upstream profile changed: {pid}'
    if PID in current_profiles:
        assert current_profiles[PID] == profile, 'Reviewed Liang profile changed'
    aliases = {}
    for p in upstream_profiles.values():
        for s in [p['id'], p['name'], *p.get('aliases', [])]:
            aliases.setdefault(normalize(s), set()).add(p['id'])
    collisions = {pid: sorted({hit for s in [pid,*names] for hit in aliases.get(normalize(s),set())}) for pid,names in candidates.items()}
    assert not any(collisions.values()), collisions
    cat['profiles'].append(profile)
    cat['updated'] = '2026-10-13'
    logs = cat['research'].get('batchLogs',[cat['research']['batchLog']])
    assert BATCH_PATH not in logs
    logs.append(BATCH_PATH)
    cat['research']['batchLogs'] = logs
    batch = load(ROOT/BATCH_PATH)
    batch['baseCommit'] = UPSTREAM
    batch['originalReviewedBaseline'] = ORIGINAL
    save(ROOT/BATCH_PATH,batch)
    batches = [load(ROOT/p) for p in logs]
    records = [r for b in batches for r in b['records']]
    assert len(records)==len({r['id'] for r in records})
    done = {r['id'] for r in records if r['status']=='complete'}
    cat['research'].update(totalProfiles=len(cat['profiles']), completedTotal=len(done), remainingCatalog=len(cat['profiles'])-len(done))
    for key,increment in [('additionalPlannedScope',4),('additionalCompleted',1),('remainingPlanned',3)]:
        assert isinstance(cat['research'][key],int)
        cat['research'][key] += increment
    save(ROOT/'catalog.json',cat)
    # Re-render from the exact concurrent upstream HTML to retain its naming fix.
    (ROOT/'index.html').write_bytes(git_bytes('index.html'))
    follow = load(ROOT/f'research/candidates/{BATCH}.json')
    follow['counts']['catalogProfiles'] = len(cat['profiles'])
    follow['dedupAudit'].update(baseCommit=UPSTREAM, catalogBlob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(), parsedProfiles=386, matchesInBaseline=collisions)
    follow['concurrentReconciliation'] = {'upstream':UPSTREAM,'retainedUpstreamProfiles':386,'finalProfiles':387,'addedByThisPR':[PID],'preserved':'All upstream profile fields, eight dataflow admissions and Iluvatar naming changes.'}
    save(ROOT/f'research/candidates/{BATCH}.json',follow)
    (ROOT/f'research/candidates/{BATCH}.md').write_text(
        '# 下一批四位：最终整合状态\n\n2026-10-13。\n\n'
        '**本PR只新增梁军一位，最终目录387位。** 初次基线378位；核验期间主分支另新增8位dataflow人物并修正天数智芯命名，已完整保留。以该386位上游为基线叠加梁军，不重复计算，也不覆盖其他编辑。\n\n'
        '梁军的两项共同署名专利分别涉及张量描述符访问/依赖控制，以及阶码分组累加。中美同族、优先权与署名链已核，同族只计一项。未入组的输入保留继续处理；sticky-bit条件的原文差异保留，不宣称IEEE逐位等价、独立测得PPA收益或量产采用。\n\n'
        '单天逸仍缺第二项具体技术正文，2026年4月19日CCF报告仅作为后续线索；张亚林按系统产品化/数据中心方向保留，运营访谈不补足机制证据；赵立东继续暂缓。三位均未收入正式目录。\n\n'
        f'逐项来源见 [{BATCH}.json]({BATCH}.json)。原始378位校验回执为历史记录；并发整合检查另见 [最终校验回执](2026-10-13-next4-reconciled-validation.json)。\n\n'
        '脚本reconcile_next4.py以固定上游提交复现整合；integrate_next4.py保留初始378位基线的复现。部署状态须另核GitHub Pages，不能从生成动作推定。\n',encoding='utf-8')
    receipt = load(ROOT/'research/candidates/2026-10-13-next4-validation.json')
    receipt['snapshotStatus'] = 'historical-pre-concurrent-reconciliation'
    receipt['supersededBy'] = '2026-10-13-next4-reconciled-validation.json'
    save(ROOT/'research/candidates/2026-10-13-next4-validation.json',receipt)
    subprocess.run([sys.executable,str(ROOT/'tools/render_contribution_batch.py')],check=True)
    final=load(ROOT/'catalog.json')
    assert len(final['profiles'])==387
    assert {p['id']:p for p in final['profiles'] if p['id']!=PID}==upstream_profiles
    assert all(pid not in {p['id'] for p in final['profiles']} for pid in candidates if pid!=PID)
    result={'upstream':UPSTREAM,'preservedProfiles':386,'admittedIds':[PID],'profiles':387,'fixedBatches':len(batches),'fixedBatchRecords':len(records),'auditedProfiles':len(done)}
    print('PASS: concurrent reconciliation; '+json.dumps(result,ensure_ascii=False))
    return result


if __name__=='__main__':
    reconcile()
