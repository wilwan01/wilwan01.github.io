(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else{root.SiliconAtlas=api;api.init();}})(typeof window==='undefined'?globalThis:window,function(){
'use strict';
const KEY='silicon-atlas-research-v1';
const quarters=['2026 Q4','2027 Q1','2027 Q2','2027 Q3','2027 Q4','2028 Q1','2028 Q2','2028 Q3','2028 Q4'];
const gates=['工作负载与尾延迟','内存与 NUMA','电力与冷却','软件与 I/O','供货与报价'];
const profiles=[
 {id:'epyc9965',vendor:'AMD',name:'EPYC 9965',unit:'x86 · 每 CPU 192 核',nodes:400,unitU:2,nodeKW:0.9,nodeCost:10000,evaluate:0,qualify:1,deploy:2,end:5},
 {id:'epyc9996',vendor:'AMD',name:'EPYC 9996',unit:'x86 · 每 CPU 256 核',nodes:600,unitU:2,nodeKW:1.2,nodeCost:14000,evaluate:1,qualify:2,deploy:4,end:7},
 {id:'xeon6980p',vendor:'Intel',name:'Xeon 6980P',unit:'x86 · 每 CPU 128 核',nodes:240,unitU:2,nodeKW:1,nodeCost:12000,evaluate:0,qualify:1,deploy:3,end:5},
 {id:'diamondrapids',vendor:'Intel',name:'Diamond Rapids',unit:'x86 · 具体 SKU 待确认',nodes:0,unitU:2,nodeKW:1.2,nodeCost:15000,evaluate:3,qualify:5,deploy:7,end:8},
 {id:'grace',vendor:'NVIDIA',name:'Grace CPU Superchip',unit:'Arm · 每双 CPU 模块 144 核',nodes:120,unitU:1,nodeKW:0.7,nodeCost:11000,evaluate:0,qualify:2,deploy:3,end:5},
 {id:'vera',vendor:'NVIDIA',name:'Vera CPU',unit:'Arm · 每 CPU 88 核',nodes:80,unitU:1,nodeKW:0.8,nodeCost:12000,evaluate:1,qualify:3,deploy:5,end:7}
];
const globalRules={rackBudget:[0,100000,true],rackU:[1,100,true],rackKW:[0.1,1000],reserveKW:[0,999],pue:[1,3],electricity:[0,10],years:[1,10,true],annualOps:[0,100000]};
const platformRules={nodes:[0,100000,true],unitU:[1,100,true],nodeKW:[0.01,1000],nodeCost:[0,10000000],evaluate:[0,8,true],qualify:[0,8,true],deploy:[0,8,true],end:[0,8,true]};
const clone=x=>JSON.parse(JSON.stringify(x));
function defaults(){return {version:1,name:'2027 容量扩展示例',settings:{rackBudget:140,rackU:40,rackKW:20,reserveKW:2,pue:1.2,electricity:0.12,years:3,annualOps:300},platforms:profiles.map(p=>({id:p.id,...Object.fromEntries(Object.keys(platformRules).map(k=>[k,p[k]])),gates:gates.map(()=>false),evidence:''}))};}
function numbers(input,rules){const clean={};if(!input||typeof input!=='object')throw Error('缺少输入。');for(const [key,[min,max,int]] of Object.entries(rules)){const n=input[key];if(typeof n!=='number'||!Number.isFinite(n)||n<min||n>max||(int&&!Number.isInteger(n)))throw Error('输入超出范围或不是有效数字：'+key);clean[key]=n;}return clean;}
function validate(raw){
 if(!raw||raw.version!==1||typeof raw.name!=='string'||!raw.name.trim()||raw.name.length>80)throw Error('计划名称或文件版本无效。');
 const settings=numbers(raw.settings,globalRules);
 if(settings.reserveKW>=settings.rackKW)throw Error('每架预留功率必须小于机架 IT 功率上限。');
 if(!Array.isArray(raw.platforms)||raw.platforms.length!==profiles.length)throw Error('计划必须包含全部六个平台。');
 const platforms=profiles.map(meta=>{const matches=raw.platforms.filter(p=>p&&p.id===meta.id);if(matches.length!==1)throw Error('平台缺失或重复。');const p=matches[0],nums=numbers(p,platformRules);
 if(!(nums.evaluate<nums.qualify&&nums.qualify<nums.deploy&&nums.deploy<=nums.end))throw Error(meta.name+' 的时间顺序应为：评估 < 验证 < 部署 ≤ 结束。');
 if(!Array.isArray(p.gates)||p.gates.length!==5||p.gates.some(g=>typeof g!=='boolean'))throw Error('验证记录无效。');
 if(typeof p.evidence!=='string'||p.evidence.length>2000)throw Error('证据说明过长或无效。');
 if(p.gates.some(Boolean)&&!p.evidence.trim())throw Error('勾选验证记录时，请填写证据说明。');
 return {id:meta.id,...nums,gates:[...p.gates],evidence:p.evidence};});
 return {version:1,name:raw.name.trim(),settings,platforms};
}
function calculate(raw){const plan=validate(raw),s=plan.settings;const rows=plan.platforms.map(p=>{const space=Math.floor(s.rackU/p.unitU),power=Math.floor((s.rackKW-s.reserveKW)/p.nodeKW+1e-10),perRack=Math.min(space,power),blocked=p.nodes>0&&perRack<1,racks=blocked?null:p.nodes===0?0:Math.ceil(p.nodes/perRack);return {id:p.id,nodes:p.nodes,perRack,racks,blocked,limit:space===power?'空间 + 功率':space<power?'空间':'功率',capex:p.nodes*p.nodeCost};});
 const nodes=rows.reduce((a,r)=>a+r.nodes,0),capex=rows.reduce((a,r)=>a+r.capex,0),blocked=rows.some(r=>r.blocked);if(blocked)return {rows,nodes,capex,blocked,racks:null,facilityKW:null,energy:null,total:null};
 const racks=rows.reduce((a,r)=>a+r.racks,0),itKW=plan.platforms.reduce((a,p)=>a+p.nodes*p.nodeKW,0)+racks*s.reserveKW,facilityKW=itKW*s.pue,energy=facilityKW*8760*s.years*s.electricity,ops=nodes*s.annualOps*s.years;
 return {rows,nodes,capex,blocked,racks,itKW,facilityKW,energy,ops,total:capex+energy+ops,overBudget:racks>s.rackBudget};}
function init(){
 const $=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),fmt=n=>new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(n),money=n=>'$'+new Intl.NumberFormat('en-US',{maximumFractionDigits:0}).format(n);
 let plan=defaults(),editing=null,storageReady=true,loaded=false;
 try{const saved=localStorage.getItem(KEY);if(saved){plan=validate(JSON.parse(saved));loaded=true;}}catch(e){storageReady=false;$('#save-status').textContent='未能读取保存的计划，当前显示示例。可导出计划备份。';}
 const status=msg=>{$('#save-status').textContent=msg;};
 function save(){try{localStorage.setItem(KEY,JSON.stringify(plan));storageReady=true;status('已保存在当前浏览器。导出计划可跨设备使用。');}catch(e){storageReady=false;status('当前浏览器无法保存；请导出计划备份。');}}
 function renderRoadmap(){const vendor=$('#vendor-filter').value;$('#roadmap-head').innerHTML='<tr><th>平台 / 架构</th>'+quarters.map(q=>'<th>'+q+'</th>').join('')+'</tr>';
 $('#roadmap-body').innerHTML=profiles.filter(p=>vendor==='all'||p.vendor===vendor).map(meta=>{const p=plan.platforms.find(p=>p.id===meta.id);return '<tr><th><button type="button" class="edit-link" data-edit="'+meta.id+'">'+meta.vendor+' '+meta.name+'</button><small>'+meta.unit+'</small><small>'+fmt(p.nodes)+' 节点 · 编辑计划</small></th>'+quarters.map((q,i)=>{const phase=i<p.evaluate||i>p.end?'':i<p.qualify?'evaluate':i<p.deploy?'qualify':'deploy';return '<td>'+(phase?'<span class="phase '+phase+'">'+({evaluate:'评估',qualify:'验证',deploy:p.nodes===0?'观察':'部署'}[phase])+'</span>':'—')+'</td>';}).join('')+'</tr>';}).join('');}
 function renderCapacity(){let candidate=clone(plan);for(const el of document.querySelectorAll('[data-global]'))candidate.settings[el.dataset.global]=el.value.trim()===''?NaN:Number(el.value);
 let result;try{candidate=validate(candidate);result=calculate(candidate);}catch(e){$('#capacity-status').textContent=e.message;$('#capacity-status').classList.add('error');$('#capacity-results').hidden=true;$('#rack-count').textContent='待修正';$('#rack-budget-note').textContent='容量输入无效';return false;}
 plan.settings=candidate.settings;$('#capacity-results').hidden=false;$('#capacity-status').classList.toggle('error',result.blocked||result.overBudget);
 $('#node-count').textContent=fmt(result.nodes);$('#rack-count').textContent=result.blocked?'不可行':fmt(result.racks)+' / '+fmt(plan.settings.rackBudget);$('#rack-budget-note').textContent=result.blocked?'有平台无法装入单个机架':result.overBudget?'超过可用机架预算':'所需 / 可用机架';
 $('#capacity-status').textContent=result.blocked?'有分配的平台无法在当前空间或功率限制下放入一个节点。请调整机架或整机参数。':result.overBudget?'计划超出机架预算 '+fmt(result.racks-plan.settings.rackBudget)+' 架。请调整分配、整机参数或机房约束。':'按当前空间与功率假设可容纳；供货、冷却和业务资格仍须分别验证。';
 $('#capex').textContent=money(result.capex);$('#facility-power').textContent=result.blocked?'—':fmt(result.facilityKW)+' kW';$('#energy-cost').textContent=result.blocked?'—':money(result.energy);$('#listed-cost').textContent=result.blocked?'—':money(result.total);
 $('#capacity-body').innerHTML=result.rows.map(r=>{const p=plan.platforms.find(p=>p.id===r.id),meta=profiles.find(p=>p.id===r.id);return '<tr><th><button type="button" class="secondary" data-edit="'+r.id+'">'+meta.name+'</button></th><td>'+fmt(p.nodes)+'</td><td>'+p.unitU+' U / '+p.nodeKW+' kW</td><td>'+money(p.nodeCost)+'</td><td>'+r.perRack+'</td><td>'+(r.blocked?'不可行':r.racks)+'</td><td>'+r.limit+'</td></tr>';}).join('');return true;}
 function renderReadiness(){const count=plan.platforms.reduce((a,p)=>a+p.gates.filter(Boolean).length,0);$('#gate-count').textContent=count+' / 30';$('#readiness-grid').innerHTML=profiles.map(meta=>{const p=plan.platforms.find(p=>p.id===meta.id),done=p.gates.filter(Boolean).length;return '<article class="readiness-card"><span class="badge">'+done+' / 5 已记录</span><h3>'+meta.name+'</h3><ul>'+gates.map((g,i)=>'<li>'+(p.gates[i]?'已记录':'待验证')+' · '+g+'</li>').join('')+'</ul><p>'+esc(p.evidence||'尚无业务测量、供货或验收证据。')+'</p><button type="button" class="secondary" data-edit="'+meta.id+'">编辑证据与计划</button></article>';}).join('');}
 function render(){ $('#plan-name').value=plan.name;for(const el of document.querySelectorAll('[data-global]'))el.value=plan.settings[el.dataset.global];renderRoadmap();renderCapacity();renderReadiness();}
 function edit(id){editing=id;const p=plan.platforms.find(p=>p.id===id),meta=profiles.find(p=>p.id===id),form=$('#platform-form');$('#platform-title').textContent=meta.vendor+' '+meta.name;for(const key of Object.keys(platformRules)){const el=form.elements.namedItem(key);if(el.tagName==='SELECT')el.innerHTML=quarters.map((q,i)=>'<option value="'+i+'">'+q+'</option>').join('');el.value=p[key];}$('#gate-fields').innerHTML='<legend>验证记录</legend>'+gates.map((g,i)=>'<label><input type="checkbox" name="gate'+i+'" '+(p.gates[i]?'checked':'')+'>'+g+'</label>').join('');form.elements.evidence.value=p.evidence;$('#edit-error').textContent='';$('#platform-dialog').showModal();}
 document.addEventListener('click',e=>{const button=e.target.closest('[data-edit]');if(button)edit(button.dataset.edit);});
 $('#close-dialog').addEventListener('click',()=>$('#platform-dialog').close());
 $('#platform-form').addEventListener('submit',e=>{e.preventDefault();const candidate=clone(plan),p=candidate.platforms.find(p=>p.id===editing),form=e.currentTarget;for(const k of Object.keys(platformRules))p[k]=Number(form.elements.namedItem(k).value);p.gates=gates.map((g,i)=>form.elements.namedItem('gate'+i).checked);p.evidence=form.elements.evidence.value;try{plan=validate(candidate);save();render();$('#platform-dialog').close();}catch(err){$('#edit-error').textContent=err.message;}});
 $('#vendor-filter').addEventListener('change',renderRoadmap);
 $('#capacity-form').addEventListener('submit',e=>e.preventDefault());$('#capacity-form').addEventListener('input',()=>{if(renderCapacity())save();});
 $('#plan-name').addEventListener('change',e=>{const name=e.target.value.trim();if(name){plan.name=name;save();}else{e.target.value=plan.name;status('情景名称不能为空。');}});
 $('#export-plan').addEventListener('click',()=>{if(!renderCapacity()){status('请先修正容量输入，再导出计划。');return;}const blob=new Blob([JSON.stringify(plan,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='silicon-atlas-plan.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('已导出当前计划。');});
 $('#import-plan').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>1000000)throw Error('计划文件超过 1 MB。');const imported=validate(JSON.parse(await file.text()));plan=imported;save();render();status('计划已导入并保存在当前浏览器。');}catch(err){status('导入失败：'+err.message);}finally{e.target.value='';}});
 $('#reset-plan').addEventListener('click',()=>{if(confirm('恢复示例将替换当前浏览器中的计划。需要保留时请先导出。')){plan=defaults();save();render();}});
 render();if(storageReady)status(loaded?'已载入当前浏览器保存的计划。':'修改将保存在当前浏览器。默认数据为示例，验证记录全部待确认。');
}
return {defaults,validate,calculate,profiles,quarters,gates,init};
});
