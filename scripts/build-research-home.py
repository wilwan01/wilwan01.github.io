#!/usr/bin/env python3
"""Refresh the two research homepages from existing report cards and dated evidence."""
from pathlib import Path
import re, json, html
ROOT=Path(__file__).resolve().parents[1]
AI=ROOT/'ai'
esc=html.escape
AMD='https://ir.amd.com/news-events/press-releases/detail/1305/amd-showcases-6th-gen-amd-epyc-processors-to-lead-next-era-of-ai-and-enterprise-computing'
for lang,file in [('zh','index.html'),('en','index-en.html')]:
 p=AI/file;s=p.read_text();en=lang=='en';pick=lambda zh,en_:en_ if en else zh
 cards=re.findall(r'<section class="card"[^>]*>[\s\S]*?</section>',s)
 assert len(cards)==15,len(cards)
 updated=[]
 for card in cards:
  slug=re.search(r'class="primary" href="([a-z]+)-(?:zh|en).html"',card)[1]
  card=re.sub(r'<p class="report-freshness">[\s\S]*?</p>','',card)
  if slug=='amd':
   source='amd-'+lang+'.html';cutoff='2026-09-27'
   assert ('27 September 2026' in (AI/'amd-en.html').read_text())
  else:
   source=next('files/'+x.name for x in (AI/'files').glob('*Canonical_Data.json') if x.name.lower().startswith(slug+'_'))
   cutoff=json.loads((AI/source).read_text())['cutoff']
  note=pick('后续变化尚未全面纳入原报告。','Later developments are not comprehensively incorporated in this report.')
  if slug=='amd':note=pick('补充核验：2026-11-12；原报告未整体更新。','Supplement checked: 2026-11-12; the full report has not been refreshed.')
  meta=f'<p class="report-freshness">{pick("报告证据截止","Report evidence cutoff")} <a href="{source}"><time datetime="{cutoff}">{cutoff}</time></a><br>{note}</p>'
  card=card.replace('<div class="actions">',meta+'<div class="actions">')
  card=card.replace('<h2>','<h3>').replace('</h2>','</h3>')
  updated.append(card)
 title=pick('AI 基础设施研究','AI Infrastructure Research')
 desc=pick('连接产品机制、市场证据与架构判断。搜索公司、人物与技术，追踪重要变化，深入阅读原始研究。','Connect product mechanisms, market evidence and architecture decisions. Search companies, people and technologies; follow material changes and explore the underlying research.')
 s=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',s)
 s=re.sub(r'<meta content="[^"]*" name="description"\s*/?>',f'<meta content="{esc(desc)}" name="description"/>',s)
 s=re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*',r'\g<1>'+title,s)
 s=re.sub(r'(<meta (?:property="og:description"|name="twitter:description") content=")[^"]*',r'\g<1>'+esc(desc),s)
 s=s.replace('<link href="style.css" rel="stylesheet"/>','<link href="style.css" rel="stylesheet"/>')
 if 'home.css' not in s:s=s.replace('</head>','<link href="home.css?v=20261112" rel="stylesheet"/></head>')
 # Home navigation remains in the reader's current language.
 s=re.sub(r'<a href="/ai/index(?:-en)?\.html"[^>]*>(?:产品分析|Product Analysis|研究首页|Research home)</a>',f'<a href="/ai/{file}" aria-current="page">{pick("研究首页","Research home")}</a>',s,count=1)
 s=s.replace('ARCHITECTURE / 2015—2026','ARCHITECTURE · MARKETS · EVIDENCE')
 search=f'<form class="home-search" action="/ai/search.html" method="get" role="search"><label for="home-query">{pick("搜索整个研究库","Search the research library")}</label><div><input id="home-query" name="q" type="search" required placeholder="{pick("公司、产品、架构师或技术问题…","Company, product, architect or technical question…")}"><button type="submit">{pick("搜索","Search")}</button></div><p>{pick("例如","Try")}: <a href="/ai/search.html?q=CXL">CXL</a> · <a href="/ai/search.html?q=Crusoe">Crusoe</a> · <a href="/ai/search.html?q=Deepak%20Goel">Deepak Goel</a></p></form>'
 changes=[
  (pick('产品状态 · 公告 2026-11-10','Product status · announced 2026-11-10'),pick('AMD SP7：上市与云可用分开判断','AMD SP7: separate chip launch from cloud availability'),pick('已核验公告中的芯片上市与 OEM 交付；云实例普遍可用、HDv2 预览及客户验证仍须分别追踪。','The reviewed announcement distinguishes processor availability and OEM shipping from upcoming cloud access, HDv2 preview and customer validation.'),pick('采购时按 SKU、系统、云区域分别确认。厂商披露未等于独立性能验证。','Check the SKU, system and cloud region separately. Vendor disclosures are not independent performance verification.'),AMD,pick('官方公告','Official announcement')),
  (pick('研究补充 · 2026-11-12','Research addition · 2026-11-12'),pick('Neocloud：从服务菜单到实际交付','Neoclouds: from service menus to delivered capacity'),pick('加入 Nebius、Lambda、Fluidstack、GMI Cloud、IREN 与 Crusoe，保留来源和服务范围。','Coverage now includes Nebius, Lambda, Fluidstack, GMI Cloud, IREN and Crusoe, with sources and service boundaries.'),pick('设施、电力规划与可租 GPU 容量分开核算；服务文档不能证明实时库存。','Separate facility and power plans from rentable GPU capacity; documentation does not prove live inventory.'),'/ai/customers/',pick('查看需求与买家','Explore customers and demand')),
  (pick("事件分析 · 2026-11-12","Event analysis · 2026-11-12"),pick("Jensen Huang 离任：NVDA 估值与执行风险","Jensen Huang’s departure: NVDA valuation and execution risk"),pick("用十种分析师方法，拆解接班安排、平台执行、竞争优势持续期与估值敏感性。","Ten analyst frameworks examine succession, platform execution, competitive-advantage duration and valuation sensitivity."),pick("短期盈利受损尚未证实；重点跟踪技术骨干、后续交付与客户采购变化。","Near-term earnings damage is unproven; track technical leadership, subsequent deliveries and customer purchasing decisions."),"/ai/analysts/cases/nvda-jensen-departure-20261112.html",pick("阅读离任分析","Read the departure analysis (中文)")),
 ]
 recent='<section class="home-section" id="recent-updates"><h2>'+pick('近期重要变化','Recent material changes')+'</h2><p class="section-note">'+pick('区分当期事件、研究补充与历史证据；各材料保留自己的截止日期。','Current events, research additions and historical evidence are labeled separately; sources retain their own cutoffs.')+'</p><div class="update-grid">'
 for kind,t,body,impact,url,label in changes:
  link_lang=' hreflang="zh-CN"' if en and url=='/ai/analysts/cases/nvda-jensen-departure-20261112.html' else ''
  recent+=f'<article class="update-card"><p class="update-kind">{kind}</p><h3>{t}</h3><p>{body}</p><p class="implication">{impact}</p><a href="{url}"{link_lang}>{label} →</a></article>'
 recent+='</div></section>'
 paths=[('/ai/'+file+'#company-reports',pick('比较产品与代际','Compare products and generations'),pick('从 CPU、加速器与互连机制开始。','Start with CPU, accelerator and interconnect mechanisms.')),('/ai/earnings/',pick('理解需求与经济性','Understand demand and economics'),pick('连接财报证据、买家需求与技术约束。','Connect earnings evidence, buyer demand and technical constraints.')),('/ai/architects/',pick('研究架构决策','Study architecture decisions'),pick('沿作品、人物与方法追踪设计取舍。','Trace design tradeoffs through works, people and methods.'))]
 routes='<section class="home-section" aria-labelledby="path-title"><h2 id="path-title">'+pick('从研究问题进入','Start with a research question')+'</h2><div class="research-paths">'+''.join(f'<a href="{u}"><strong>{t}</strong><span>{d}</span></a>' for u,t,d in paths)+'</div></section>'
 intro=f'<section class="home-hero"><p class="kicker">{pick("技术 × 市场 × 证据","Technology × markets × evidence")}</p><h1>{title}</h1><p class="home-lead">{desc}</p>{search}</section>'
 reports=f'<section id="company-reports" class="home-section"><div class="section-heading"><div><h2>{pick("公司报告","Company reports")}</h2><p>{pick(str(len(updated))+" 家公司研究 · 中英双语",str(len(updated))+" company studies · Chinese and English")}</p></div><details class="collection-download"><summary>{pick("下载历史报告合集","Download historical collection")}</summary><p><a download href="files/AI_Infrastructure_All_15_Companies.zip">ZIP · {pick("全部报告与资料","Reports and supporting files")}</a></p><small>{pick("历史快照；各报告截止日期见下方卡片。","Historical snapshots; see each card for its report cutoff.")}</small></details></div><div class="grid">'+''.join(updated)+'</div></section>'
 footer='<footer class="footer">'+pick('研究范围：2015–2026。页面更新不改变报告原始截止日期。','Research coverage: 2015–2026. A homepage update does not change a report’s evidence cutoff.')+' <a href="/ai/method/">'+pick('研究方法与术语','Research method and glossary')+'</a></footer>'
 s=re.sub(r'<main>[\s\S]*?</main>','<main>'+intro+recent+routes+reports+footer+'</main>',s,count=1)
 p.write_text(s)
print('Built Chinese and English homepages; 15 existing company cards preserved per language.')
