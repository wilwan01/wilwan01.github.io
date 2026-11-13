const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch(),base='http://127.0.0.1:8765',path='/ai/analysts/cases/nvda-jensen-departure-20261112.html';
 const report={sha:process.env.TESTED_SHA,rows:[]};
 try{
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
  const page=await browser.newPage({viewport}),errors=[],bad=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)bad.push(r.url())});
  await page.goto(base+path,{waitUntil:'networkidle'});assert.equal(await page.locator('.research-nav a').count(),15);assert.equal(await page.locator('main>section').count(),8);
  assert((await page.locator('#publication-note').innerText()).includes('不是当前行情'));
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);
  assert.deepEqual(await page.locator('a[href^="#"]').evaluateAll(as=>as.map(a=>a.getAttribute('href')).filter(h=>!document.getElementById(h.slice(1)))),[]);
  const detail=page.locator('#s8 details');await detail.locator('summary').click();assert.equal(await detail.evaluate(e=>e.open),true);
  await page.screenshot({path:`browser-results/case-${viewport.width}.png`});
  for(const entry of ['/ai/analysts/','/ai/analysts/thoughts.html','/ai/bridge/']){
   await page.goto(base+entry,{waitUntil:'networkidle'});await page.locator('#nvda-jensen-case a').click();await page.waitForURL('**'+path);
  }
  await page.goto(base+'/ai/search.html?q='+encodeURIComponent('黄仁勋'),{waitUntil:'networkidle'});
  const result=page.locator(`#results a[href="${path}"]`);await result.waitFor({state:'visible'});assert.equal(await result.count(),1);await result.click();await page.waitForURL('**'+path);
  assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);report.rows.push({viewport,caseSections:8,entryLinks:3,search:true,anchors:true,sourceExpansion:true,errors,bad});await page.close();
 }
 report.status='passed';
 }catch(e){report.status='failed';report.error=e.stack;throw e}finally{fs.writeFileSync('browser-results/report.json',JSON.stringify(report,null,2));await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
