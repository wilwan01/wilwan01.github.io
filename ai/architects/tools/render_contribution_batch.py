#!/usr/bin/env python3
"""Render audited contribution profiles and synchronize all catalog indexes.
Uses Python 3 + lxml. Re-runs are idempotent; preserves unaudited profile markup.
"""
import json
from pathlib import Path
from html import escape as esc
from lxml import html,etree
ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/'catalog.json').read_text());profiles=catalog['profiles'];domains={d['id']:d for d in catalog['domains']};numbers={p['id']:i+1 for i,p in enumerate(profiles)}
batch=json.loads((ROOT/'research/batches/2026-10-06.json').read_text())
counts=batch['counts'];progress=f"本批完成 {counts['complete']} 位：深化既有 {batch['completedExisting']} 位、新增候选 {batch['completedNew']} 位；部分完成 {counts.get('partial',0)} 位，待补 {counts.get('pending',0)} 位。"
page=html.fromstring((ROOT/'index.html').read_text())
def E(tag,text=None,**attrs):
 e=etree.Element(tag,attrib={k.rstrip('_').replace('_','-'):str(v) for k,v in attrs.items()});e.text=text;return e
def append(parent,tag,text=None,**attrs):e=E(tag,text,**attrs);parent.append(e);return e
def link(url,label):return E('a',label,href=url,rel='noreferrer' if url.startswith('http') else '')
def fragment(s):return html.fragment_fromstring(s)
skillnames={e.get('id').split('-')[-1].upper():e.xpath('.//h3')[0].text_content()[3:].strip() for e in page.xpath('//article[contains(@class,"reasoning-skill")]')}
def render(p):
 a=E('article',id=p['id'],class_='profile',data_research_status='complete')
 append(a,'div',f"{numbers[p['id']]} · {p['field']}",class_='profile-number');append(a,'h2',p['name'])
 tags=append(a,'p','主领域：',class_='domain-tags');primary=link('#domain-'+p['domain'],domains[p['domain']]['label']);tags.append(primary)
 related=p.get('relatedDomains',[])
 if related:primary.tail=' · 关联领域：'
 for i,d in enumerate(related):
  x=link('#domain-'+d,domains[d]['label']);x.tail=' ／ ' if i<len(related)-1 else None;tags.append(x)
 append(a,'p',p['core'],class_='thesis');append(a,'h3','最重要贡献')
 ul=append(a,'ul')
 for c in p['contributions']:append(ul,'li',c)
 for w in p.get('awardsVerified',[]):
  x=append(a,'p',f"{w['name']} · {w['year']}：{w['citationZh']}（官方理由的中文转述） ",class_='award-citation');x.append(link(w['url'],'原始来源'))
 if not p.get('awardsVerified'):append(a,'p','以上为基于署名作品的编辑提炼，非官方获奖理由。',class_='contribution-origin')
 append(a,'p','本次关键贡献研究已核验 · 2026-10-06；不表示穷尽个人成果。',class_='profile-number')
 de=append(a,'details',class_='research-detail');append(de,'summary','展开：背景、机制、取舍、诊断与来源')
 append(de,'h3','背景与贡献归属');append(de,'p',p['background'])
 if p.get('sourceFacts'):
  append(de,'h3','来源事实 · 与编辑解读分列');facts=append(de,'ul')
  audit={s['workId']:s for s in p['sourceAudit'] if s.get('workId')}
  for fact in p['sourceFacts']:
   li=append(facts,'li',fact['text']+' ');s=audit[fact['workId']];li.append(link(s['url'],s['title']))
 append(de,'h3','机制与核心论证 · 编辑解读');append(de,'p',p['argument'])
 append(de,'h3','思维方式');ul=append(de,'ul')
 for h in p['habits']:append(ul,'li',h)
 append(de,'h3','可复用提问');ul=append(de,'ul')
 for q in p['questions']:append(ul,'li',q)
 limits=append(de,'div',class_='limits');append(limits,'h3','适用边界');append(limits,'p',p['boundary']);append(limits,'h3','建议诊断 · 编辑提炼');append(limits,'p',p['diagnostic'])
 ch=p['challenge'];cc=append(de,'section',class_='limits challenge-card',aria_label=ch['lens']);append(cc,'h3','架构挑战者 · '+ch['lens']);append(cc,'p',ch['question'],class_='thesis')
 sk=append(cc,'p','技能：',class_='skill-links')
 for k in ch['skills']:x=link('#skill-'+k.lower(),k+' '+skillnames[k]);x.set('class','skill-link');x.tail=' ';sk.append(x)
 dl=append(cc,'dl')
 for label,key in [('变量与比较边界','variables'),('条件性模型 · 编辑提炼','model'),('交叉条件','crossover'),('最强反例','counterexample'),('生产验证','validation'),('跨领域迁移','transfer')]:append(dl,'dt',label);append(dl,'dd',ch[key])
 append(de,'h3','已核验来源与证据范围');ol=append(de,'ol',class_='source-audit')
 for s in p['sourceAudit']:
  li=append(ol,'li');li.append(link(s['url'],s['title']));append(li,'p',f"{s['authors']} · {s['date']} · {s['type']}；{s['locator']}。{s['contentStatus']}；证据：{s['evidenceStrength']}；用途：{s['role']}。")
 legacy=append(de,'details',class_='sources');append(legacy,'summary','保留的代表来源');ol=append(legacy,'ol')
 for title,url,role in p['sources']:li=append(ol,'li');li.append(link(url,title));append(li,'small',role)
 if p.get('notes'):
  pp=append(de,'p','相关短文：',class_='connections')
  for nid,title in p['notes']:x=link('/ai/notes/'+nid+'.html',title);x.tail=' ';pp.append(x)
 a.append(link('#directory','回到人物名单'));return a
for p in profiles:
 if p.get('researchStatus',{}).get('standard')!='contribution-led-v1':continue
 new=render(p);old=page.xpath('//article[@id="'+p['id']+'"]')
 if old:old[0].getparent().replace(old[0],new)
 else:page.xpath('//section[contains(@class,"domain-block")][@aria-labelledby="domain-'+p['domain']+'"]')[0].append(new)
# All directory counts, entries and contribution summaries come from catalog.
directory=page.xpath('//*[@id="directory"]')[0];directory.xpath('./h2')[0].text=f'按领域浏览 · {len(profiles)} 位人物'
for d in catalog['domains']:
 members=[p for p in profiles if p['domain']==d['id']];d['members']=[p['id'] for p in members]
 sec=page.xpath('//*[@id="directory-'+d['id']+'"]')[0];h=sec.xpath('./h3')[0];h[0].tail=f' · {len(members)} 位'
 body=sec.xpath('.//tbody')[0];body.clear()
 for p in members:
  tr=append(body,'tr');append(tr,'td',str(numbers[p['id']]));td=append(tr,'td');td.append(link('#'+p['id'],p['name']));append(tr,'td',p['field']);append(tr,'td',p['core'])
 page.xpath('//*[@id="domain-'+d['id']+'"]/span')[0].text=f'{len(members)} 位'
 directory.xpath('./nav/a[@href="#domain-'+d['id']+'"]/span')[0].text=f'{len(members)} 位'
(ROOT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
# Sidebar navigation also derives from the catalog (including earlier additions).
toc=page.xpath('//aside[@class="toc"]')[0];toc.clear();toc.set('class','toc');toc.set('aria-label','领域与人物目录')
for d in catalog['domains']:
 members=[p for p in profiles if p['domain']==d['id']];de=append(toc,'details',open='open');append(de,'summary',f"{d['label']} · {len(members)}");x=link('#domain-'+d['id'],'阅读本领域');x.set('class','domain-jump');de.append(x)
 for p in members:de.append(link('#'+p['id'],p['name']))
# Skill table, selectable counts, accessible caption and initial status.
table=page.xpath('//*[@id="architect-skill-table"]')[0];body=table.xpath('./tbody')[0];body.clear()
for p in profiles:
 skills=p['challenge']['skills'];tr=append(body,'tr',data_name=p['name'],data_skills=' '.join(skills));th=append(tr,'th',scope='row');th.append(link('#'+p['id'],p['name']));append(tr,'td',domains[p['domain']]['label'],class_='matrix-domain')
 for n in range(1,11):
  k='A'+str(n);yes=k in skills;td=append(tr,'td',class_='skill-cell '+('associated' if yes else 'unmarked'),data_skill=k);append(td,'span','✓' if yes else '—',aria_label=skillnames[k]+('：已关联' if yes else '：未标注'))
 td=append(tr,'td',class_='matrix-mobile-skills')
 for k in skills:x=link('#skill-'+k.lower(),k);x.set('class','skill-link');x.tail=' ';td.append(x)
table.xpath('./caption')[0].text=f'{len(profiles)} 位人物与 A1–A10 技能的关联'
select=page.xpath('//*[@id="matrix-skill"]')[0]
for option in select:
 k=option.get('value');option.text=f'{k} · {skillnames[k]} · {sum(k in p["challenge"]["skills"] for p in profiles)} 位' if k else f'全部技能 · {len(profiles)} 位人物'
page.xpath('//*[@id="matrix-count"]')[0].text=f'显示 {len(profiles)} / {len(profiles)} 位人物'
stat=page.xpath('//div[@class="stats"]')[0];stat[0].text=str(len(profiles));stat[0].tail=' 位人物 · 更新 '+catalog['updated']
intro=page.xpath('//div[@class="intro"]/div[1]/p')[0];intro.text='以最重要贡献为阅读主线，结合官方获奖理由与代表作品，解释突破、机制与适用边界。贡献式展示按已核验研究逐批更新。'
existing=page.xpath('//*[@id="research-progress"]')
if existing:existing[0].getparent().remove(existing[0])
b=E('section',id='research-progress',class_='directory');append(b,'h2','研究进度 · 2026-10-06');append(b,'p',progress+'计划总范围为原 250 位与 50 名候选；另保留此前已新增的 Tushar Krishna。');pp=append(b,'p');pp.append(link('research/batches/2026-10-06.html','逐人状态、证据与待办'));pp[-1].tail=' · ';pp.append(link('research/batches/2026-10-06.json','机器可读来源审计'))
page.xpath('//main')[0].insert(1,b)
(ROOT/'index.html').write_text('<!doctype html>\n'+html.tostring(page,encoding='unicode',method='html')+'\n')
# Public batch report, readable without JS.
batch=json.loads((ROOT/'research/batches/2026-10-06.json').read_text());out=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CPU 与平台研究批次 · 2026-10-06</title><link rel="stylesheet" href="/ai/style.css"><link rel="stylesheet" href="../../thoughts.css"><style>table{border-collapse:collapse;width:100%;font-size:15px}td,th{padding:10px;border:1px solid #ccd6dc;text-align:left;vertical-align:top}td:first-child{width:20%}.research-detail summary{cursor:pointer}</style><main><h1>CPU 与平台 · 2026-10-06</h1><p>固定批次 76 位；'+esc(progress)+'完成仅指选定关键贡献与证据通过核验。</p><p><a href="../../">返回人物目录</a> · <a href="2026-10-06.json">完整来源审计 JSON</a></p><p>以官方获奖理由式的最重要贡献作为主线；无奖项者明确标为编辑提炼。完整机制与边界放入展开内容，历史资料保留。</p><table><thead><tr><th>人物</th><th>类别</th><th>状态</th><th>结论与待办</th></tr></thead><tbody>']
for x in batch['records']:
 name=esc(x['name']);name=f'<a href="../../#{x["id"]}">{name}</a>' if x['status']=='complete' else name
 out.append(f'<tr><td>{name}</td><td>{"既有" if x["kind"]=="existing" else "候选"}</td><td>{dict(complete="完成",partial="部分完成",pending="待补")[x["status"]]}</td><td>{esc(x["reason"])} {esc(x["nextAction"] or "")}</td></tr>')
out.append('</tbody></table><h2>证据与归属说明</h2><ul>')
for n in batch['notes']:out.append('<li>'+esc(n)+'</li>')
out.append('</ul><p>已核验内容通过 Pages 部署与公开文件一致性检查。<a href="'+esc(batch['publication'].get('verificationRecord','2026-10-06-deployment.json'))+'">查看上线核验记录</a>。</p></main></html>' if batch['publication']['status']=='published' else '</ul><p>页面提交后须另核对 GitHub Pages 部署与公开 catalog；此日志不预先宣称上线。</p></main></html>')
(ROOT/'research/batches/2026-10-06.html').write_text('\n'.join(out)+'\n')
print(f'Rendered {len(profiles)} profiles; audited cards: {sum(p.get("researchStatus",{}).get("standard")=="contribution-led-v1" for p in profiles)}')
