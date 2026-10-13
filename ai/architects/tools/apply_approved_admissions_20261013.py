#!/usr/bin/env python3
"""Apply the approved six-person decision to contribution-led-v1, preserving others.

Existing profiles are enriched in place. Missing approved identities are added.
Yan Xie's original record is archived intact outside the public directory because
this decision does not count the interview as the second qualifying work.
Run --check before applying. No network, shell execution, or guessed identities.
"""
import argparse
import copy
import json
from pathlib import Path

DATE = '2026-10-13'
BATCH = '2026-10-13-approved-six'
TARGETS = {'heng-liao', 'shouyi-yin', 'peng-ouyang', 'xinyu-niu', 'kuen-hung-tsoi', 'yang-jiao-hanguang'}
PENDING = 'yan-xie'
ROLES = {
    'heng-liao': 'DaVinci 软硬件架构、AI 系统互连与低精度计算',
    'shouyi-yin': '可重构 AI 处理器研究与架构',
    'peng-ouyang': 'Thinker／可重构神经网络处理器',
    'xinyu-niu': '可重构计算与编译／编程协同设计',
    'kuen-hung-tsoi': '可重构加速器／数据流与编程体系',
    'yang-jiao-hanguang': '含光 800 历史项目与 NPU 并行互连',
}
BOUNDARIES = {
    'heng-liao': 'DaVinci 架构职责、UB-Mesh 与 HiFloat4 分别归属；共同署名不代表独立发明，不把后两项研究的全部机制反推为早期 DaVinci 的个人设计。',
    'shouyi-yin': '共同作品不按职务猜测与欧阳鹏的模块分工；Thinker 大学记录仅作为作者与摘要核验，ELearn 不作为本次正文证据；不把专利自动等同于 TX8 产品实现。',
    'peng-ouyang': '以署名作品支持共同贡献，不外推为清微后续全部型号的唯一主架构师；与尹首一共享作品时分别记录共同参与。',
    'xinyu-niu': 'Remarn 与 Session Types 是研究成果，不等于 CAISA 商业产品已实现相同机制；不把共同作品中的全部编译器贡献独占归给牛昕宇。',
    'kuen-hung-tsoi': '研究与 CAISA 商业产品分开记录；不把 Remarn 或 Session Types 的全部硬件贡献独占归给蔡权雄，也不按管理头衔推断设计分工。',
    'yang-jiao-hanguang': '仅保留 Alibaba 历史项目归属；不猜中文名或现任雇主。US20230185749A1 是公开专利申请，不写成授权专利，不宣称其中方案已用于含光 800。',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def source(wid, title, authors, date, url, locator, kind='论文全文', body=True, substantive=True):
    return dict(workId=wid, title=title, authors=authors, date=date, url=url,
                locator=locator, type=kind,
                contentStatus=('已核对署名与所列机制正文；不代表通读或复现全部实验。' if body else '仅核对官方题名、署名或职责；不宣称正文已复核。'),
                evidenceStrength='一手作品支持共同贡献；不支持独占模块归属。',
                role='机制与共同贡献归属' if substantive else '历史职责归属',
                primary=True, substantive=substantive, mechanismBody=body, retrievedAt=DATE)


REMARN = source('remarn-trets2022',
    'Remarn: A Reconfigurable Multi-threaded Multi-core Accelerator for Recurrent Neural Networks',
    'Zhiqiang Que、Hiroki Nakahara、Hongxiang Fan、He Li、Jiuxi Meng、Kuen Hung Tsoi、Xinyu Niu、Eriko Nurvitadhi、Wayne Luk',
    '2022-12-22', 'https://doi.org/10.1145/3534969', '作者表；§3 的粗粒度多线程、子层调度及多核划分')
SESSION = source('session-types-can2012',
    'Session Types: Towards Safe and Fast Reconfigurable Programming',
    'Nicholas Ng、Nobuko Yoshida、Xinyu Niu、Kuen Hung Tsoi、Wayne Luk',
    '2012', 'https://mrg.cs.ox.ac.uk/publications/session-types-towards-safe-and-fast-reconfigurable-programming/',
    '大学作者页与摘要；论文 DOI 10.1145/2460216.2460221', '大学论文记录', False)
REMARN_FACT = '作为共同作者，参与用粗粒度多线程隐藏 RNN 数据依赖停顿、并通过子加速器划分支持多个模型并行执行的 Remarn 研究。'
SESSION_FACT = '作为共同作者，参与以会话类型描述并行通信并在编译期检查通信安全及无死锁性质的可重构编程研究。'


def make_profile(pid, name, aliases, domain, related, core, background, facts, audits, question, variables, model, counterexample, diagnostic):
    return {
        'id': pid, 'name': name, 'aliases': aliases, 'field': ROLES[pid],
        'domain': domain, 'relatedDomains': related, 'core': core,
        'contributions': [text for _, text in facts], 'background': background,
        'argument': '编辑分析：' + model,
        'evidence': '至少两项不同的一手技术作品，且至少一项具体机制正文；署名支持共同贡献。',
        'habits': ['将个人贡献归属、团队机制和产品采用证据分开。', '用端到端成本检验局部架构收益。'],
        'questions': [question], 'boundary': BOUNDARIES[pid], 'diagnostic': diagnostic,
        'notes': [], 'sources': [[s['title'], s['url'], s['locator']] for s in audits],
        'sourceAudit': audits,
        'sourceFacts': [{'workId': wid, 'text': text} for wid, text in facts],
        'awardsVerified': [], 'contributionBasis': '基于署名技术作品的编辑提炼；不声称官方获奖理由或独占贡献。',
        'researchStatus': {'status': 'complete', 'batch': BATCH, 'standard': 'contribution-led-v1',
                           'meaning': '完成所列贡献核验，不代表穷尽成果或确认商业产品采用。', 'verifiedAt': DATE},
        'challenge': {'lens': ROLES[pid], 'skills': ['A1', 'A2', 'A7'], 'question': question,
                      'variables': variables, 'model': '编辑条件模型：' + model,
                      'crossover': '新增机制减少的等待或数据移动成本须高于实现、转换和调度成本。',
                      'counterexample': counterexample, 'validation': diagnostic,
                      'transfer': '用于比较加速器、互连与软硬件协同方案的可复用评审问题。'},
    }


def new_profiles():
    liao_audits = [
        source('ub-mesh-2025', 'UB-Mesh: a Hierarchically Localized nD-FullMesh Datacenter Network Architecture',
               'Heng Liao 等；Huawei', '2025', 'https://arxiv.org/html/2503.20377v3',
               '作者表；§3 层次化 nD-FullMesh；§4.1 All-Path Routing'),
        source('hifloat4-2026', 'HiFloat4 Format for Language Model Inference',
               'Yuanyong Luo 等；共同作者 Heng Liao', '2026-02-11', 'https://arxiv.org/html/2602.11287v1',
               '作者表；§II-A 三级缩放元数据；§III-B 点积流程'),
        source('liao-eth-role-2025', 'ETH Sustainable AI 2025: Heng Liao speaker biography',
               'ETH Future Computing Laboratory', '2025',
               'https://efcl.ethz.ch/events/conferences---workshops/sustainable-ai-2025/speakers.html',
               'Heng Liao 简介中的 DaVinci 软硬件架构职责', '官方会议简介', False, False),
    ]
    liao = make_profile('heng-liao', '廖恒', ['Heng Liao'], 'network', ['gpu-ai', 'physical-energy'],
        '把通信局部性和数值表示的成本放回 AI 系统协同设计。',
        'ETH 2025 活动简介记载其领导 DaVinci 软硬件架构；UB-Mesh 列其为第一及共同通讯作者，HiFloat4 列其为共同作者。职责资料不代替具体技术作品。',
        [('ub-mesh-2025', '参与以层次化 nD-FullMesh 和拓扑感知路由匹配训练通信局部性的 UB-Mesh 架构研究。'),
         ('hifloat4-2026', '参与 HiFloat4 三级共享缩放表示与面向硬件点积的低精度计算研究。')], liao_audits,
        '减少远距离通信与算术成本后，收益是否被拓扑映射、格式转换或精度损失抵消？',
        '通信局部性、拥塞、有效带宽、转换成本、精度预算、能耗',
        '通信与数值格式应分别测量；只有未被转换、拥塞和精度补偿抵消的成本节省才形成系统收益。',
        '缺少通信局部性、工作负载频繁换型或转换占主导时，特化方案未必胜出。',
        '固定模型与精度目标，分别记录通信等待、格式转换、算术执行和系统能耗。')
    niu = make_profile('xinyu-niu', '牛昕宇', ['Xinyu Niu'], 'compiler-runtime', ['gpu-ai', 'correctness'],
        '把依赖停顿、资源划分与编译期通信约束联合纳入可重构计算设计。',
        '以 Xinyu Niu 署名的 Remarn 和 Session Types 共同作者身份为依据；Session Types 的 Imperial College London 研究归属为历史背景，不推断现任职务。',
        [('remarn-trets2022', REMARN_FACT), ('session-types-can2012', SESSION_FACT)],
        [copy.deepcopy(REMARN), copy.deepcopy(SESSION)],
        '线程切换和分区后的利用率收益，能否覆盖上下文、缓冲和跨核通信成本？',
        '模型大小、依赖停顿、线程数、核划分、缓冲容量、带宽',
        '将时间维度的停顿隐藏与空间维度的资源划分分开测量，再验证通信安全约束是否保持。',
        '独立任务不足或供数已饱和时，多线程与多核划分可能增加成本而不增吞吐。',
        '固定精度与模型集合，测量利用率、吞吐、尾延迟、缓冲及总线压力，并检查通信协议约束。')
    yang_audits = [
        source('hc32-hanguang800', 'Hanguang 800 NPU – The Ultimate AI Inference Solution for Data Centers',
               'Yang Jiao；Alibaba（2020 年报告归属）', '2020-08-18', 'https://hc32.hotchips.org/',
               'Conference Day 2 / ML Inference：题名、报告人与机构', '官方技术报告议程记录', False),
        source('US20230185749A1', 'Systems and methods for parallel processing',
               'Liang Han、Chengyuan Wu、Guoyu Zhu、Rong Zhong、Yang Jiao 等共同发明人',
               '2023-06-15', 'https://patents.google.com/patent/US20230185749A1/en',
               '发明人表；Description 中 inter-chip network、DMA、load/store、push/pull 段落', '公开专利申请说明书'),
    ]
    yang = make_profile('yang-jiao-hanguang', 'Yang Jiao', [], 'gpu-ai', ['network'],
        '在历史 NPU 项目与并行互连方案中区分报告归属、传输机制和产品采用。',
        'Hot Chips 2020 官方议程将其列为 Alibaba 含光 800 报告人；Alibaba 公开专利申请列 Yang Jiao 为共同发明人。只记录该历史项目关联，不推定其现任雇主。',
        [('hc32-hanguang800', '作为技术报告人，在 Hot Chips 2020 介绍含光 800 NPU；本项核验题名与报告归属，不推断整芯片独占设计权。'),
         ('US20230185749A1', '作为共同发明人，参与以片间网络支持 NPU 间 DMA、直接 load/store 与 push/pull 传输的公开申请方案。')], yang_audits,
        '互连旁路节省的数据路径开销，是否超过寻址、同步和软件接口带来的成本？',
        '传输粒度、片间带宽、DMA 设置、load/store 延迟、同步等待',
        '分别比较大块 DMA 与细粒度远程访问；不得仅由申请文本推导量产芯片性能。',
        '软件接口、同步开销或远程访问粒度不匹配时，更直接的硬件数据路径不保证应用更快。',
        '在同一任务和一致性要求下比较吞吐、完成延迟与同步次数；产品采用另需独立证据。')
    return {p['id']: p for p in (liao, niu, yang)}


def validate_profile(p, domains):
    require(p['domain'] in domains, 'Unknown primary domain: ' + p['id'])
    require(set(p.get('relatedDomains', [])) <= domains, 'Unknown related domain')
    audits = p.get('sourceAudit', [])
    works = {s['workId'] for s in audits if s.get('primary') and s.get('substantive')}
    require(len(works) >= 2, 'Fewer than two distinct substantive works: ' + p['id'])
    require(any(s.get('primary') and s.get('substantive') and s.get('mechanismBody') for s in audits), 'Missing mechanism body: ' + p['id'])
    all_ids = {s['workId'] for s in audits}
    require(all(f['workId'] in all_ids for f in p.get('sourceFacts', [])), 'Dangling fact citation: ' + p['id'])
    for key in ('name', 'field', 'core', 'background', 'argument', 'boundary', 'diagnostic'):
        require(isinstance(p.get(key), str) and p[key].strip(), 'Missing renderer field: ' + key)
    for key in ('lens', 'skills', 'question', 'variables', 'model', 'crossover', 'counterexample', 'validation', 'transfer'):
        require(p.get('challenge', {}).get(key), 'Missing challenge field: ' + key)
    return len(works)


def apply(catalog, root, write=False):
    original = copy.deepcopy(catalog)
    require(catalog.get('research', {}).get('standard') == 'contribution-led-v1', 'Unexpected catalog schema')
    ids = [p['id'] for p in catalog['profiles']]
    require(len(ids) == len(set(ids)), 'Duplicate existing profile ids')
    old = {p['id']: copy.deepcopy(p) for p in catalog['profiles']}
    profiles = catalog['profiles']
    by_id = {p['id']: p for p in profiles}
    additions = new_profiles()
    require({'shouyi-yin', 'peng-ouyang', 'kuen-hung-tsoi'} <= set(by_id), 'Expected existing records are missing')
    added = []
    for pid in sorted(TARGETS):
        if pid not in by_id:
            require(pid in additions, 'Refusing to invent an unreviewed profile')
            p = additions[pid]
            profiles.append(p)
            by_id[pid] = p
            added.append(pid)
        p = by_id[pid]
        p['field'] = ROLES[pid]
        p['boundary'] = BOUNDARIES[pid]
        p['researchStatus'].update(status='complete', standard='contribution-led-v1', verifiedAt=DATE)
        if pid in additions:
            # Existing concurrent admissions retain their extra research and sources.
            for s in additions[pid]['sourceAudit']:
                if not any(x.get('workId') == s['workId'] for x in p['sourceAudit']):
                    p['sourceAudit'].append(copy.deepcopy(s))
                    p['sources'].append([s['title'], s['url'], s['locator']])
        if pid == 'kuen-hung-tsoi':
            for s, text in ((REMARN, REMARN_FACT), (SESSION, SESSION_FACT)):
                if not any(x.get('workId') == s['workId'] for x in p['sourceAudit']):
                    p['sourceAudit'].append(copy.deepcopy(s))
                    p['sources'].append([s['title'], s['url'], s['locator']])
                if not any(x.get('workId') == s['workId'] for x in p['sourceFacts']):
                    p['sourceFacts'].append({'workId': s['workId'], 'text': text})
                if text not in p['contributions']:
                    p['contributions'].append(text)
    pending_path = root/'research'/'yan-xie-admission-pending-20261013.json'
    pending = json.loads(pending_path.read_text()) if pending_path.exists() else None
    if PENDING in by_id:
        pending = {'id': PENDING, 'name': '谢炎', 'status': 'needs_more_evidence', 'reviewedAt': DATE,
                   'qualifyingWorkIds': ['m100-isca2026'],
                   'reason': '按本次批准的严格门槛暂留待补证：M100 项目负责人及共同作者已确认；原采访保留，但本次不计为第二项合格技术作品。',
                   'nextAction': '补第二项可归属到同一人的实质技术作品并定位个人贡献范围；不将项目负责等同于模块独占设计。',
                   'previousProfilePreserved': copy.deepcopy(by_id[PENDING])}
        catalog['profiles'] = [p for p in profiles if p['id'] != PENDING]
    require(pending is not None, 'No pending record or archival source for Yan Xie')
    profiles = catalog['profiles']
    after = {p['id']: p for p in profiles}
    require(len(profiles) == len(after), 'Duplicate resulting profile ids')
    require(TARGETS <= set(after) and PENDING not in after, 'Approved disposition was not applied')
    for pid, prior in old.items():
        if pid not in TARGETS | {PENDING}:
            require(after.get(pid) == prior, 'Unrelated profile changed: ' + pid)
    domain_ids = {d['id'] for d in catalog['domains']}
    work_counts = {pid: validate_profile(after[pid], domain_ids) for pid in sorted(TARGETS)}
    for d in catalog['domains']:
        d['members'] = [p['id'] for p in profiles if p['domain'] == d['id']]
    research = catalog['research']
    research['totalProfiles'] = len(profiles)
    research['completedTotal'] = sum(p.get('researchStatus', {}).get('status') == 'complete' for p in profiles)
    research['remainingCatalog'] = len(profiles) - research['completedTotal']
    batchpath = 'research/batches/' + BATCH + '.json'
    logs = research.setdefault('batchLogs', [research['batchLog']])
    if batchpath not in logs:
        logs.append(batchpath)
    catalog['updated'] = DATE
    report = {'date': DATE, 'scope': 'approved-six-and-one-pending', 'beforeCount': len(old), 'afterCount': len(after),
              'added': added, 'updatedExisting': sorted(TARGETS & set(old)), 'movedToPending': PENDING,
              'qualifyingWorks': work_counts, 'unrelatedProfilesPreserved': True, 'duplicates': 0,
              'catalogChanged': catalog != original, 'publication': 'not-yet-verified'}
    batchfile = root/batchpath
    if batchfile.exists():
        batch = json.loads(batchfile.read_text())
    else:
        batch = {'date': DATE, 'focus': '可重构处理器、互连与编程体系贡献核验',
                 'completedExisting': len(TARGETS & set(old)), 'completedNew': len(added),
                 'counts': {'complete': 6, 'partial': 0, 'pending': 1},
                 'records': [{'id': pid, 'name': after[pid]['name'], 'kind': 'existing' if pid in old else 'candidate',
                              'status': 'complete', 'reason': BOUNDARIES[pid], 'nextAction': ''} for pid in sorted(TARGETS)] +
                            [{'id': PENDING, 'name': '谢炎', 'kind': 'existing', 'status': 'pending',
                              'reason': pending['reason'], 'nextAction': pending['nextAction']}],
                 'notes': ['共同署名仅证明共同贡献，不证明独立设计整款芯片。',
                           '研究机制、公开专利申请与商业产品采用分别标注。',
                           'Yang Jiao 保留历史项目归属；谢炎原条目与采访材料完整保留在待补证记录。'],
                 'publication': {'status': 'pending'}}
    if write:
        (root/'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')
        pending_path.write_text(json.dumps(pending, ensure_ascii=False, indent=2)+'\n')
        batchfile.parent.mkdir(parents=True, exist_ok=True)
        batchfile.write_text(json.dumps(batch, ensure_ascii=False, indent=2)+'\n')
        # The existing renderer regenerates indexes but does not remove old cards.
        from lxml import html
        index = root/'index.html'
        page = html.fromstring(index.read_text())
        for element in page.xpath('//article[@id="yan-xie"]'):
            element.getparent().remove(element)
        index.write_text('<!doctype html>\n'+html.tostring(page, encoding='unicode', method='html')+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    catalog = json.loads((args.root/'catalog.json').read_text())
    print(json.dumps(apply(catalog, args.root, write=not args.check), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
