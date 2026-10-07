'use strict';
(() => {
  const el = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const text = value => Array.isArray(value) ? value.map(text).join('；') : value && typeof value === 'object' ? Object.entries(value).map(([k,v]) => `${k}: ${text(v)}`).join(' · ') : String(value ?? '未核验');
  const labels = {'candidate':'待补证据','identity-verified':'身份有来源','research-ready':'方法材料已核验'};
  let candidates = [], page = 0;
  const size = 20;
  const sourceLink = s => /^https?:\/\//.test(s.url || '') ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title || s.url)}</a>` : esc(s.title || '来源地址未确认');
  function render() {
    const q = el('candidate-search').value.trim().toLowerCase();
    const side = el('candidate-side').value, status = el('candidate-state').value;
    const rows = candidates.filter(c => (!side || c.side === side) && (!status || (status === 'priority' ? c.priority : c.status === status)) && JSON.stringify([c.id,c.name,c.firm,c.focus,c.roleAtSource,c.currentRole]).toLowerCase().includes(q));
    page = Math.max(0, Math.min(page, Math.ceil(rows.length / size) - 1));
    el('candidate-count').textContent = `${rows.length} / ${candidates.length} 位候选 · 第 ${page + 1} / ${Math.max(1,Math.ceil(rows.length / size))} 页`;
    el('candidate-results').innerHTML = rows.slice(page * size, (page + 1) * size).map(c => `<article class="person"><p class="tag">${esc(c.id)} · ${c.side === 'buy' ? '买方提名' : '卖方提名'}${c.priority ? ' · 优先研究' : ''}</p><h3>${esc(c.name)}</h3><p>${esc(text(c.firm))}</p><p><strong>${esc(labels[c.status] || labels.candidate)}</strong>${c.profileId ? ' · 已有方法档案' : ''}</p><p>${esc(text(c.focus))}</p><details><summary>身份、材料与待补项</summary><p><strong>来源时期角色：</strong>${esc(text(c.roleAtSource))}</p><p><strong>当前角色记录：</strong>${esc(text(c.currentRole))}</p>${c.roleNote ? `<p>${esc(c.roleNote)}</p>` : ''}<ul>${(c.identitySources || []).map(s => `<li>${sourceLink(s)}<br>${esc(s.date || '未注明发布日期')} · ${esc(s.accessed || '')}<br>${esc(s.whatVerified || '')}${s.accessLevel ? `<br>读取范围：${esc(s.accessLevel)}` : ''}</li>`).join('')}</ul>${c.research ? `<p><strong>已读材料归纳：</strong>${esc(text(c.research.thesis || '见方法档案'))}</p>` : ''}${(c.methodSources?.length || c.research?.sources?.length) ? `<p><strong>方法材料与读取范围：</strong></p><ul>${(c.methodSources?.length ? c.methodSources : c.research.sources).map(s => `<li>${sourceLink(s)} · ${esc(s.date || '日期未知')}<br>${esc(s.access || s.accessLevel || s.retrieval_level || '见方法档案的具体读取范围')}</li>`).join('')}</ul>` : ''}<p><strong>待补：</strong>${esc((c.gaps || []).map(text).join('；') || '未列出新增缺口；不等于完整覆盖或预测业绩审计。')}</p>${c.profileId ? `<p><a href="#map" data-candidate-profile="${esc(c.profileId)}">查看方法档案</a></p>` : ''}</details></article>`).join('') || '<p>没有匹配的候选人。请调整筛选条件。</p>';
    el('candidate-prev').disabled = page === 0;
    el('candidate-next').disabled = (page + 1) * size >= rows.length;
    el('candidate-results').querySelectorAll('[data-candidate-profile]').forEach(a => a.onclick = () => {
      document.dispatchEvent(new CustomEvent('analyst-select-profile', {detail:a.dataset.candidateProfile}));
    });
  }
  async function init() {
    try {
      const response = await fetch('candidate-pipeline.json?v=20261007-200');
      if (!response.ok) throw Error('candidate data unavailable');
      const data = await response.json(); candidates = data.candidates;
      const totals = Object.fromEntries(Object.keys(labels).map(k => [k,candidates.filter(c => c.status === k).length]));
      el('candidate-summary').textContent = `固定提名池：100 买方 + 100 卖方；${totals['research-ready']} 位方法材料已核验，${totals['identity-verified']} 位身份有来源，${totals.candidate} 位待补证据。角色按材料时期记录，包含历史人物及已转职人士，不代表 200 位现任行业分析师。`;
      ['candidate-search','candidate-side','candidate-state'].forEach(id => el(id).addEventListener(id === 'candidate-search' ? 'input' : 'change', () => {page = 0;render();}));
      el('candidate-prev').onclick = () => {page--;render();};
      el('candidate-next').onclick = () => {page++;render();};
      render();
    } catch (error) {el('candidate-count').textContent = '候选台账读取失败，请刷新或下载 JSON。';console.error(error);}
  }
  init();
})();
