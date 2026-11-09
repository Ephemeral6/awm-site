'use strict';

const casesElement = document.querySelector('#cases');
const detail = document.querySelector('#detail');
const filters = document.querySelectorAll('[data-filter]');
let cases = [];
let selected;
let filter = 'all';

function render() {
  const rows = cases.filter(run => filter === 'all' || `L${run.level}` === filter);
  if (!rows.includes(selected)) selected = rows[0];
  casesElement.innerHTML = rows.map(run => `
    <tr class="${run === selected ? 'selected' : ''}" data-case="${run.id}">
      <td><button class="casebutton" type="button" aria-pressed="${run === selected}">
        <b>L${run.level} / ${run.id.split('-').at(-1)}</b><span>${run.protocol}</span>
      </button></td>
      <td><span class="number">${run.budget.value}</span><span class="budget-source">${run.budget.source}</span></td>
      <td class="scope">${run.proof.scope}</td><td aria-hidden="true">↗</td>
    </tr>`).join('');
  const run = selected;
  detail.innerHTML = `
    <p class="eyebrow">${run.protocol} / LEVEL ${run.level}</p>
    <h3>${run.id.split('-').at(-1)}</h3>
    <p><b>Budget source</b><br>${run.budget.description}</p>
    <p><b>${run.proof.phase} theorem</b><br><code>${run.proof.theorem}</code></p>
    <p>${run.proof.description}</p>
    <a class="textlink" href="records/#${run.id}">Open attempt record →</a>`;
}

casesElement.addEventListener('click', event => {
  const row = event.target.closest('[data-case]');
  if (!row) return;
  const restoreFocus = document.activeElement === row.querySelector('button');
  selected = cases.find(run => run.id === row.dataset.case);
  render();
  if (restoreFocus) casesElement.querySelector('[aria-pressed="true"]').focus();
});

async function load() {
  const response = await fetch('records/data/summary.json');
  if (!response.ok) throw Error(`HTTP ${response.status}`);
  cases = (await response.json()).runs;
  render();
  for (const button of filters) {
    button.addEventListener('click', () => {
      filter = button.dataset.filter;
      for (const item of filters) {
        item.classList.toggle('active', item === button);
        item.setAttribute('aria-pressed', String(item === button));
      }
      render();
    });
  }
}

load().catch(error => {
  detail.textContent = `Unable to load the replication records (${error.message}).`;
});
