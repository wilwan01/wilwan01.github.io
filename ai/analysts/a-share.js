(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const text = value => Array.isArray(value) ? value.map(text).filter(Boolean).join('；') : value == null ? '' : typeof value === 'object' ? Object.values(value).map(text).join('；') : String(value);
  const el = (tag, content, cls) => { const n = document.createElement(tag); if (content != null) n.textContent = text(content); if (cls) n.className = cls; return n; };
  const label = p => p.status === 'method_sample' ? '方法样本' : '仅覆盖证据';
  let profiles = [], page = 0;
  const size = 10;
  function field(dl, title, value) { if (!text(value)) return; dl.append(el('dt', title), el('dd', value)); }
  function card(p) {
    const root = el('details', null, 'as-card'); root.id = p.id;
    const summary = el('summary');
    summary.append(el('span', `${text(p.name)} · ${text(p.institution)}`, 'as-person'), el('span', `${text(p.side)} / ${label(p)} / ${text(p.id)}`, 'as-meta'));
    root.append(summary);
    const body = el('div', null, 'as-card-body');
    const link = el('a', '链接到此人 ↗'); link.href = '#' + encodeURIComponent(p.id); body.append(link);
    const dl = el('dl');
    field(dl, '机构与角色口径', p.role_status);
    field(dl, 'AI 基础设施覆盖', p.scope_reason);
    field(dl, '可归属的来源观点', p.source_claim);
    if (p.status === 'method_sample') {
      field(dl, '本次方法样本（非长期认证）', p.method_sample);
      field(dl, '编辑重建 · 驱动模型', p.model);
      field(dl, '编辑重建 · 关键变量', p.key_variables);
      field(dl, '编辑挑战 · 反例', p.counterexample);
      field(dl, '编辑挑战 · 证伪条件', p.falsification);
      field(dl, '后续问题', p.next_question);
      field(dl, '训练能力映射', p.skills);
    } else {
      field(dl, '证据边界', '目前只确认直接覆盖 AI 基础设施；尚无足够可读、可归属内容提炼个人方法。');
    }
    field(dl, '证据缺口', p.evidence_gap); body.append(dl);
    const sources = Array.isArray(p.sources) ? p.sources : [];
    const fold = el('details', null, 'as-sources'); fold.append(el('summary', `查看来源与阅读范围（${sources.length}）`));
    const list = el('ol');
    sources.forEach(s => {
      const li = el('li'); let safeURL;
      try { const u = new URL(text(s.url)); if (u.protocol === 'http:' || u.protocol === 'https:') safeURL = u.href; } catch (_) { /* Non-web URLs are displayed without a link. */ }
      const title = text(s.title) || '来源标题未提供';
      if (safeURL) { const a = el('a', title); a.href = safeURL; a.target = '_blank'; a.rel = 'noopener noreferrer'; li.append(a); } else li.append(el('span', title));
      const meta = el('dl'); field(meta, '日期', s.date); field(meta, '实际阅读范围', s.access); field(meta, '定位', s.locator); field(meta, '署名与归属', s.attribution); li.append(meta); list.append(li);
    });
    if (!sources.length) fold.append(el('p', '暂无可展示来源；请参阅证据缺口。')); else fold.append(list);
    body.append(fold); root.append(body); return root;
  }
  function filtered() {
    const q = $('a-share-search').value.trim().toLocaleLowerCase();
    return profiles.filter(p => (!$('a-share-side').value || p.side === $('a-share-side').value) && (!$('a-share-state').value || p.status === $('a-share-state').value) && (!q || text([p.id,p.name,p.institution,p.scope_reason,p.status === 'method_sample' ? [p.method_sample,p.model,p.skills] : '']).toLocaleLowerCase().includes(q)));
  }
  function render() {
    const rows = filtered(); const pages = Math.max(1, Math.ceil(rows.length / size)); page = Math.min(page, pages - 1);
    const results = $('a-share-results'); results.replaceChildren();
    rows.slice(page * size, (page + 1) * size).forEach(p => results.append(card(p)));
    if (!rows.length) results.append(el('p', '没有匹配项。试试姓名、机构或“算力”“电源”等领域词，或清除筛选。', 'as-empty'));
    $('a-share-count').textContent = `${rows.length} 位匹配 · 第 ${page + 1} / ${pages} 页 · 每页最多 ${size} 位`;
    $('a-share-prev').disabled = page === 0; $('a-share-next').disabled = page + 1 >= pages;
  }
  function reset() { $('a-share-search').value = ''; $('a-share-side').value = ''; $('a-share-state').value = ''; page = 0; }
  function followHash() {
    let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const index = profiles.findIndex(p => p.id === id); if (index < 0) return;
    reset(); page = Math.floor(index / size); render(); const target = $(id); target.open = true; requestAnimationFrame(() => target.scrollIntoView({block:'start'}));
  }
  async function load() {
    $('a-share-retry').hidden = true; $('a-share-summary').textContent = '正在读取 A 股研究名单…';
    try {
      const response = await fetch('a-share.json?v=20261011-1'); if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json(); if (!Array.isArray(data.profiles)) throw new Error('名单格式异常');
      profiles = data.profiles.filter(p => p && typeof p.id === 'string');
      $('a-share-summary').textContent = `截至 ${text(data.as_of) || '日期待补'} · ${profiles.length} 位：买方 ${profiles.filter(p=>p.side==='买方').length} / 卖方 ${profiles.filter(p=>p.side==='卖方').length} · 方法样本 ${profiles.filter(p=>p.status==='method_sample').length} / 仅覆盖证据 ${profiles.filter(p=>p.status==='coverage_only').length}`;
      $('a-share-controls').hidden = false; $('a-share-pagination').hidden = false;
      render(); followHash();
    } catch (_) {
      $('a-share-summary').textContent = 'A 股名单暂时未能载入。请检查网络后重试，或下载 CSV 查看；本页原有思想档案仍可使用。';
      $('a-share-results').replaceChildren(); $('a-share-count').textContent = ''; $('a-share-retry').hidden = false;
      $('a-share-controls').hidden = true; $('a-share-pagination').hidden = true;
    }
  }
  ['a-share-search','a-share-side','a-share-state'].forEach(id => $(id).addEventListener(id === 'a-share-search' ? 'input' : 'change', () => { page = 0; render(); }));
  $('a-share-reset').addEventListener('click', () => { reset(); render(); $('a-share-search').focus(); });
  $('a-share-prev').addEventListener('click', () => { page--; render(); $('a-share-count').scrollIntoView({block:'nearest'}); });
  $('a-share-next').addEventListener('click', () => { page++; render(); $('a-share-count').scrollIntoView({block:'nearest'}); });
  $('a-share-retry').addEventListener('click', load); window.addEventListener('hashchange', followHash); load();
})();
