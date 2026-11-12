const {chromium}=require('playwright');
const fs=require('node:fs'), assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch(), base='http://127.0.0.1:8765';
 const report={sha:process.env.TESTED_SHA,observedAt:new Date().toISOString(),rows:[]};
 try {
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
  const page=await browser.newPage({viewport}), errors=[],failed=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)failed.push(r.url())});
  await page.goto(base+'/ai/customers/',{waitUntil:'networkidle'});
  assert.equal(await page.locator('#list article').count(),19);
  for(const id of ['C14','C15','C16','C17','C18','C19'])assert.equal(await page.locator('#'+id).count(),1);
  assert((await page.locator('#C19').innerText()).includes('Crusoe'));
  await page.locator('#langbar [data-l="en"]').click();assert.equal(await page.locator('body').getAttribute('data-lang'),'en');
  await page.locator('#langbar [data-l="zh"]').click();assert.equal(await page.locator('body').getAttribute('data-lang'),'zh');
  await page.locator('#langbar [data-l="both"]').click();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);
  await page.screenshot({path:`browser-results/customers-${viewport.width}.png`});
  await page.goto(base+'/ai/earnings/',{waitUntil:'networkidle'});
  assert.equal(await page.locator('#coverage tbody tr').count(),35);
  const archive=page.locator('#coverage-evidence-archive');assert.equal(await archive.evaluate(e=>e.open),false);
  const evidence=page.locator('details.coverage-evidence').first();await evidence.locator(':scope > summary').click();assert.equal(await evidence.evaluate(e=>e.open),true);
  const disclosure=evidence.locator('details.coverage-disclosure').first();await disclosure.locator(':scope > summary').click();assert.equal(await disclosure.evaluate(e=>e.open),true);assert(await disclosure.locator('a[href^="https://"]').count()>0);
  await page.evaluate(()=>location.hash='latest-refresh');await page.locator('#latest-refresh').waitFor({state:'visible'});assert.equal(await archive.evaluate(e=>e.open),true);
  await page.screenshot({path:`browser-results/earnings-${viewport.width}.png`});
  for(const [name,id] of [['Nebius','C14'],['Lambda','C15'],['Fluidstack','C16'],['GMI','C17'],['IREN','C18'],['Crusoe','C19']]){
   await page.goto(base+'/ai/search.html',{waitUntil:'networkidle'});await page.waitForFunction(()=>document.querySelector('#count').textContent.includes('entries indexed'));
   await page.locator('#q').fill(name);const link=page.locator(`#results a[href="/ai/customers/#${id}"]`);assert.equal(await link.count(),1);await link.click();await page.locator('#'+id).waitFor({state:'visible'});
  }
  assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);report.rows.push({viewport,customers:19,companies:35,evidenceExpansion:true,legacyAnchor:true,search:true,errors,failed});await page.close();
 }
 report.status='passed';
 }catch(e){report.status='failed';report.error=e.stack;throw e}
 finally{fs.writeFileSync('browser-results/report.json',JSON.stringify(report,null,2)+'\n');await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
