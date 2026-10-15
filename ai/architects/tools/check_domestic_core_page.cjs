/* Usage: PLAYWRIGHT_MODULE=... CHROMIUM_EXECUTABLE=... node this-file [URL]
 * Optional BROWSER_PROXY, IGNORE_HTTPS_ERRORS=1, SCREENSHOT_DIR.
 * Checks the fixed 2026-10-15 admission batch against the local catalog.
 */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'catalog.json'),'utf8'));
const batch=JSON.parse(fs.readFileSync(path.join(root,'research/batches/2026-10-15-domestic-core.json'),'utf8'));
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE,headless:true,
  ...(process.env.BROWSER_PROXY?{proxy:{server:process.env.BROWSER_PROXY}}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader']});
 const results=[];
 try {
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
  const page=await browser.newPage({viewport,ignoreHTTPSErrors:process.env.IGNORE_HTTPS_ERRORS==='1'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.argv[2]||'http://127.0.0.1:8765/ai/architects/',{waitUntil:'networkidle'});
  assert.equal(await page.locator('article.profile').count(),catalog.profiles.length);
  assert.equal(await page.locator('#architect-skill-table tbody tr').count(),catalog.profiles.length);
  for(const rec of batch.records){
   await page.locator('#matrix-name').fill(rec.name);
   const visible=page.locator('#architect-skill-table tbody tr:not([hidden])');
   assert.equal(await visible.count(),1,rec.name);
   assert.equal(await visible.locator('th a').getAttribute('href'),'#'+rec.id);
   await visible.locator('th a').click();
   const detail=page.locator('#'+rec.id+' > details.research-detail');
   await detail.locator(':scope > summary').click();assert(await detail.evaluate(e=>e.open));
   const profile=catalog.profiles.find(p=>p.id===rec.id);
   for(const fact of profile.sourceFacts)assert((await page.locator('#'+rec.id).innerText()).includes(fact.text));
  }
  await page.locator('#matrix-name').fill('no-such-architect-xyz');
  assert.equal(await page.locator('#architect-skill-table tbody tr:not([hidden])').count(),0);
  assert.equal(await page.locator('#matrix-empty').evaluate(e=>e.hidden),false);
  await page.locator('#matrix-name').fill('');await page.locator('#matrix-skill').selectOption('A1');
  assert.equal(await page.locator('#architect-skill-table tbody tr:not([hidden])').count(),catalog.profiles.filter(p=>p.challenge.skills.includes('A1')).length);
  await page.locator('#matrix-skill').selectOption('');
  assert((await page.locator('#matrix-count').innerText()).includes(`${catalog.profiles.length} / ${catalog.profiles.length}`));
  await page.locator('#jianlin-gao').evaluate(e=>window.scrollTo(0,window.scrollY+e.getBoundingClientRect().top-100));
  await page.waitForTimeout(350);
  assert.equal(await page.locator('.toc a[href="#jianlin-gao"]').getAttribute('aria-current'),'location');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  assert.deepEqual(errors,[]);
  if(process.env.SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.SCREENSHOT_DIR,`domestic-${viewport.width}.png`)});
  results.push({viewport,profiles:catalog.profiles.length,admissionsChecked:batch.records.length,search:true,details:true,sourceFacts:true,emptyState:true,skillFilter:true,sidebar:true,noPageErrors:true,noOverflow:true});
  await page.close();
 }
 console.log(JSON.stringify(results,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
