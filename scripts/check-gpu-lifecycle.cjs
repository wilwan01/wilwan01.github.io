const assert=require('node:assert/strict');
const fs=require('node:fs');
const {compare}=require('../ai/analysts/cases/gpu-lifecycle.js');
const base={oldCost:.8,newCost:2.4,oldRate:1000,newRate:2000,oldUtil:60,newUtil:60,feasible:true};
const near=(a,b)=>assert(Math.abs(a-b)<1e-8,`${a} != ${b}`);
const r=compare(base);assert(r.valid);near(r.oldUnit,10/27);near(r.newUnit,5/9);near(r.oldCeiling,1.2);near(r.oldUtilFloor,40);
near(compare({...base,oldCost:1.2}).ratio,1);
assert(compare({...base,newRate:4000}).ratio>1);
near(compare({...base,oldRate:2000,newRate:4000}).oldUnit,r.oldUnit/2);
for(const v of [{oldUtil:0},{newUtil:0},{oldUtil:101},{oldCost:-1},{oldRate:0},{newCost:NaN},{feasible:false}])assert.equal(compare({...base,...v}).valid,false);
console.log('Economics: worked examples, reversal, equality, unit scaling and infeasible inputs passed.');
if(process.argv.includes('--unit-only'))process.exit(0);
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch(),origin='http://127.0.0.1:8765',path='/ai/analysts/cases/gpu-lifecycle-workloads-20261113.html';
 const report={sha:process.env.TESTED_SHA,modelTests:'passed',rows:[]};
 try{
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
  const page=await browser.newPage({viewport}),errors=[],bad=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(origin)&&r.status()>=400)bad.push(r.url())});
  await page.goto(origin+path,{waitUntil:'networkidle'});
  assert.equal(await page.locator('h1').count(),1);assert.equal(await page.locator('main>section').count(),8);assert.equal(await page.locator('.research-nav a').count(),15);
  assert.equal(await page.locator('#old-unit').innerText(),'$0.370');assert.equal(await page.locator('#new-unit').innerText(),'$0.556');
  await page.locator('#fast-new-case').click();assert.equal(await page.locator('#new-unit').innerText(),'$0.278');assert((await page.locator('#calc-status').innerText()).includes('新方案单位成本低'));
  await page.locator('#oldUtil').fill('0');assert.equal(await page.locator('#calc-results').isVisible(),false);assert((await page.locator('#calc-status').innerText()).includes('无定义'));
  await page.locator('#base-case').click();await page.locator('#oldRate').fill('');assert.equal(await page.locator('#calc-results').isVisible(),false);
  await page.locator('#base-case').click();await page.locator('#feasible').uncheck();assert.equal(await page.locator('#calc-results').isVisible(),false);
  await page.locator('#base-case').click();assert.equal(await page.locator('#calc-results').isVisible(),true);
  assert.deepEqual(await page.locator('a[href^="#"]').evaluateAll(as=>as.map(a=>a.getAttribute('href')).filter(h=>!document.getElementById(h.slice(1)))),[]);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);
  await page.screenshot({path:`browser-results/gpu-lifecycle-${viewport.width}.png`,fullPage:true});
  for(const entry of ['/ai/analysts/','/ai/analysts/thoughts.html']){
   await page.goto(origin+entry,{waitUntil:'networkidle'});await page.locator('#gpu-lifecycle-case a').click();await page.waitForURL('**'+path);
  }
  await page.goto(origin+'/ai/search.html?q='+encodeURIComponent('GPU lifecycle'),{waitUntil:'networkidle'});
  const result=page.locator(`#results a[href="${path}"]`);await result.waitFor({state:'visible'});assert.equal(await result.count(),1);await result.click();await page.waitForURL('**'+path);
  assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);report.rows.push({viewport,calculator:true,infeasibleStates:true,entryLinks:2,search:true,anchors:true,noOverflow:true});await page.close();
 }
 report.status='passed';
 }catch(e){report.status='failed';report.error=e.stack;throw e}finally{fs.writeFileSync('browser-results/gpu-lifecycle-report.json',JSON.stringify(report,null,2));await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
