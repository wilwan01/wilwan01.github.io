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
     for(const value of ['115844','43777','130000','stock-based compensation'])assert(text.includes(value),value);
     const counts=await page.locator('#earnings-current-counts').innerText();
     assert(counts.includes(corpus.counts.quarterly_events+' quarterly slots'));
     assert(counts.includes(corpus.counts.questions+' selected Q&A probes'));
     assert.deepEqual(JSON.parse(await page.locator('#ledger-data').textContent()),corpus.ledger);
     assert.deepEqual(await page.locator('article.entry').evaluateAll(xs=>xs.map(x=>x.id).sort()),corpus.ledger.map(q=>q.id).sort());
     assert.equal(await page.locator('#result-count').innerText(),`${corpus.ledger.length} of ${corpus.ledger.length} probes`);
     for(const [field,table] of [['status','answer-status-counts'],['theme','theme-counts']]){
      const options=await page.locator('#'+field+' option').evaluateAll(xs=>xs.map(x=>x.value));
      for(const value of new Set(corpus.ledger.map(q=>q[field])))assert(options.includes(value),`Missing ${field} option ${value}`);
      const rows=await page.locator('#'+table+' tbody tr').evaluateAll(xs=>xs.map(x=>[x.cells[0].textContent,Number(x.cells[1].textContent)]));
      assert.equal(rows.reduce((sum,row)=>sum+row[1],0),corpus.ledger.length);
      for(const [value,n] of rows)assert.equal(n,corpus.ledger.filter(q=>q[field]===value).length,`${field}: ${value}`);
     }
     if(unread)assert(text.includes('main-call Q&A not reviewed'));
     else{
      const expectedIds=Array.from({length:8},(_,i)=>'QA'+(225+i));
      assert.deepEqual(event.question_ids,expectedIds);
      assert.equal(event.transcript_coverage.analyst_turns_reviewed,8);
      assert.equal(event.transcript_coverage.analyst_turns_total,8);
      assert.equal(event.transcript_coverage.independent_asks,15);
      assert.equal(event.transcript_coverage.audio_verified,false);
      assert.equal(event.full_filing_status,'pending_publication');
      const disclosure=corpus.financial_disclosures.find(d=>d.id===id);
      assert.equal(disclosure.full_filing_review.status,'pending_publication');
      assert.equal(disclosure.full_filing_review.review_completed,false);
      assert(!Number.isNaN(Date.parse(disclosure.full_filing_review.checked_at)));
      assert(text.includes('pending_publication'));
      const banner=await page.locator('#current-results-update').innerText();
      for(const value of ['8 of 8 analyst exchanges','15 substantive asks','Full Q3 10-Q pending'])assert(banner.includes(value),value);
      assert((await card.innerText()).includes('8 of 8 analyst exchanges'));
      assert((await card.innerText()).includes('15 substantive asks'));
      assert((await card.innerText()).includes('Not audio-verified'));
      for(const qaId of expectedIds){
       const q=corpus.ledger.find(q=>q.id===qaId);
       assert.equal(q.call_id,quarter);assert(q.source_type.includes('mirror'));
       await page.locator('#company').selectOption('Cisco');
       const qCard=page.locator('#'+qaId);assert.equal(await qCard.isVisible(),false);
       const link=card.locator('a[href="#'+qaId+'"]');assert.equal(await link.count(),1);await link.click();
       assert.equal(await qCard.isVisible(),true);assert.equal(await page.locator('#company').inputValue(),'');
       assert.equal(await qCard.locator('a').evaluateAll((xs,url)=>xs.filter(x=>x.href===url).length,q.url),1);
       assert.equal(await page.locator('#result-count').innerText(),`${corpus.ledger.length} of ${corpus.ledger.length} probes`);
      }
     }
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
