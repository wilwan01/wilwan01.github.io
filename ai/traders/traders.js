'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const cards = [...document.querySelectorAll('details.card')];
  function filter() {
    const term = $('trader-search').value.trim().toLowerCase();
    const category = $('trader-category').value;
    let count = 0;
    cards.forEach((card, i) => {
      const group = i < 2 ? 'supply' : i < 4 ? 'pricing' : i < 6 ? 'risk' : 'execution';
      card.hidden = !((!category || category === group) && card.textContent.toLowerCase().includes(term));
      if (!card.hidden) count++;
    });
    $('trader-count').textContent = `${count} / ${cards.length} 位交易员`;
  }
  $('trader-search').addEventListener('input', filter);
  $('trader-category').addEventListener('change', filter);
  $('expand-all').addEventListener('click', () => cards.filter(c => !c.hidden).forEach(c => c.open = true));
  $('collapse-all').addEventListener('click', () => cards.forEach(c => c.open = false));
  function locate() {
    const card = cards.find(c => '#'+c.id === location.hash);
    if (card) { $('trader-search').value = ''; $('trader-category').value = ''; filter(); card.open = true; card.scrollIntoView(); }
  }
  window.addEventListener('hashchange', locate);
  const ids = ['q','q0','strike','index-price','actual-price','cost'];
  function calculate() {
    if (ids.some(id => !$(id).validity.valid || $(id).value.trim() === '')) {
      $('calc-output').textContent = '请输入有限、非负的数字；所有价格单位为美元/GPU-hour。'; return;
    }
    const [q,q0,k,i,p,cost] = ids.map(id => Number($(id).value));
    if (![q,q0,k,i,p,cost].every(Number.isFinite)) { $('calc-output').textContent = '输入超出可计算范围。'; return; }
    const revenue = q*p, hedge = q0*(k-i), basis=q*(p-i), mismatch=(q0-q)*(k-i), total=revenue+hedge-cost;
    if (![revenue,hedge,basis,mismatch,total].every(Number.isFinite)) { $('calc-output').textContent = '结果超出可计算范围。'; return; }
    const usd = n => n.toLocaleString('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2});
    $('calc-output').textContent = `实物收入 ${usd(revenue)} + 空头套保损益 ${usd(hedge)} − 成本 ${usd(cost)} = 合计 ${usd(total)}。基差贡献 ${usd(basis)}；数量错配贡献 ${usd(mismatch)}。`;
  }
  ids.forEach(id => $(id).addEventListener('input', calculate));
  document.querySelectorAll('[data-scenario]').forEach(button => button.addEventListener('click', () => {
    const values = [[730000,730000,2,1.5,1.5,0],[730000,730000,2,1.5,1.2,0],[365000,730000,2,3,2.7,0]][Number(button.dataset.scenario)];
    ids.forEach((id,i) => $(id).value = values[i]); calculate();
  }));
  filter(); calculate(); locate();
})();
