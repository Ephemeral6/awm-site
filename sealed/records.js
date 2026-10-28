'use strict';
const REVISION='20261027-run-details', PREFIX=document.body.dataset.prefix||'', BASELINE=document.body.dataset.kind==='baseline';
const $=selector=>document.querySelector(selector);
let manifest,current,active='attempts',pageIndex=0,sequence=0,sourceSequence=0;
const pageSize=35;
function assetURL(path){const url=new URL(PREFIX+path,location.href);url.searchParams.set('v',REVISION);return url.href;}
async function request(path,text=false){const response=await fetch(assetURL(path),{cache:'no-store'});if(!response.ok)throw new Error(`Could not load ${path} (${response.status}).`);return text?response.text():response.json();}
function node(tag,text,className){const element=document.createElement(tag);if(text!=null)element.textContent=text;if(className)element.className=className;return element;}
function printable(value){return typeof value==='string'?value:JSON.stringify(value,null,2);}
function option(value,label){const element=node('option',label);element.value=value;return element;}
function details(title,value){const element=node('details');element.append(node('summary',title),node('pre',printable(value)));return element;}
function bound(row){const value=row.reported_initial_bound;return value==null||value===''?'Bound —':`Bound ${value}${row.repaired_bound==null?'':' → '+row.repaired_bound}`;}
const player=new MotionPlayer(path=>request(path));
function selectedRow(){return manifest.historical_runs.find(row=>row.id===current?.summary.id);}
function updateURL(){if(!current)return;const url=new URL(location.href);url.searchParams.set('run',current.summary.id);url.searchParams.set('attempt',$('#attempt').value||'1');url.searchParams.set('view',active);if(active==='actions'&&$('#motionAttempt').value.startsWith('feedback:'))url.searchParams.set('motion',$('#motionAttempt').value);else url.searchParams.delete('motion');url.hash='';history.replaceState(null,'',url);}
function tab(name){
  active=name;
  document.querySelectorAll('.pane').forEach(element=>{element.hidden=element.id!==name;});
  document.querySelectorAll('[data-tab]').forEach(button=>{button.classList.toggle('active',button.dataset.tab===name);button.setAttribute('aria-selected',String(button.dataset.tab===name));});
  if(name==='raw')renderMessages();
  if(name==='models')renderSource();
  if(name==='actions')renderActions();else player.pause();
  updateURL();
}
function renderActions(){
  if(!current)return;
  const row=selectedRow();
  const value=$('#motionAttempt').value,feedback=value.startsWith('feedback:'),attempt=Number(feedback?value.split(':')[1]:value),url=feedback?row.feedback_motion_url:row.motion_url;
  if(!url){$('#motionStatus').textContent='No action log is available for this run.';return;}
  $('#motionPhase').textContent=feedback?`External feedback · attempt ${attempt} of ${row.feedback_motion_attempts}. This stage follows the original eight attempts.`:`Original attempt ${attempt} of 8.`;
  player.show(url,attempt,manifest.palette);
  $('#motionDownload').href=assetURL(url);
}
async function loadCase(id,requestedAttempt=1,requestedMotion=null){
  const ticket=++sequence;player.pause();++player.sequence;$('#motionFrames').hidden=true;$('#summary').replaceChildren(node('p','Loading run records…'));
  try{
    const row=manifest.historical_runs.find(row=>row.id===id),data=await request(row.data);
    if(ticket!==sequence)return;current=data;const s=current.summary;
    $('#summary').replaceChildren(node('h2',`Level ${s.level} · ${s.id}`));
    $('#summary').append(node('div',`${s.recorded_attempts}/8 original attempts · sealed budget ${s.sealed_cap} · engine threshold ${s.engine_minimum_cap} · ${bound(row)}`,'facts'));
    for(const text of [row.bound_note,row.repair_note,s.completion_note])if(text)$('#summary').append(node('p',text,'muted'));
    if(s.pending_note)$('#summary').append(node('p',s.pending_note,'pending'));
    const download=node('a',BASELINE?'Download the original baseline records':'Download this run’s archive');download.href=assetURL(s.download);download.download='';$('#summary').append(download);
    if(s.raw_messages!=null)$('#summary').append(node('p',`${s.raw_messages.toLocaleString()} user/assistant messages. ${s.model_coverage_note||`${s.missing_source_version_count||0} older source versions lack full snapshots; tool history is retained.`}`,'muted'));
    document.querySelectorAll('#runs button').forEach(button=>{button.classList.toggle('active',button.dataset.id===id);button.setAttribute('aria-pressed',String(button.dataset.id===id));});
    for(const selector of ['#attempt','#motionAttempt']){
      $(selector).replaceChildren();for(const attempt of current.attempts)$(selector).append(option(attempt.attempt,`Attempt ${attempt.attempt}`));
      $(selector).value=String(current.attempts.some(r=>r.attempt===Number(requestedAttempt))?requestedAttempt:1);
    }
    if(row.feedback_motion_url){const group=node('optgroup');group.label='After external feedback';for(let k=1;k<=row.feedback_motion_attempts;k++)group.append(option(`feedback:${k}`,`Feedback attempt ${k}`));$('#motionAttempt').append(group);}
    if(requestedMotion&&[...$('#motionAttempt').options].some(o=>o.value===requestedMotion))$('#motionAttempt').value=requestedMotion;
    $('#session').replaceChildren();for(const source of new Set((current.events||[]).map(e=>e.source)))$('#session').append(option(source,source));
    $('#source').replaceChildren();for(const [i,file]of(current.source_files||[]).entries())$('#source').append(option(i,`[${file.phase}] ${file.path}`));
    $('#search').value='';pageIndex=0;renderAttempt();renderFinal();renderFeedback();tab(active);
  }catch(error){if(ticket===sequence)$('#summary').replaceChildren(node('p',error.message,'pending'));}
}
function renderAttempt(){
  $('#answers').replaceChildren();if(!current)return;
  const row=current.attempts.find(r=>String(r.attempt)===$('#attempt').value);if(!row)return;
  $('#answers').append(node('h3',`Attempt ${row.attempt}`));
  for(const answer of new Set(row.answers||[]))$('#answers').append(node('pre',answer));
  if(!(row.answers||[]).length)$('#answers').append(node('p','No structured answer is archived. Consult the full session or download.'));
  if(row.questions)$('#answers').append(details('Prompts for this attempt',row.questions));
  if(row.continuation_note)$('#answers').append(node('p',row.continuation_note,'muted'));
  if(row.verdict)$('#answers').append(details('Recorded verdict',row.verdict));
  if(row.gate)$('#answers').append(details('Historical gate record',row.gate));
  if(row.model_manifest)$('#answers').append(details(`Source inventory: ${row.recovered_files}/${row.model_files} files recovered by exact hash`,row.model_manifest));
}
function renderFinal(){const f=current.final_interview;$('#finalText').replaceChildren(node(f?'pre':'p',f?(f.text||printable(f)):'No final interview is archived.'));}
function renderFeedback(){
  $('#repairText').replaceChildren();const feedback=current.feedback;
  if(feedback){
    $('#repairText').append(node('p',feedback.scope));
    for(const turn of feedback.turns){$('#repairText').append(node('h3',turn.phase));if(turn.prompt)$('#repairText').append(details('Prompt',turn.prompt));$('#repairText').append(node('pre',turn.text));}
    $('#repairText').append(details('Final reported fields',feedback.final));
  }else{
    const repair=current.selected_external_repair;
    $('#repairText').append(node('p',repair?repair.scope:'No external-feedback round is linked to this run.'));
    if(repair)$('#repairText').append(node('pre',repair.answers));
  }
}
function renderMessages(){
  if(!current)return;$('#messages').replaceChildren();
  const query=$('#search').value.toLowerCase(),role=$('#role').value,source=$('#session').value;
  const rows=(current.events||[]).filter(e=>e.source===source&&(role==='all'||e.role===role)&&(!query||printable(e.content).toLowerCase().includes(query)));
  const total=Math.max(1,Math.ceil(rows.length/pageSize));pageIndex=Math.max(0,Math.min(pageIndex,total-1));
  $('#page').textContent=`${pageIndex+1} / ${total} · ${rows.length.toLocaleString()} messages`;
  $('#previous').disabled=pageIndex===0;$('#next').disabled=pageIndex===total-1;
  for(const event of rows.slice(pageIndex*pageSize,(pageIndex+1)*pageSize)){
    const entry=node('section',null,'entry');entry.append(node('div',`${event.role.toUpperCase()} · ${event.timestamp||''} · ${event.source}:${event.source_line}`,'meta'));
    const content=Array.isArray(event.content)?event.content:[{type:'text',text:event.content}];
    for(const block of content){
      if(!block||typeof block!=='object')entry.append(node('pre',printable(block)));
      else if(block.type==='text')entry.append(node('pre',block.text||''));
      else if(block.type==='tool_use')entry.append(details(`Tool call · ${block.name}`,block.input));
      else if(block.type==='tool_result')entry.append(details(`Tool result · ${block.tool_use_id}`,block.content));
      else entry.append(details(`Recorded ${block.type}`,block));
    }
    $('#messages').append(entry);
  }
  if(!rows.length)$('#messages').append(node('p','No messages match this filter.'));
}
async function renderSource(){
  const ticket=++sourceSequence,file=(current?.source_files||[])[Number($('#source').value)];
  if(!file){$('#code').textContent='No separate source file is archived.';return;}
  $('#sourceMeta').textContent=`${file.phase} · ${file.path}`;$('#code').textContent='Loading source…';
  try{const text=await request(file.url,true);if(ticket===sourceSequence)$('#code').textContent=text;}
  catch(error){if(ticket===sourceSequence)$('#code').textContent=error.message;}
}
document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>tab(button.dataset.tab));
$('#attempt').onchange=()=>{$('#motionAttempt').value=$('#attempt').value;renderAttempt();updateURL();};
$('#motionAttempt').onchange=()=>{if(!$('#motionAttempt').value.startsWith('feedback:')){$('#attempt').value=$('#motionAttempt').value;renderAttempt();}renderActions();updateURL();};
$('#source').onchange=renderSource;
for(const selector of ['#session','#role','#search'])$(selector).addEventListener(selector==='#search'?'input':'change',()=>{pageIndex=0;renderMessages();});
$('#previous').onclick=()=>{pageIndex--;renderMessages();};$('#next').onclick=()=>{pageIndex++;renderMessages();};
(async()=>{
  manifest=await request(BASELINE?'data/baselines.json':'data/summary.json');
  for(const row of manifest.historical_runs){
    const button=node('button');button.dataset.id=row.id;button.type='button';
    button.append(node('strong',`L${row.level} · ${row.id.split('-').at(-1)}`));
    if(BASELINE)button.append(node('small',row.agent));
    button.append(node('span',bound(row),'run-bound'),node('small',`${row.recorded_attempts} attempts · ${row.final_interview_present?'final interview':'interview pending'}`));
    button.title=[row.bound_note,row.repair_note].filter(Boolean).join('\n');
    button.onclick=()=>loadCase(row.id);$('#runs').append(button);
  }
  for(const release of manifest.harnesses||[]){const a=node('a',release.label||release.version);a.href=assetURL(release.web_download);a.className='release-link';$('#releases').append(a);}
  for(const reference of manifest.supplementary_downloads||[]){const a=node('a',reference.label);a.href=assetURL(reference.path);$('#references').append(a);}
  const params=new URL(location.href).searchParams,requested=params.get('run')||location.hash.slice(1);
  const selected=manifest.historical_runs.find(row=>row.id===requested)||manifest.historical_runs[0];
  if([...document.querySelectorAll('[data-tab]')].some(button=>button.dataset.tab===params.get('view')))active=params.get('view');
  await loadCase(selected.id,Number(params.get('attempt')||1),params.get('motion'));
})().catch(error=>{$('#summary').replaceChildren(node('p',error.message,'pending'));});
