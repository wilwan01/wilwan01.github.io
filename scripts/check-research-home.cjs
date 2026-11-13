const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch(),base='http://127.0.0.1:8765',report={sha:process.env.TESTED_SHA,rows:[]};
try{
for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
 const page=await browser.newPage({viewport}),errors=[],failed=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)failed.push(r.url())});
 for(const [file,lang] of [['index.html','zh'],['index-en.html','en']]){
  await page.goto(base+'/ai/'+file,{waitUntil:'networkidle'});
  assert.equal(await page.locator('h1').count(),1);assert.equal(await page.locator('#company-reports section.card').count(),15);assert.equal(await page.locator('.report-freshness').count(),15);assert.equal(await page.locator('.update-card').count(),4);
  assert.equal(await page.locator('.research-nav a').first().getAttribute('href'),'/ai/'+file);
  assert.equal(await page.locator('.report-freshness time[datetime="2026-09-27"]').count(),1);assert.equal(await page.locator('.report-freshness time[datetime="2026-09-28"]').count(),14);
  await page.locator('.collection-download>summary').click();assert.equal(await page.locator('.collection-download').evaluate(e=>e.open),true);
  await page.locator('.collection-download>summary').click();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);
  await page.screenshot({path:`browser-results/home-${lang}-${viewport.width}.png`,fullPage:true});
  await page.locator('#home-query').fill('Crusoe');await page.locator('.home-search button').click();
  await page.waitForURL('**/search.html?q=Crusoe');await page.locator('#results a[href="/ai/customers/#C19"]').waitFor({state:'visible'});
  await page.goto(base+'/ai/'+file+'#company-reports',{waitUntil:'networkidle'});
  await page.locator('#company-reports .primary').first().click();await page.waitForURL('**/amd-'+lang+'.html');
  assert.equal(await page.locator('html').getAttribute('lang'),lang==='zh'?'zh-CN':'en');
  report.rows.push({viewport,lang,search:true,reportNavigation:true,counts:true,noOverflow:true});
 }
 assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);await page.close();
}
report.status='passed';
}catch(e){report.status='failed';report.error=e.stack;throw e}finally{fs.writeFileSync('browser-results/report.json',JSON.stringify(report,null,2));await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
