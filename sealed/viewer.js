'use strict';
let manifest,current,active='attempts',pageIndex=0;const pageSize=35;
const $=s=>document.querySelector(s);
function node(tag,text,cls){const n=document.createElement(tag);if(text!=null)n.textContent=text;if(cls)n.className=cls;return n}
function clear(id){$(id).replaceChildren()}
function printable(x){return typeof x==='string'?x:JSON.stringify(x,null,2)}
function option(value,label){const n=node('option',label);n.value=value;return n}
function details(title,content){const d=node('details');d.append(node('summary',title),node('pre',printable(content)));return d}
function tab(name){active=name;document.querySelectorAll('.pane').forEach(p=>p.hidden=p.id!==name);document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));if(name==='raw')renderMessages();}
async function loadCase(id){
 clear('#summary');$('#summary').append(node('p','Loading run…'));current=await(await fetch('data/'+id+'.json')).json();
 const s=current.summary;clear('#summary');$('#summary').append(node('h2',`Level ${s.level} · ${s.id}`));
 $('#summary').append(node('div',`Initial attempts recorded: ${s.recorded_attempts}/8 · Sealed cap: ${s.sealed_cap} · Engine threshold: ${s.engine_minimum_cap} · Reported initial bound: ${s.reported_initial_bound}`,'facts'));
 if(s.bound_note)$('#summary').append(node('p',s.bound_note,'muted'));
 if(s.pending_note)$('#summary').append(node('p','Continuation pending: the collaborator will upload attempts 4–8 and the final interview.','pending'));
 const a=node('a','Download the complete available run archive');a.href=s.download;a.download='';$('#summary').append(a);
 const missed=s.missing_source_version_count;$('#summary').append(node('p',`Raw user/assistant messages: ${s.raw_messages}. Older source versions without a recovered full snapshot: ${missed}. Original tool history is retained.`,'muted'));
 document.querySelectorAll('#runs button').forEach(b=>b.classList.toggle('active',b.dataset.id===id));
 clear('#attempt');for(const r of current.attempts)$('#attempt').append(option(r.attempt,'Attempt '+r.attempt));
 clear('#session');for(const source of [...new Set(current.events.map(e=>e.source))])$('#session').append(option(source,source));
 clear('#source');for(const [i,f] of current.source_files.entries())$('#source').append(option(i,`[${f.phase}] ${f.path}`));
 $('#search').value='';pageIndex=0;renderAttempt();renderFinal();clear('#repairText');const repair=current.selected_external_repair;$('#repairText').append(node('p',repair?repair.scope:'No selected external-feedback repair is linked to this run.'));if(repair)$('#repairText').append(node('pre',repair.answers));await renderSource();tab(active);location.hash=id;
}
function renderAttempt(){
 clear('#answers');const row=current.attempts.find(r=>String(r.attempt)===$('#attempt').value);if(!row)return;
 $('#answers').append(node('h3','Attempt '+row.attempt));
 if(row.answers.length){for(const text of [...new Set(row.answers)])$('#answers').append(node('pre',text));}
 else $('#answers').append(node('p','This partial run has a console audit and raw session, but no structured round-answer record. Use Full session or the archive.'));
 if(row.verdict)$('#answers').append(details('Recorded verdict',row.verdict));
 if(row.gate)$('#answers').append(details('Historical gate record',row.gate));
 if(row.model_manifest)$('#answers').append(details(`Model / Lean inventory: ${row.recovered_files} of ${row.model_files} files recovered by exact hash`,row.model_manifest));
}
function renderFinal(){clear('#finalText');const f=current.final_interview;if(!f){$('#finalText').append(node('p','Final interview not yet available. The collaborator will supply it with the actual continuation.','pending'));return}$('#finalText').append(node('pre',f.text||printable(f)));}
function renderMessages(){
 if(!current)return;clear('#messages');const query=$('#search').value.toLowerCase(),role=$('#role').value,source=$('#session').value;
 const rows=current.events.filter(e=>e.source===source&&(role==='all'||e.role===role)&&(!query||printable(e.content).toLowerCase().includes(query)));
 const total=Math.max(1,Math.ceil(rows.length/pageSize));pageIndex=Math.max(0,Math.min(pageIndex,total-1));$('#page').textContent=`${pageIndex+1} / ${total} · ${rows.length} messages`;
 for(const e of rows.slice(pageIndex*pageSize,(pageIndex+1)*pageSize)){
  const el=node('section',null,'entry');el.append(node('div',`${e.role.toUpperCase()} · ${e.timestamp||''} · ${e.source}:${e.source_line}`,'meta'));
  const content=Array.isArray(e.content)?e.content:[{type:'text',text:e.content}];
  for(const b of content){
   if(!b||typeof b!=='object'){el.append(node('pre',printable(b)));continue}
   if(b.type==='text')el.append(node('pre',b.text||''));
   else if(b.type==='tool_use')el.append(details('Tool call · '+b.name,b.input));
   else if(b.type==='tool_result')el.append(details('Tool result · '+b.tool_use_id,b.content));
   else el.append(details('Recorded '+b.type,b));
  }
  $('#messages').append(el);
 }
 if(!rows.length)$('#messages').append(node('p','No messages match this filter.'));
}
async function renderSource(){if(!current)return;const f=current.source_files[Number($('#source').value)];if(!f){$('#code').textContent='No source file available.';return}$('#sourceMeta').textContent=f.phase+' · '+f.path;$('#code').textContent=await(await fetch(f.url)).text();}
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>tab(b.dataset.tab));
$('#attempt').onchange=renderAttempt;$('#source').onchange=renderSource;
for(const id of ['#session','#role','#search'])$(id).addEventListener(id==='#search'?'input':'change',()=>{pageIndex=0;renderMessages()});
$('#previous').onclick=()=>{pageIndex--;renderMessages()};$('#next').onclick=()=>{pageIndex++;renderMessages()};
(async()=>{manifest=await(await fetch('data/summary.json')).json();for(const r of manifest.historical_runs){const b=node('button');b.dataset.id=r.id;b.append(node('strong',`L${r.level} · ${r.id.split('-').at(-1)}`),node('small',r.status==='continuation_pending'?'3 attempts · continuation pending':'8 attempts · initial record'));b.onclick=()=>loadCase(r.id);$('#runs').append(b)}for(const r of manifest.harnesses){const a=node('a',r.label||r.version);a.title=r.version;a.href=r.web_download;a.style.display='block';a.style.fontSize='12px';a.style.marginBottom='12px';$('#releases').append(a)}for(const r of manifest.supplementary_downloads||[]){const a=node('a',r.label);a.href=r.path;a.style.display='block';a.style.fontSize='12px';a.style.marginBottom='12px';$('#references').append(a)}await loadCase(manifest.historical_runs.find(r=>r.id===location.hash.slice(1))?.id||manifest.historical_runs[0].id)})().catch(e=>{$('#summary').replaceChildren(node('p','Unable to load data. Serve this folder over HTTP; see the handoff README. '+e.message))});
