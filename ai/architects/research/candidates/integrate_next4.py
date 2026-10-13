#!/usr/bin/env python3
"""Integrate the qualified next-four result; preserve the initial screening snapshot.

Run from a full checkout. The original contribution validator remains authoritative.
This script never pushes, changes access, or declares a deployment successful.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BATCH = '2026-10-13-next4-followthrough'
BATCH_PATH = f'research/batches/{BATCH}.json'
DATE = '2026-10-13'
BASE = '7e4d1a5626fd91bc2152a1bd0e7ec192c1d810fb'
BASE_BLOB = '2c28862eb57ebcae28a4625bae2cb50910fbc12a'
PID = 'jun-liang-cambricon'
CANDIDATES = {
    PID: ['梁军', 'Jun Liang', 'Liang Jun'],
    'tianyi-shan-iluvatar': ['单天逸', 'Tianyi Shan', 'Shan Tianyi'],
    'yalin-zhang-enflame': ['张亚林', 'Yalin Zhang', 'Zhang Yalin'],
    'lidong-zhao-enflame': ['赵立东', 'Lidong Zhao', 'Zhao Lidong'],
}
SOURCES = [
    {
        'workId': 'liang-descriptor-wo2020200244',
        'title': '数据处理方法及装置以及相关产品 — WO2020200244A1',
        'authors': '刘少礼、王秉睿、周晓勇、庄毅敏、兰慧盈、梁军、李震、吴健华、郝勇峥',
        'date': '2020-10-08',
        'url': 'https://patents.google.com/patent/WO2020200244A1/zh',
        'locator': 'Inventor / Original Assignee；具体实施方式 S11a/S12a、张量接口单元、描述符管理及前序依赖处理',
        'type': '专利说明书正文（所列部分）',
        'contentStatus': '已直接审阅署名、优先权与所列实施方式文字；未宣称审阅全部附图。',
        'evidenceStrength': '原始专利说明书；共同署名支持共同贡献，不证明独创整个ISA或量产采用。',
        'role': '张量寻址、管理状态与依赖控制；中文身份归属',
        'primary': True, 'substantive': True, 'mechanismBody': True,
        'retrievedAt': DATE,
        'independenceKey': 'descriptor-priorities-2019-04',
        'priorityAnchors': ['CN201910272625.6', 'CN201910272411.9', 'CN201910272660.8', 'CN201910320091.X', 'CN201910319165.8', 'CN201910340177.9', 'CN201910341003.4'],
    },
    {
        'workId': 'liang-accumulation-wo2022111014',
        'title': 'Accumulation device and method, and readable storage medium — US20230229393A1',
        'authors': 'Enhe LIU、Qi LI、Boyu QIAN、Shaoli LIU、Jun LIANG',
        'date': '2023-07-20',
        'url': 'https://patents.justia.com/patent/20230229393',
        'locator': 'Cross-Reference to Related Applications；Detailed Description 的指数分组、对阶、补码累加、剩余输入再处理；Claims 3–4、6、15；Inventors',
        'type': '专利说明书正文（所列部分）',
        'contentStatus': '已直接审阅美国同族的原始说明书镜像文字；PCT/CN2021/119947 与 CN202011364680.7 交叉一致。同族只计一项。未审阅全部附图。',
        'evidenceStrength': '共同发明人及独立技术机制已核；Claim 6 的 all 1 与 Claim 15 的 not all 0 存在 sticky-bit 表述差异，未消除此差异。',
        'role': '阶码差分组累加机制及英文署名身份链；不支持IEEE逐位等价、测得PPA收益或产品采用',
        'primary': True, 'substantive': True, 'mechanismBody': True,
        'retrievedAt': DATE,
        'independenceKey': 'accumulation-cn2020113646807',
        'priorityAnchors': ['CN202011364680.7'],
        'sameWorkAliases': ['WO2022111014A1', 'CN114546331A', 'CN114546331B', 'US20230229393A1'],
        'originalWorkUrl': 'https://patents.google.com/patent/WO2022111014A1/en',
    },
]
PROFILE = {
    'id': PID, 'name': '梁军', 'aliases': ['Jun Liang'],
    'domain': 'gpu-ai', 'relatedDomains': ['memory', 'correctness'],
    'field': '张量寻址与浮点累加',
    'core': '通过描述符组织张量访问，以阶码差分组组织累加；把控制开销与数值边界一起纳入架构判断。',
    'background': '本条限定于寒武纪历史技术作品：中文专利列梁军为共同发明人；累加专利的中美同族、共同作者及优先权对应 Jun LIANG。该身份链只覆盖所列作品，不认定现任职务，也不跨公司拼接同名专利。',
    'contributions': [
        '共同署名张量描述符访问方案：指令引用描述符标识，取回形状及地址参数并生成访问地址，另设描述符管理与依赖处理路径。',
        '共同署名阶码差分组累加方案：组内对阶后转换为补码进行定点累加；未选中的输入保留并继续处理，而不是直接丢弃小量级项。',
    ],
    'argument': '编辑解读：描述符把重复地址参数转为可复用状态，但增加查表、管理及依赖等待；指数分组把宽范围对阶拆成有限范围的处理，但数据分布决定组数、额外轮次与舍入风险。两者都应比较完整处理成本，而不只比较单次运算。',
    'evidence': '两项不同优先权集合的共同署名专利，均已直接审阅所列机制正文；美国、国际及中国同族不重复计数。',
    'habits': ['以下是基于作品的编辑归纳，不是本人原话：先区分语义状态与执行机制，再核算状态维护成本。', '把输入分布、额外处理轮次和数值语义作为性能结论的前提。'],
    'questions': ['描述符复用省下多少参数传递，又增加多少状态查询、更新和依赖阻塞？', '阶码差分布改变后，累加需要几轮；抵消和舍入如何影响最终误差？'],
    'boundary': '仅支持所列方案的共同技术贡献，不证明整颗芯片主架构师身份、独创整个ISA或量产采用。累加文本对 sticky bit 的 all 1 / not all 0 表述不一致；不得据此声称IEEE逐位等价。面积、功耗与精度收益未经本次独立实验验证。',
    'diagnostic': '编辑建议：联合测量描述符复用率、管理频度与依赖等待；累加按阶码跨度、抵消比例和分组阈值分层测试，报告轮次、吞吐、能耗和相对高精度基准的误差，并单独审查异常值与次正规数。',
    'notes': [], 'sources': [[s['title'], s['url'], s['locator']] for s in SOURCES],
    'sourceAudit': SOURCES,
    'sourceFacts': [
        {'workId': SOURCES[0]['workId'], 'text': 'WO2020200244A1 将描述符标识连接到形状、地址参数和指令执行；梁军列为共同发明人。'},
        {'workId': SOURCES[1]['workId'], 'text': 'US20230229393A1 描述按阶码差分组、组内对阶与补码累加，并保留未处理输入继续迭代；Jun LIANG 列为共同发明人。'},
        {'workId': SOURCES[1]['workId'], 'text': '同一公开文本 Claim 6 与 Claim 15 的 sticky-bit 条件措辞不同，本条保留此未决数值语义限制。'},
    ],
    'awardsVerified': [], 'contributionBasis': '基于共同署名技术作品的编辑提炼；不将团队成果写成个人独创。',
    'researchStatus': {'status': 'complete', 'batch': BATCH, 'standard': 'contribution-led-v1', 'meaning': '所列共同贡献完成核验；不等于穷尽成果、消除原文歧义或确认产品采用。', 'verifiedAt': DATE},
    'challenge': {
        'lens': '重用状态与分组运算的完整成本', 'skills': ['A1', 'A2', 'A5', 'A7', 'A9'],
        'question': '局部简化何时能覆盖额外控制、重复处理和数值检查的代价？',
        'variables': '描述符复用次数、更新频率、依赖等待；阶码分布、分组阈值、轮次、抵消强度、误差预算。',
        'model': '编辑条件模型：复用收益大于描述符查表、管理与等待成本；分组方案总成本为各轮选择、对阶、累加及结果处理成本之和，并受误差上限约束。',
        'crossover': '高复用、低更新的描述符，以及能用少量分组覆盖且满足误差预算的输入，更可能获得净收益；需要实测而非预设。',
        'counterexample': '低复用且高更新的张量状态，或阶码跨度大、严重抵消而需要多轮处理的数据，可使局部节省被控制开销或误差风险抵消。',
        'validation': '建立相同语义、相同输入与相同工艺约束的对照；分别报告状态维护、累加轮次、PPA及误差分布，不只报告峰值吞吐。',
        'transfer': '适用于张量ISA、GPU描述符、混合精度归约及其他用可复用状态替代重复工作的方法评审。',
    },
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def norm(value: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', value).casefold() if c.isalnum())


def main() -> None:
    path = ROOT / 'catalog.json'
    raw = path.read_bytes()
    cat = load(path)
    before = {p['id']: p for p in cat['profiles'] if p['id'] != PID}
    if PID not in {p['id'] for p in cat['profiles']}:
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert blob == BASE_BLOB, 'Baseline changed; rebase and review before integrating.'
        assert len(before) == 378
    else:
        assert next(p for p in cat['profiles'] if p['id'] == PID) == PROFILE, 'Existing profile differs; do not overwrite.'
    alias_index = {}
    for p in before.values():
        for value in [p['id'], p['name'], *p.get('aliases', [])]:
            alias_index.setdefault(norm(value), set()).add(p['id'])
    collisions = {pid: sorted({match for alias in [pid, *names] for match in alias_index.get(norm(alias), set())}) for pid, names in CANDIDATES.items()}
    assert not any(collisions.values()), collisions
    for p in before.values():
        assert p['id'] not in CANDIDATES
    assert len({s['independenceKey'] for s in SOURCES}) == 2
    assert not set(SOURCES[0]['priorityAnchors']) & set(SOURCES[1]['priorityAnchors'])
    if PID not in {p['id'] for p in cat['profiles']}:
        cat['profiles'].append(PROFILE)
    batch = {
        'date': DATE, 'focus': '中国AI架构候选：共同贡献与系统范围复核', 'scope': 'additional', 'baseCommit': BASE,
        'plannedScope': 4, 'plannedExisting': 0, 'plannedCandidates': 4,
        'counts': {'complete': 1, 'partial': 2, 'pending': 1}, 'completedExisting': 0, 'completedNew': 1,
        'evidenceGate': 'two-distinct-primary-works-one-body-v1',
        'records': [
            {'id': PID, 'name': '梁军', 'kind': 'candidate', 'status': 'complete', 'reason': '两项不同专利的共同署名及机制正文已核，英文同族身份链和全库别名去重已完成；只收录所列贡献。', 'nextAction': None, 'sources': SOURCES},
            {'id': 'tianyi-shan-iluvatar', 'name': '单天逸', 'kind': 'candidate', 'status': 'partial', 'reason': '保留2026年1月本人技术访谈；新增定位4月19日CCF活动，但活动报道不是第二项完整技术作品。', 'nextAction': '取得该场关于Vibe Coding与硬件设计的署名幻灯片、实录或实现文档；未达标不建人物卡。'},
            {'id': 'yalin-zhang-enflame', 'name': '张亚林', 'kind': 'candidate', 'status': 'partial', 'reason': '复核方向确定为datacenter：系统产品化、软件栈与部署经济性；现有材料不支持个人GPU/GCU微架构主设计者。', 'nextAction': '继续补第二项可归属本人、包含具体系统设计机制的作品；运营访谈不充当该证据。'},
            {'id': 'lidong-zhao-enflame', 'name': '赵立东', 'kind': 'candidate', 'status': 'pending', 'reason': '按原结论暂缓。机构履历支持历史工程背景，不替代作品级技术贡献。', 'nextAction': '未取得两项合格技术作品前不入库。'},
        ],
        'notes': ['本批只新增梁军一位，其他三位不计入正式目录。', '专利共同署名、团队机制和独立性能验证分开；未认定現任职务或量产采用。', '美国、国际与中国同族不重复计数；sticky-bit原文差异保留。', '原next4候选稿保留为初筛历史快照，以本批及followthrough记录为当前状态。'],
        'publication': {'status': 'prepared', 'target': 'https://wilwan01.github.io/ai/architects/', 'note': '仅表示仓库整合准备完成；部署状态须另查GitHub Pages。'},
    }
    save(ROOT / BATCH_PATH, batch)
    logs = cat['research'].setdefault('batchLogs', [cat['research']['batchLog']])
    if BATCH_PATH not in logs:
        logs.append(BATCH_PATH)
    batches = [load(ROOT / p) for p in logs]
    ids = [r['id'] for b in batches for r in b['records']]
    assert len(ids) == len(set(ids)), 'Duplicate fixed-batch identity'
    done = {r['id'] for b in batches for r in b['records'] if r['status'] == 'complete'}
    cat['updated'] = DATE
    cat['research'].update(totalProfiles=len(cat['profiles']), completedTotal=len(done), remainingCatalog=len(cat['profiles']) - len(done))
    # Preserve the earlier additional-scope accounting; append this fixed cohort once.
    assert cat['research']['additionalPlannedScope'] in (79, 83)
    cat['research'].update(additionalPlannedScope=83, additionalCompleted=78, remainingPlanned=5)
    save(path, cat)
    snapshot_path = ROOT / 'research/candidates/2026-10-13-china-ai-next4.json'
    snapshot = load(snapshot_path)
    snapshot.update(snapshotStatus='historical-initial-screening', supersededBy=f'{BATCH}.json')
    save(snapshot_path, snapshot)
    snapshot_md = snapshot_path.with_suffix('.md')
    text = snapshot_md.read_text(encoding='utf-8')
    notice = '> 历史初筛快照：下面的零入库结论仅对应初筛时点。当前核验、整合及三位待补状态见 [后续记录](2026-10-13-next4-followthrough.md)。\n\n'
    if not text.startswith(notice):
        snapshot_md.write_text(notice + text, encoding='utf-8')
    follow = {
        'date': DATE, 'batchId': BATCH, 'initialSnapshot': '2026-10-13-china-ai-next4.json',
        'catalogIntegrated': True, 'deploymentVerified': False, 'evidenceGate': batch['evidenceGate'],
        'counts': {'candidates': 4, 'gatePassed': 1, 'newCatalogProfiles': 1, 'remainingCandidates': 3, 'catalogProfiles': 379},
        'admittedIds': [PID], 'notAdmittedIds': [p for p in CANDIDATES if p != PID],
        'dedupAudit': {'baseCommit': BASE, 'catalogBlob': BASE_BLOB, 'parsedProfiles': 378, 'normalization': 'NFKD-casefold-Unicode-alnum; ids/names/aliases', 'queryAliases': CANDIDATES, 'matchesInBaseline': collisions, 'result': 'passed'},
        'eligibleWorks': SOURCES,
        'followups': [
            {'id': 'tianyi-shan-iluvatar', 'primaryInterview': 'https://www.infoq.cn/news/hR5WX4alMiNZumPR5ukC', 'newLead': 'https://www.ccf.org.cn/Chapters/Local_Activities/Chapter_News/2026-04-23/882173.shtml', 'eventDate': '2026-04-19', 'publicationDate': '2026-04-23', 'accessStatus': 'official-indexed-report; direct-open-failed', 'countsTowardGate': False, 'finding': '官方报道指明本人讨论AI驱动开发向硬件设计延伸，但未取得该报告的具体设计正文；不是第二项已通过作品。'},
            {'id': 'yalin-zhang-enflame', 'proposedDomain': 'datacenter', 'sources': ['https://zhidx.com/p/247317.html', 'https://www.tmtpost.com/7151767.html'], 'finding': '系统产品化方向保留；2024运营访谈不计作第二项设计机制作品。'},
            {'id': 'lidong-zhao-enflame', 'finding': '暂缓，不新增履历或同名专利作为技术证据。'},
        ],
        'validation': {'integrationAssertions': 'passed', 'fullSiteValidation': 'run-original-validator-separately', 'deployment': 'not-verified-by-this-script'},
    }
    save(ROOT / f'research/candidates/{BATCH}.json', follow)
    (ROOT / f'research/candidates/{BATCH}.md').write_text(
        '# 下一批四位：后续核验与整合\n\n2026-10-13。初筛历史稿保留，本页为后续状态。\n\n'
        '**本次整合梁军一位：378 → 379。** 其两项共同署名专利的所列机制正文、不同优先权集合及中英文身份链已核。全库378位的ID、名称和别名经结构化检查，四位候选均无重复。\n\n'
        '梁军贡献范围限于张量描述符访问和分组累加。累加的美国同族正文已取得：未入组的输入保留并继续处理，不是丢弃小量级项。Claim 6与15的sticky-bit条件措辞不同；不声称IEEE逐位等价、独立测得PPA改善或量产采用。\n\n'
        '单天逸仍缺第二项独立技术作品：新定位2026年4月19日CCF会议，官方报道发表于4月23日，尚未取得具体硬件设计的报告正文。张亚林按系统产品化/数据中心方向保留，运营访谈不凑设计证据。赵立东继续暂缓。三位均未进入正式人物目录。\n\n'
        f'逐项来源与读取状态见 [{BATCH}.json]({BATCH}.json)，人物/批次字段由同一整合脚本产生。\n\n'
        '验证：整合脚本检查基线blob、别名冲突、同族计数、旧378份人物数据逐字段不变和379位目录一致性；完整历史保留、矩阵与链接须运行原站validate_contribution_batch.py。脚本不自动宣称该命令或GitHub Pages部署成功，实际结果以CI日志为准。\n', encoding='utf-8')
    subprocess.run([sys.executable, str(ROOT / 'tools/render_contribution_batch.py')], check=True)
    after = load(path)
    assert {p['id']: p for p in after['profiles'] if p['id'] != PID} == before, 'An existing profile changed'
    assert len(after['profiles']) == 379
    assert Counter(r['status'] for r in batch['records']) == batch['counts']
    assert all(pid not in {p['id'] for p in after['profiles']} for pid in CANDIDATES if pid != PID)
    print('PASS: next-four integration; 1 admitted, 3 deferred; 378 existing profiles unchanged; total 379.')


if __name__ == '__main__':
    main()
