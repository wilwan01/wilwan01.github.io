(function(){
  'use strict';
  function compare(v){
    const values=[v.oldCost,v.newCost,v.oldRate,v.newRate,v.oldUtil,v.newUtil];
    if(values.some(x=>!Number.isFinite(x))||v.oldCost<=0||v.newCost<=0||v.oldRate<=0||v.newRate<=0||v.oldUtil<0||v.oldUtil>100||v.newUtil<0||v.newUtil>100)return {valid:false,reason:'请填写正的成本和吞吐；有效利用率须在 0–100% 之间。'};
    if(!v.feasible)return {valid:false,reason:'尚未通过相同质量、容量与 SLO 检验：价格再低也不能据此认定可替代。'};
    if(v.oldUtil===0||v.newUtil===0)return {valid:false,reason:'零有效产出时，每项任务成本无定义；先确认真实需求和可用时间。'};
    const oldOutput=3600*v.oldRate*v.oldUtil/100,newOutput=3600*v.newRate*v.newUtil/100;
    const oldUnit=1e6*v.oldCost/oldOutput,newUnit=1e6*v.newCost/newOutput;
    return {valid:true,oldUnit,newUnit,oldCeiling:v.newCost*oldOutput/newOutput,oldUtilFloor:100*v.oldCost*v.newRate*(v.newUtil/100)/(v.newCost*v.oldRate),ratio:oldUnit/newUnit};
  }
  if(typeof module!=='undefined'&&module.exports)module.exports={compare};
  if(typeof document==='undefined')return;
  const form=document.getElementById('lifecycle-calculator');if(!form)return;
  const keys=['oldCost','newCost','oldRate','newRate','oldUtil','newUtil'];
  const el=id=>document.getElementById(id),money=x=>'$'+x.toFixed(3);
  function render(){
    const v=Object.fromEntries(keys.map(k=>[k,el(k).value.trim()===''?NaN:Number(el(k).value)]));v.feasible=el('feasible').checked;
    const r=compare(v);el('calc-results').hidden=!r.valid;
    if(!r.valid){el('calc-status').textContent=r.reason;return;}
    el('old-unit').textContent=money(r.oldUnit);el('new-unit').textContent=money(r.newUnit);el('old-ceiling').textContent=money(r.oldCeiling)+'/小时';
    el('old-util-floor').textContent=r.oldUtilFloor>100?'需要 '+r.oldUtilFloor.toFixed(1)+'% 利用率，当前假设下不可达。':'旧方案需至少 '+r.oldUtilFloor.toFixed(1)+'% 有效利用率才与新方案持平。';
    const max=Math.max(r.oldUnit,r.newUnit);el('old-bar').style.width=(100*r.oldUnit/max)+'%';el('new-bar').style.width=(100*r.newUnit/max)+'%';
    el('old-bar-value').textContent=money(r.oldUnit);el('new-bar-value').textContent=money(r.newUnit);
    let verdict=Math.abs(r.ratio-1)<1e-9?'两方案的单位成本相同。':r.ratio<1?'旧方案单位成本低 '+((1-r.ratio)*100).toFixed(1)+'%。':'新方案单位成本低 '+((1-1/r.ratio)*100).toFixed(1)+'%。';
    el('calc-status').textContent=verdict+' 仅在本组同工作负载假设下成立；这不是具体 GPU 的测量结果。';
  }
  const defaults={oldCost:.8,newCost:2.4,oldRate:1000,newRate:2000,oldUtil:60,newUtil:60};
  function preset(newRate){for(const k of keys)el(k).value=defaults[k];el('newRate').value=newRate;el('feasible').checked=true;render();}
  el('base-case').addEventListener('click',()=>preset(2000));el('fast-new-case').addEventListener('click',()=>preset(4000));
  form.addEventListener('input',render);form.addEventListener('change',render);form.addEventListener('submit',e=>e.preventDefault());render();
})();
