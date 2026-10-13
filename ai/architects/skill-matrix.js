(()=>{
  const table=document.getElementById('architect-skill-table');
  if(!table)return;
  const skill=document.getElementById('matrix-skill');
  const name=document.getElementById('matrix-name');
  const count=document.getElementById('matrix-count');
  const empty=document.getElementById('matrix-empty');
  const rows=[...table.tBodies[0].rows];
  const columns=[...table.querySelectorAll('[data-skill]')];
  function update(){
    const selected=skill.value;
    const query=name.value.trim().toLocaleLowerCase();
    let visible=0;
    for(const row of rows){
      const matchesSkill=!selected||row.dataset.skills.split(' ').includes(selected);
      const matchesName=!query||row.dataset.name.toLocaleLowerCase().includes(query);
      row.hidden=!(matchesSkill&&matchesName);
      if(!row.hidden)visible++;
    }
    for(const cell of columns)cell.classList.toggle('selected-skill',!!selected&&cell.dataset.skill===selected);
    count.textContent=`显示 ${visible} / ${rows.length} 位人物`;
    empty.hidden=visible!==0;
  }
  skill.addEventListener('change',update);
  name.addEventListener('input',update);
  update();
})();

/* Keep the reading directory aligned with the visible content. */
(() => {
  const toc = document.querySelector('.reading .toc');
  if (!toc) return;
  const links = new Map([...toc.querySelectorAll('a[href^="#"]')]
    .map(link => [link.getAttribute('href').slice(1), link]));
  // Document order matters: newly added profiles need not be in catalog order.
  const sections = [...document.querySelectorAll('.domain-heading h2[id], article.profile[id]')]
    .filter(section => links.has(section.id));
  if (!sections.length) return;
  const desktop = window.matchMedia('(min-width: 681px)');
  let current = null;
  let frame = 0;

  function update() {
    frame = 0;
    const line = Math.min(160, window.innerHeight * 0.25);
    let low = 0, high = sections.length - 1, index = -1;
    while (low <= high) {
      const mid = (low + high) >> 1;
      if (sections[mid].getBoundingClientRect().top <= line) {
        index = mid;
        low = mid + 1;
      } else high = mid - 1;
    }
    const link = index < 0 ? null : links.get(sections[index].id);
    const changed = link !== current;
    if (changed) {
      if (current) current.removeAttribute('aria-current');
      current = link;
      if (current) {
        current.setAttribute('aria-current', 'location');
        if (desktop.matches) current.closest('details').open = true;
      }
    }
    if (!current || !desktop.matches) return;
    const group = current.closest('details');
    // Preserve manual directory browsing and collapsed groups until the
    // reader reaches another section.
    if (!group.open) return;
    const item = current.getBoundingClientRect();
    const box = toc.getBoundingClientRect();
    if (item.top < box.top + 12 || item.bottom > box.bottom - 12) {
      // Scroll only the sidebar: scrollIntoView would also move the article.
      toc.scrollTop += item.top - box.top - (toc.clientHeight - item.height) / 2;
    }
  }
  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  window.addEventListener('hashchange', schedule);
  window.addEventListener('pageshow', schedule);
  // Expanding a profile can move every section below it.
  const content = sections[0].closest('.reading');
  content.addEventListener('toggle', event => {
    if (!toc.contains(event.target)) schedule();
  }, true);
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(schedule);
    observer.observe(content);
  }
  document.fonts?.ready.then(schedule);
  schedule();
})();
