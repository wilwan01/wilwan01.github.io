const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE,headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader']});
const results=[];
for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
const page=await browser.newPage({viewport}); const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto(process.argv[2]||'http://127.0.0.1:8765/ai/architects/',{waitUntil:'networkidle'});
assert.equal(await page.locator('article.profile').count(),390);
assert.equal(await page.locator('#architect-skill-table tbody tr').count(),390);
assert.match(await page.locator('#matrix-count').innerText(),/390 \/ 390/);
await page.locator('#matrix-name').fill('谢炎');
assert.equal(await page.locator('#architect-skill-table tbody tr:not([hidden])').count(),1);
await page.locator('#matrix-name').fill('zzzz-no-such-person');
assert.equal(await page.locator('#architect-skill-table tbody tr:not([hidden])').count(),0);
assert.equal(await page.locator('#matrix-empty').evaluate(e=>e.hidden),false);
await page.locator('#matrix-name').fill('');
const value=await page.locator('#matrix-skill option').nth(1).getAttribute('value');await page.locator('#matrix-skill').selectOption(value);
assert(await page.locator('#architect-skill-table tbody tr:not([hidden])').count()>0);
await page.locator('#matrix-skill').selectOption('');
await page.locator('#matrix-name').fill('谢炎');
assert.equal(await page.locator('#architect-skill-table tbody tr:not([hidden])').count(),1);
await page.locator('#architect-skill-table tbody tr:not([hidden]) a[href="#yan-xie"]').click();
await page.locator('#yan-xie > details.research-detail > summary').click();
assert.equal(await page.locator('#yan-xie > details.research-detail').evaluate(e=>e.open),true);
assert(await page.locator('#yan-xie').innerText().then(t=>t.includes('WO2016141807A1')));
await page.locator('#yan-xie').evaluate(e=>window.scrollTo(0,window.scrollY+e.getBoundingClientRect().top-100));
await page.waitForTimeout(350);
assert.equal(await page.locator('.toc a[href="#yan-xie"]').getAttribute('aria-current'),'location');
if(viewport.width>681)assert(await page.locator('.toc a[href="#yan-xie"]').evaluate(e=>{const a=e.getBoundingClientRect(),b=e.closest('.toc').getBoundingClientRect();return a.top>=b.top&&a.bottom<=b.bottom}));
const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);assert.equal(overflow,false);
assert.deepEqual(errors,[]);
if(process.env.SCREENSHOT_DIR) await page.screenshot({path:`${process.env.SCREENSHOT_DIR}/${viewport.width}.png`});
results.push({viewport,profiles:390,matrixRows:390,searchChinese:true,emptyState:true,skillFilter:true,details:true,sidebarSync:true,noPageErrors:true,noHorizontalOverflow:true});await page.close();}
console.log(JSON.stringify(results,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
