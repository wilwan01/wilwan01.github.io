// Static company-table integration. Run after each earnings refresh:
// node ai/earnings/tools/sync-coverage.mjs [--check]
// Add an evidence-backed progression summary before introducing a new reviewed company.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const dir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const corpus = JSON.parse(fs.readFileSync(path.join(dir, '../analysts/corpus.json'), 'utf8'));
const notes = JSON.parse(fs.readFileSync(path.join(dir, 'coverage-progression.json'), 'utf8'));
const filename = path.join(dir, 'index.html');
const original = fs.readFileSync(filename, 'utf8');
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const link = (url, label) => `<a href="${esc(url)}"${url.startsWith('#') ? '' : ' rel="noopener" target="_blank"'}>${esc(label)}</a>`;
const qa = new Map(corpus.ledger.map(q => [q.id, q]));
const disclosures = new Map(corpus.financial_disclosures.map(d => [d.id, d]));
assert.equal(notes.evidence_cutoff_at, corpus.cutoff_at, 'Review progression summaries at the new evidence cutoff');

// Micron predates event_increments; preserve its original stable call IDs.
const micron = ['MU_2026Q4', 'MU_2026Q4_post'].map(call_id => {
  const questions = corpus.ledger.filter(q => q.call_id === call_id);
  assert.ok(questions.length);
  return {quarter_id:'MU_2026Q4', call_id, company:'Micron', period:'FY2026 Q4', date:'2026-09-30',
    call_type:call_id.endsWith('_post') ? 'post_earnings' : 'primary', question_ids:questions.map(q => q.id)};
});
const events = [...micron, ...corpus.event_increments];
const unique = new Set(events.map(e => e.call_id || e.quarter_id));
assert.equal(unique.size, events.length, 'Duplicate incremental event');
const quarters = new Set(events.map(e => e.quarter_id));
const postCalls = events.filter(e => e.call_type === 'post_earnings');
const gaps = events.filter(e => e.call_verification_status === 'main_call_body_not_reviewed');
assert.equal(140 + quarters.size, corpus.counts.quarterly_events);
assert.equal(postCalls.length, corpus.counts.post_earnings_calls);

// Preserve the dated snapshots verbatim, but keep them collapsed as an audit archive.
// Refresh producers may still add a dated section; every coverage sync folds it in.
let html = original.replace(/<!-- coverage-archive:start --><details id="coverage-evidence-archive"><summary>[\s\S]*?<\/summary>([\s\S]*?)<\/details><!-- coverage-archive:end -->/, '$1');
const archive = [];
html = html.replace(/<section id="(?:latest-refresh|refresh-[^"]+)">[\s\S]*?<\/section>/g, snapshot => { archive.push(snapshot); return ''; });
const valueHtml = value => {
  if (Array.isArray(value)) return '<ul>' + value.map(v => '<li>' + valueHtml(v) + '</li>').join('') + '</ul>';
  if (value && typeof value === 'object') return '<dl>' + Object.entries(value).map(([k,v]) => '<dt>' + esc(k.replaceAll('_',' ')) + '</dt><dd>' + valueHtml(v) + '</dd>').join('') + '</dl>';
  return esc(value ?? 'Not recorded');
};
const financialCards = company => {
  const records = corpus.financial_disclosures.filter(d => d.company === company).sort((a,b) => b.release_date.localeCompare(a.release_date));
  if (!records.length) return '';
  return '<!-- coverage-evidence:start --><details class="coverage-evidence"><summary>Financial evidence · ' + records.length + ' disclosures · latest ' + esc(records[0].release_date) + '</summary><p>Recorded disclosures, not additional quarters or calls. Historical preliminary figures and supersession links are retained. Management guidance is not consensus.</p>' + records.map(d => {
    const fields = Object.entries(d).filter(([k]) => !['id','company','ticker','period','release_date','sources','source_keys'].includes(k));
    return '<details class="coverage-disclosure" id="company-evidence-' + esc(d.id) + '"><summary>' + esc(d.period + ' · ' + d.release_date + ' · ' + d.event_type.replaceAll('_',' ')) + '</summary>' + valueHtml(Object.fromEntries(fields)) + '<h4>Sources and reading locations</h4><ul>' + d.sources.map(source => '<li>' + link(source.url, source.title || source.id || source.key) + valueHtml(Object.fromEntries(Object.entries(source).filter(([k]) => !['url','title','source_ref'].includes(k)))) + '</li>').join('') + '</ul></details>';
  }).join('') + '</details><!-- coverage-evidence:end -->';
};
const sectionStart = html.indexOf('<section id="coverage">');
const sectionEnd = html.indexOf('</section>', sectionStart) + '</section>'.length;
assert.ok(sectionStart > 0 && sectionEnd > sectionStart);
let section = html.slice(sectionStart, sectionEnd);
// Remove only our generated segments, so reruns preserve all historical content.
section = section.replace(/<!-- coverage-increments:start -->[\s\S]*?<!-- coverage-increments:end -->/g, '');
section = section.replace(/<!-- coverage-progression:start -->[\s\S]*?<!-- coverage-progression:end -->/g, '');
section = section.replace(/<!-- coverage-evidence:start -->[\s\S]*?<!-- coverage-evidence:end -->/g, '');
section = section.replace(/<!-- coverage-summary:start -->[\s\S]*?<!-- coverage-summary:end -->/g, '');
section = section.replace('<div><a href="#MU_2026Q4">FY2026 Q4 · NEW</a><small>September 30, 2026</small></div>', '');

const intro = '<p>Quarters retain the source’s fiscal labels; they are not synchronized calendar periods. The original four-quarter history is preserved, with later results and separately labeled post-earnings calls added to each company. Transcript links identify official text versus public mirrors; results-only links are releases, not reviewed calls. Dates are event dates for reviewed calls and release dates for results-only entries. Schneider’s Q1 and Q3 slots are revenue updates; its other slots are half-year and full-year results. Progression updates are editorial inferences from the linked selected exchanges, not analyst quotations or certified recurring personal patterns.</p>';
section = section.replace(/(<h2>Company coverage and four-quarter progression<\/h2>)<p>[\s\S]*?<\/p>/, '$1' + intro);
const summary = `<!-- coverage-summary:start --><p class="note" id="coverage-status">Evidence cutoff: <strong>${esc(corpus.cutoff_at)}</strong> (Europe/London). <strong>${corpus.counts.companies} companies · ${corpus.counts.quarterly_events} quarterly slots · ${postCalls.length} separate post-earnings calls</strong>. The ${quarters.size} added quarters include ${gaps.length} results-only entries whose main-call bodies remain unreviewed. The current ledger contains ${corpus.counts.questions} selected Q&amp;A records with stable IDs; each call retains its own review scope. Non-quarter preliminary notices, monthly revenue and long-term targets are included in each company’s expandable financial evidence and do not add quarterly slots.</p><!-- coverage-summary:end -->`;
section = section.replace('<div class="table-wrap">', summary + '<div class="table-wrap">');
section = section.replace('Historical four calls + incremental additions', 'Original four-quarter history + later results / calls');

const rendered = new Set();
let rows = 0;
section = section.replace(/<tr><td><strong>([^<]+)<\/strong>[\s\S]*?<\/tr>/g, row => {
  rows++;
  const company = row.match(/<strong>([^<]+)<\/strong>/)[1];
  row = row.replace('</td></tr>', financialCards(company) + '</td></tr>');
  const additions = events.filter(e => e.company === company);
  if (!additions.length) return row;
  const cards = additions.map(e => {
    rendered.add(e.call_id || e.quarter_id);
    const questions = e.question_ids.map(id => {assert.ok(qa.has(id), id); return qa.get(id);});
    assert.ok(questions.every(q => q.company === company && q.call_id === e.call_id));
    const disclosure = e.source_disclosure_id ? disclosures.get(e.source_disclosure_id) : null;
    if (e.source_disclosure_id) assert.ok(disclosure, e.source_disclosure_id);
    const missing = e.call_verification_status === 'main_call_body_not_reviewed';
    const post = e.call_type === 'post_earnings';
    const id = e.call_id || e.quarter_id;
    const title = `${e.period}${post ? ' · separate post-call' : missing ? ' · results only' : ' · added'}`;
    let sources = '';
    if (questions.length) {
      const first = questions[0];
      const official = /official|issuer_hosted/.test(first.source_type || '');
      sources += link(first.url, official ? 'Official transcript' : 'Public transcript mirror');
      const scope = e.transcript_coverage;
      if (scope) {
        assert.ok(Number.isInteger(scope.analyst_turns_reviewed) && Number.isInteger(scope.analyst_turns_total));
        assert.ok(scope.analyst_turns_reviewed >= 0 && scope.analyst_turns_reviewed <= scope.analyst_turns_total);
        assert.ok(Number.isInteger(scope.independent_asks) && scope.independent_asks >= scope.analyst_turns_reviewed);
        const medium = official ? 'transcript' : 'mirrored transcript';
        sources += `<small>${scope.analyst_turns_reviewed} of ${scope.analyst_turns_total} analyst exchanges reviewed in the ${medium}; ${scope.independent_asks} substantive asks. ${scope.audio_verified === true ? 'Audio verification recorded.' : 'Not audio-verified.'}</small>`;
      } else sources += `<small>Selected passages reviewed; not audio-verified.</small>`;
    }
    if (disclosure) sources += link(disclosure.sources[0].url, /syndicated/.test(disclosure.sources[0].evidence_kind) ? 'Issuer-distributed results' : 'Official results');
    if (!disclosure && !post && company === 'Micron') sources += link('#MU_2026Q4', 'Results and source notes');
    if (missing) sources += '<small class="coverage-gap">Main-call body not reviewed; no new selected Q&amp;A.</small>';
    if (questions.length) sources += `<span class="coverage-qa">${questions.map(q => link('#' + q.id, q.id)).join(' · ')}</span>`;
    if (e.data_quality_status) sources += `<small class="coverage-gap">${esc(e.data_quality_status)}</small>`;
    return `<div class="coverage-added" id="coverage-${esc(id)}" data-quarter-id="${esc(e.quarter_id)}" data-event-kind="${post ? 'post_earnings' : 'quarter'}" data-review="${missing ? 'results_only' : 'selected_qa'}"><strong>${esc(title)}</strong><small>${esc(e.date)} · ${missing ? 'release date' : 'call date'}</small>${sources}</div>`;
  }).join('');
  row = row.replace('</div></td><td class="company-note">', `<!-- coverage-increments:start -->${cards}<!-- coverage-increments:end --></div></td><td class="company-note">`);
  const reviewed = additions.filter(e => e.question_ids.length);
  let progression;
  if (reviewed.length) {
    assert.ok(notes.updates[company], `Missing editorial summary for ${company}`);
    progression = `<p><strong>Latest editorial progression</strong><br/>${esc(notes.updates[company])}</p><small>Evidence: ${reviewed.flatMap(e => e.question_ids).map(id => link('#' + id, id)).join(' · ')}</small>`;
  } else {
    progression = `<p class="coverage-gap"><strong>${esc(additions.at(-1).period)} results added (${esc(additions.at(-1).date)}).</strong> Main-call body not reviewed. The earlier question-level synthesis is retained; no new Q&amp;A progression is inferred from the release alone.</p>`;
  }
  return row.replace('</td></tr>', `<!-- coverage-progression:start -->${progression}<!-- coverage-progression:end --></td></tr>`);
});
assert.equal(rows, corpus.counts.companies);
assert.equal(rendered.size, events.length, 'Every incremental event must appear in exactly one company row');
html = html.slice(0, sectionStart) + section + (archive.length ? '<!-- coverage-archive:start --><details id="coverage-evidence-archive"><summary>Historical evidence snapshots · original cutoffs, checks and gaps</summary>' + archive.join('') + '</details><!-- coverage-archive:end -->' : '') + html.slice(sectionEnd);
// Normalize the whitespace left by migrating sections, without touching their contents.
html = html.replace(/\n{3,}/g, '\n\n');
// Keep the current overview separate from dated snapshot totals.
const overview = `<p class="metricline" id="earnings-current-counts">${corpus.counts.companies} companies · ${corpus.counts.quarterly_events} quarterly slots + ${postCalls.length} separate post-earnings calls · ${corpus.counts.questions} selected Q&amp;A probes · ${corpus.financial_disclosures.length} financial disclosures</p>`;
const overviewPattern = /<p class="metricline"(?: id="earnings-current-counts")?>\d+ companies · \d+ quarterly (?:events|slots) \+ \d+ (?:standalone|separate) post-earnings calls · \d+ selected Q&amp;A probes · \d+ (?:supplemental non-quarterly|financial) disclosures<\/p>/;
assert.ok(overviewPattern.test(html), 'Missing current earnings overview');
html = html.replace(overviewPattern, overview);
// Current statistics derive from the ledger; dated archive sections remain verbatim.
assert.equal(corpus.ledger.length, corpus.counts.questions, 'Question count must match the ledger');
const frequencies = field => corpus.ledger.reduce((out, q) => out.set(q[field], (out.get(q[field]) || 0) + 1), new Map());
const statusCounts = frequencies('status'), themeCounts = frequencies('theme');
const statusOrder = [...new Set(['answered', 'partially answered', 'deferred', 'deflected', 'unanswered', ...statusCounts.keys()])];
const countTable = (id, label, rows) => `<table id="${id}"><thead><tr><th>${label}</th><th>Probes / ${corpus.ledger.length}</th></tr></thead><tbody>${rows.map(([name, count]) => `<tr><td>${esc(name)}</td><td>${count}</td></tr>`).join('')}</tbody></table>`;
const methodPattern = /<section id="method">[\s\S]*?<\/section>/;
assert.ok(methodPattern.test(html), 'Missing current method section');
html = html.replace(methodPattern, method => {
  method = method.replace('current totals are 160 quarters and two standalone post-calls.', 'totals at the 4 November cutoff were 160 quarters and two standalone post-calls.');
  method = method.replace(/The \d+ probes are grouped question-level records/, `The ${corpus.ledger.length} probes are grouped question-level records`);
  method = method.replace(/they are not \d+ exhaustively normalized atomic asks/, `they are not ${corpus.ledger.length} exhaustively normalized atomic asks`);
  const statusPattern = /(<h3>Answer status in this selected ledger<\/h3>)<table\b[^>]*>[\s\S]*?<\/table>/;
  const themePattern = /(<summary>Theme counts in the selected ledger<\/summary>)<table\b[^>]*>[\s\S]*?<\/table>/;
  assert.ok(statusPattern.test(method) && themePattern.test(method), 'Missing current count tables');
  method = method.replace(statusPattern, '$1' + countTable('answer-status-counts', 'Status', statusOrder.map(name => [name, statusCounts.get(name) || 0])));
  method = method.replace(themePattern, '$1' + countTable('theme-counts', 'Primary theme', [...themeCounts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))));
  return method;
});
html = html.replace(/(<section id="ledger"><h2>Auditable question ledger<\/h2><p>[\s\S]*?Export includes all )\d+( records,)/, `$1${corpus.ledger.length}$2`);
html = html.replace(/(<p\b[^>]*\bid="result-count"[^>]*>)[\s\S]*?(<\/p>)/, `$1${corpus.ledger.length} of ${corpus.ledger.length} probes$2`);
for (const [field, values] of [['theme', [...themeCounts.keys()].sort()], ['status', statusOrder.filter(name => statusCounts.has(name))]]) {
  const pattern = new RegExp(`<select id="${field}">[\\s\\S]*?<\\/select>`);
  assert.ok(pattern.test(html), `Missing ${field} filter`);
  html = html.replace(pattern, `<select id="${field}"><option value="">All ${field === 'status' ? 'statuses' : 'themes'}</option>${values.map(value => `<option>${esc(value)}</option>`).join('')}</select>`);
}
html = html.replace('The historical four-quarter coverage table is retained; new events are listed in the incremental section.', 'The original four-quarter history is retained in Company coverage, with later results, reviewed calls, separate post-calls and editorial progression integrated into each affected company row. Collapsed historical snapshots retain the underlying refresh history.');
// The original Micron append omitted article IDs; add the existing stable QA IDs for deep links.
html = html.replace(/<article\b([^>]*)>([\s\S]*?)<\/article>/g, (whole, attrs, body) => {
  if (!attrs.includes('class="entry"') || /\bid=/.test(attrs)) return whole;
  const id = body.match(/<h3>(QA\d+) ·/);
  return id ? `<article${attrs} id="${id[1]}">${body}</article>` : whole;
});
const css = '\n/* Integrated company progression */\n.coverage-added{border-top:2px solid var(--accent);padding-top:8px}.coverage-added small{display:block}.coverage-added>a{font-size:13px}.coverage-qa{font-size:12px}.coverage-qa a{display:inline}.coverage-gap{color:var(--muted);font-style:italic}.company-note p{margin:14px 0 8px}.company-note small a{white-space:nowrap}\n';
if (!html.includes('/* Integrated company progression */')) html = html.replace('</style>', css + '</style>');
// A coverage deep link must reveal its QA even after the reader filters another company.
const reveal = `\n// Coverage deep links reveal a filtered-out selected exchange.\ndocument.querySelectorAll('#coverage a[href^="#QA"]').forEach(a=>a.addEventListener('click',()=>{const target=document.getElementById(a.getAttribute('href').slice(1));if(target&&target.hidden){ids.forEach(k=>document.getElementById(k).value='');filter();}}));\n`;
if (!html.includes('// Coverage deep links reveal')) html = html.replace("function download(content,type,name)", reveal + "function download(content,type,name)");

const evidenceCss = '\n/* Company financial evidence */\n.coverage-evidence{margin-top:16px;border-top:1px solid var(--accent);padding-top:8px}.coverage-evidence summary,#coverage-evidence-archive>summary{cursor:pointer;font-weight:600}.coverage-disclosure{margin:12px 0}.coverage-disclosure dl{margin:8px 0}.coverage-disclosure dt{font-weight:600}.coverage-disclosure dd{margin:0 0 8px 12px;overflow-wrap:anywhere}.coverage-disclosure ul{padding-left:18px}#coverage-evidence-archive{margin:24px 0}\n';
if (!html.includes('/* Company financial evidence */')) html = html.replace('</style>', evidenceCss + '</style>');
const archiveReveal = `\n// Reveal preserved anchors inside collapsed evidence and historical snapshots.\nfunction revealEvidenceAnchor(){const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(!target)return;let parent=target.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}target.scrollIntoView();}\nwindow.addEventListener('hashchange',revealEvidenceAnchor);if(location.hash)revealEvidenceAnchor();\n`;
if (!html.includes('// Reveal preserved anchors')) html = html.replace('function download(content,type,name)', archiveReveal + 'function download(content,type,name)');
const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map(m => m[1]);
assert.equal(ids.length, new Set(ids).size, 'Duplicate HTML IDs');
for (const e of events) for (const id of e.question_ids) assert.ok(ids.includes(id), `Missing QA anchor ${id}`);
assert.equal([...html.matchAll(/<article\b[^>]*class="entry"/g)].length, corpus.counts.questions);
if (process.argv.includes('--check')) assert.equal(html, original, 'Coverage table is stale; run sync-coverage.mjs');
else fs.writeFileSync(filename, html);
console.log(JSON.stringify({companies:rows,quarterly_slots:140+quarters.size,incremental_quarters:quarters.size,separate_post_calls:postCalls.length,unreviewed_main_call_bodies:gaps.length,selected_qa:corpus.counts.questions,evidence_cutoff:corpus.cutoff_at,mode:process.argv.includes('--check')?'check':'write'},null,2));
