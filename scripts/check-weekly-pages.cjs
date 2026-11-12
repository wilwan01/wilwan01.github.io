/* Usage: node scripts/check-weekly-pages.cjs [base URL] [output JSON path] */
const {chromium}=require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const paths=['index.html','earnings/','analysts/','hot-chips/','architects/','notes/','bridge/','policy/','standards/','customers/','benchmarks/','energy/','calendar/','method/','search.html'];
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const base=process.argv[2]||'http://127.0.0.1:8765';const rows=[];
 try{
  for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
   const page=await browser.newPage({viewport});
   for(const path of paths){
    const errors=[],bad=[];const onError=e=>errors.push(e.message);const onResponse=r=>{if(r.url().startsWith(base)&&r.status()>=400)bad.push({url:r.url(),status:r.status()})};
    page.on('pageerror',onError);page.on('response',onResponse);
    const r=await page.goto(`${base}/ai/${path}`,{waitUntil:'networkidle'});
    assert.equal(r.status(),200,path);assert(await page.locator('h1').count()>0,path);
    assert.equal(await page.locator('nav.research-nav a').count(),15,path);
    const checks={};
    if(path==='architects/'){
     const d=await page.evaluate(()=>fetch('/ai/architects/catalog.json').then(r=>r.json()));
     checks.profiles=await page.locator('article.profile').count();assert.equal(checks.profiles,d.profiles.length);
     await page.locator('#matrix-name').fill('yuanbo');assert.equal(await page.locator('#architect-skill-table tbody tr:not([hidden])').count(),1);checks.filter=true;
    }
    if(path==='search.html'){
     const d=await page.evaluate(()=>fetch('/ai/search-index.json',{cache:'no-cache'}).then(r=>r.json()));
     assert.equal(d.count,d.entries.length);assert(!d.entries.some(e=>e.u.includes('/research/')||e.u.includes('#candidates')));
     await page.locator('#q').fill('Yuanbo');assert(await page.locator('#results a[href*="yuanbo-wen"]').count()>0);
     await page.locator('#chips [data-s="architects"]').click();assert(await page.locator('#results a[href*="yuanbo-wen"]').count()>0);
     await page.locator('#q').fill('zzznomatch20261112');assert((await page.locator('#count').innerText()).startsWith('0 '));checks.search=true;checks.indexEntries=d.count;
    }
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);
    rows.push({path,viewport,status:r.status(),jsErrors:errors,failedResources:bad,horizontalOverflow:overflow,checks});
    page.off('pageerror',onError);page.off('response',onResponse);
   }
   await page.close();
  }
 }finally{await browser.close()}
 const report={observedAt:new Date().toISOString(),base,scope:'15 entry pages at two viewports; search interaction and architecture count/filter. Other interactions separately validated.',rows};
 if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({pages:rows.length,errors:rows.filter(r=>r.jsErrors.length||r.failedResources.length),overflow:rows.filter(r=>r.horizontalOverflow).map(r=>({path:r.path,width:r.viewport.width}))}));
 assert(!rows.some(r=>r.jsErrors.length||r.failedResources.length),'page errors or failed resources');
})().catch(e=>{console.error(e);process.exit(1)});
