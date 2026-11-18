// Browser regression for recorded releases; source and call verification are separate.
const {chromium}=require('playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch();
 const base=process.env.TEST_BASE_URL||'http://127.0.0.1:8765';
 const corpus=JSON.parse(fs.readFileSync('ai/analysts/corpus.json','utf8'));
 const report={sha:process.env.TESTED_SHA,observedAt:new Date().toISOString(),rows:[]};
 fs.mkdirSync('browser-results',{recursive:true});
 try{
  for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
   const page=await browser.newPage({viewport});const errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   for(const [company,quarter,id] of [['Cisco','CSCO_2027Q1','CSCO_2027Q1_results_20261112'],['Applied Materials','AMAT_2026Q4','AMAT_2026Q4_results_20261112'],['NVIDIA','NVDA_2027Q3','NVDA_2027Q3_results_20261117']]){
    await page.goto(base+'/ai/earnings/#company-evidence-'+id,{waitUntil:'networkidle'});
    assert.equal(await page.locator('#coverage tbody tr').count(),corpus.counts.companies);
    const card=page.locator('#coverage-'+quarter);
    const event=corpus.event_increments.find(e=>e.call_id===quarter);assert(event);
    const unread=event.call_verification_status==='main_call_body_not_reviewed';
    assert.equal(await card.count(),1);assert.equal(await card.getAttribute('data-review'),unread?'results_only':'selected_qa');
    if(unread)assert((await card.innerText()).includes('Main-call body not reviewed'));
    const detail=page.locator('#company-evidence-'+id);
    await detail.locator(':scope > summary').click();
    assert.equal(await detail.evaluate(x=>x.open),true);
    assert((await detail.innerText()).includes('reported actuals'));
    if(company==='NVIDIA'){
     const text=await detail.innerText();
     for(const value of ['115844','43777','130000','stock-based compensation','main-call Q&A not reviewed'])assert(text.includes(value),value);
     const counts=await page.locator('#earnings-current-counts').innerText();
     assert(counts.includes(corpus.counts.quarterly_events+' quarterly slots'));
     assert(counts.includes(corpus.counts.questions+' selected Q&A probes'));
    }
    assert(await detail.locator('a[href^="https://"]').count()>0);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);
    await page.goto(base+'/ai/search.html',{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.querySelector('#count').textContent.includes('entries indexed'));
    await page.locator('#q').fill(company);
    const result=page.locator('#results a[href="/ai/earnings/#company-evidence-'+id+'"]');
    assert.equal(await result.count(),1);await result.click();
    await page.locator('#company-evidence-'+id).waitFor({state:'visible'});
   }
   assert.deepEqual(errors,[]);
   report.rows.push({viewport,releaseRows:3,searchDeepLinks:3,expansion:true,noHorizontalOverflow:true,errors});
   await page.screenshot({path:'browser-results/earnings-results-'+viewport.width+'.png'});await page.close();
  }
  report.status='passed';
 }catch(e){report.status='failed';report.error=e.stack;throw e}
 finally{fs.writeFileSync('browser-results/earnings-results-report.json',JSON.stringify(report,null,2)+'\n');await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
