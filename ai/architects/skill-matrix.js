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
