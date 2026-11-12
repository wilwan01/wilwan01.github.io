const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
(async()=>{
 const root=process.cwd(),b=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium'}),ctx=await b.newContext();
 await ctx.route('https://earnings-test.invalid/**',async route=>{let p=decodeURIComponent(new URL(route.request().url()).pathname);if(p.endsWith('/'))p+='index.html';const file=path.resolve(root,'.'+p);if(!file.startsWith(root+'/'))return route.abort();try{await route.fulfill({status:200,body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.json':'application/json','.css':'text/css'})[path.extname(file)]||'application/octet-stream'});}catch{await route.fulfill({status:404,body:'not found'});}});
 const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('https://earnings-test.invalid/ai/earnings/');
 assert.equal(await page.locator('.entry').count(),218);assert.equal(await page.locator('#coverage tbody tr').count(),35);assert.equal(await page.locator('#result-count').textContent(),'218 of 218 probes');
 await page.locator('#search').fill('QA217');assert.equal(await page.locator('.entry:visible').count(),1);await page.locator('#clear').click();
 await page.locator('#company').selectOption('Arm');assert.equal(await page.locator('#QA218').isVisible(),false);
 await page.locator('#coverage a[href="#QA218"]').click();assert.equal(await page.locator('#company').inputValue(),'');assert.ok(await page.locator('#QA218').isVisible());
 await page.locator('#theme').selectOption('Supply');assert.ok(await page.locator('#QA218').isVisible());await page.locator('#clear').click();
 for(const width of [1440,390]){await page.setViewportSize({width,height:900});assert.ok(await page.locator('#latest-refresh').isVisible());await page.locator('#QA217 details summary').click();assert.ok(await page.locator('#QA217 details a').isVisible());await page.locator('#QA217 details summary').click();}
 assert.deepEqual(errors,[]);await b.close();console.log(JSON.stringify({status:'passed',browser:'Chromium headless isolated local routing',entries:218,company_rows:35,viewports:[1440,390],search_filter:true,coverage_deep_link:true,attribution_expand:true,script_errors:errors,scope:'Earnings page only; no live deployment verification'},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
