'use strict';

let manifest, current, active = 'attempts', pageIndex = 0, loadSequence = 0, sourceSequence = 0;
const pageSize = 35;
const $ = selector => document.querySelector(selector);

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text != null) element.textContent = text;
  if (className) element.className = className;
  return element;
}
function clear(selector) { $(selector).replaceChildren(); }
function printable(value) { return typeof value === 'string' ? value : JSON.stringify(value, null, 2); }
function option(value, label) { const element = node('option', label); element.value = value; return element; }
function details(title, content) {
  const element = node('details');
  element.append(node('summary', title), node('pre', printable(content)));
  return element;
}
async function request(url, asText = false) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load ${url} (${response.status}).`);
  return asText ? response.text() : response.json();
}
function tab(name) {
  active = name;
  document.querySelectorAll('.pane').forEach(element => { element.hidden = element.id !== name; });
  document.querySelectorAll('[data-tab]').forEach(button => {
    const selected = button.dataset.tab === name;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  if (name === 'raw') renderMessages();
}
async function loadCase(id) {
  const sequence = ++loadSequence;
  $('#summary').setAttribute('aria-busy', 'true');
  clear('#summary');
  $('#summary').append(node('p', 'Loading run records…'));
  try {
    const data = await request(`data/${id}.json`);
    if (sequence !== loadSequence) return;
    current = data;
    const summary = current.summary;
    clear('#summary');
    $('#summary').append(node('h2', `Level ${summary.level} · ${summary.id}`));
    $('#summary').append(node('div', `${summary.recorded_attempts} of 8 initial attempts recorded · Sealed budget ${summary.sealed_cap} · Engine threshold ${summary.engine_minimum_cap} · Reported initial bound ${summary.reported_initial_bound}`, 'facts'));
    if (summary.bound_note) $('#summary').append(node('p', summary.bound_note, 'muted'));
    if (summary.pending_note) $('#summary').append(node('p', 'Continuation pending: the collaborator will upload attempts 4–8 and the final interview.', 'pending'));
    const download = node('a', 'Download this run’s archive ↗');
    download.href = summary.download;
    download.download = '';
    $('#summary').append(download);
    const coverage = summary.id.endsWith('2a3cc5')
      ? 'No per-attempt file-hash manifest was archived for this partial run; original proof sources and tool history are retained.'
      : `${summary.missing_source_version_count} older file versions could not be recovered as full snapshots; their recorded hashes and tool history are retained.`;
    $('#summary').append(node('p', `${summary.raw_messages.toLocaleString()} raw user/assistant messages. ${coverage}`, 'muted'));
    document.querySelectorAll('#runs button').forEach(button => {
      const selected = button.dataset.id === id;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    clear('#attempt');
    for (const row of current.attempts) $('#attempt').append(option(row.attempt, `Attempt ${row.attempt}`));
    clear('#session');
    for (const source of new Set(current.events.map(event => event.source))) $('#session').append(option(source, source));
    clear('#source');
    for (const [index, file] of current.source_files.entries()) $('#source').append(option(index, `[${file.phase}] ${file.path}`));
    $('#search').value = '';
    pageIndex = 0;
    renderAttempt();
    renderFinal();
    clear('#repairText');
    const repair = current.selected_external_repair;
    $('#repairText').append(node('p', repair ? repair.scope : 'No selected external-feedback repair is linked to this run.'));
    if (repair) $('#repairText').append(node('pre', repair.answers));
    const url = new URL(location.href);
    url.searchParams.set('run', id);
    history.replaceState(null, '', url);
    tab(active);
    await renderSource();
  } catch (error) {
    if (sequence !== loadSequence) return;
    clear('#summary');
    $('#summary').append(node('p', `${error.message} Please reload or choose another run.`, 'pending'));
  } finally {
    if (sequence === loadSequence) $('#summary').removeAttribute('aria-busy');
  }
}
function renderAttempt() {
  clear('#answers');
  if (!current) return;
  const row = current.attempts.find(attempt => String(attempt.attempt) === $('#attempt').value);
  if (!row) return;
  $('#answers').append(node('h3', `Attempt ${row.attempt}`));
  if (row.answers.length) {
    for (const text of new Set(row.answers)) $('#answers').append(node('pre', text));
  } else {
    $('#answers').append(node('p', 'This partial run has a console audit and raw session, but no structured round-answer record. Use Full session or the archive.'));
  }
  if (row.verdict) $('#answers').append(details('Recorded verdict', row.verdict));
  if (row.gate) $('#answers').append(details('Historical gate record', row.gate));
  if (row.model_manifest) $('#answers').append(details(`Model / Lean inventory: ${row.recovered_files} of ${row.model_files} files recovered by exact hash`, row.model_manifest));
}
function renderFinal() {
  clear('#finalText');
  const interview = current.final_interview;
  $('#finalText').append(node(interview ? 'pre' : 'p', interview ? interview.text || printable(interview) : 'Final interview not yet available. The collaborator will supply it with the actual continuation.', interview ? null : 'pending'));
}
function renderMessages() {
  if (!current) return;
  clear('#messages');
  const query = $('#search').value.toLowerCase(), role = $('#role').value, source = $('#session').value;
  const rows = current.events.filter(event => event.source === source && (role === 'all' || event.role === role) && (!query || printable(event.content).toLowerCase().includes(query)));
  const total = Math.max(1, Math.ceil(rows.length / pageSize));
  pageIndex = Math.max(0, Math.min(pageIndex, total - 1));
  $('#page').textContent = `${pageIndex + 1} / ${total} · ${rows.length.toLocaleString()} messages`;
  $('#previous').disabled = pageIndex === 0;
  $('#next').disabled = pageIndex === total - 1;
  for (const event of rows.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize)) {
    const entry = node('section', null, 'entry');
    entry.append(node('div', `${event.role.toUpperCase()} · ${event.timestamp || ''} · ${event.source}:${event.source_line}`, 'meta'));
    const content = Array.isArray(event.content) ? event.content : [{ type: 'text', text: event.content }];
    for (const block of content) {
      if (!block || typeof block !== 'object') { entry.append(node('pre', printable(block))); continue; }
      if (block.type === 'text') entry.append(node('pre', block.text || ''));
      else if (block.type === 'tool_use') entry.append(details(`Tool call · ${block.name}`, block.input));
      else if (block.type === 'tool_result') entry.append(details(`Tool result · ${block.tool_use_id}`, block.content));
      else entry.append(details(`Recorded ${block.type}`, block));
    }
    $('#messages').append(entry);
  }
  if (!rows.length) $('#messages').append(node('p', 'No messages match this filter.'));
}
async function renderSource() {
  const sequence = ++sourceSequence;
  if (!current) return;
  const file = current.source_files[Number($('#source').value)];
  if (!file) { $('#code').textContent = 'No source file available.'; return; }
  $('#sourceMeta').textContent = `${file.phase} · ${file.path}`;
  $('#code').textContent = 'Loading source…';
  try {
    const text = await request(file.url, true);
    if (sequence === sourceSequence) $('#code').textContent = text;
  } catch (error) {
    if (sequence === sourceSequence) $('#code').textContent = error.message;
  }
}
function renderRelease(release) {
  const card = node('article', null, 'release-card');
  const automatic = release.id.startsWith('02-');
  card.append(node('h3', release.label));
  card.append(node('p', automatic
    ? 'After a proof passes, audit its premises, test disagreements in the game, revise the model and prove again. Latest release: v2.3.1.'
    : 'Explicit transformation steps, eight initial attempts, and a separate external-feedback phase. No built-in proof-first automatic repair.'));
  const download = node('a', `Download source · ${release.offline_validation.zip_mib} MB` , 'btn');
  download.href = release.web_download;
  download.download = '';
  card.append(download);
  card.append(node('p', release.version, 'version'));
  const checksum = node('details');
  checksum.append(node('summary', 'SHA-256'), node('code', release.sha256));
  card.append(checksum);
  $('#releases').append(card);
}

const tabs = [...document.querySelectorAll('[data-tab]')];
tabs.forEach((button, index) => {
  button.onclick = () => tab(button.dataset.tab);
  button.onkeydown = event => {
    let target;
    if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') target = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') target = 0;
    if (event.key === 'End') target = tabs.length - 1;
    if (target == null) return;
    event.preventDefault();
    tabs[target].focus();
    tab(tabs[target].dataset.tab);
  };
});
$('#attempt').onchange = renderAttempt;
$('#source').onchange = renderSource;
for (const selector of ['#session', '#role', '#search']) $(selector).addEventListener(selector === '#search' ? 'input' : 'change', () => { pageIndex = 0; renderMessages(); });
$('#previous').onclick = () => { pageIndex--; renderMessages(); };
$('#next').onclick = () => { pageIndex++; renderMessages(); };

(async () => {
  manifest = await request('data/summary.json');
  for (const row of manifest.historical_runs) {
    const button = node('button');
    button.type = 'button';
    button.dataset.id = row.id;
    button.append(node('strong', `L${row.level} · ${row.id.split('-').at(-1)}`), node('small', row.status === 'continuation_pending' ? '3 attempts · pending' : '8 attempts · initial record'));
    button.onclick = () => loadCase(row.id);
    $('#runs').append(button);
  }
  for (const release of manifest.harnesses) renderRelease(release);
  for (const reference of manifest.supplementary_downloads || []) {
    const link = node('a', reference.label);
    link.href = reference.path;
    $('#references').append(link);
  }
  const requested = new URL(location.href).searchParams.get('run') || location.hash.slice(1);
  const selected = manifest.historical_runs.find(row => row.id === requested);
  const firstComplete = manifest.historical_runs.find(row => row.status === 'initial8_record_present');
  await loadCase(selected ? selected.id : (firstComplete || manifest.historical_runs[0]).id);
})().catch(error => {
  $('#summary').replaceChildren(node('p', `${error.message} Reload the page to retry.`, 'pending'));
});
