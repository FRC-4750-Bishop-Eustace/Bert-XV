'use strict';
let boot, state, currentView = 'launchpad', logBackend = 'rev', toastTimer, polling = false;
const $ = id => document.getElementById(id);
const icons = {
  play: '<svg viewBox="0 0 24 24" fill="none"><path d="m9 5 11 7-11 7V5Z" fill="currentColor"/><path d="M4 5v14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  log: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
  tool: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m14 4 5 5M4 20l9-9M13 5l4-2 4 4-2 4-6-6Z"/><circle cx="4" cy="20" r="2"/></svg>'
};
function node(tag, className, text) {
  const el = document.createElement(tag); if (className) el.className = className;
  if (text !== undefined) el.textContent = text; return el;
}
function toast(message) {
  $('toast').textContent = message; $('toast').hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').hidden = true, 8000);
}
async function api(path, body) {
  const options = body === undefined ? {} : {method:'POST', headers:{'Content-Type':'application/json','X-Bench-Token':boot.token}, body:JSON.stringify(body)};
  const response = await fetch(path, options);
  const data = await response.json(); if (!response.ok) throw new Error(data.error || 'That action could not finish.'); return data;
}
function showView(name) {
  currentView = name;
  document.querySelectorAll('.view').forEach(el => el.classList.toggle('active', el.id === 'view-' + name));
  document.querySelectorAll('.nav-button').forEach(el => el.classList.toggle('active', el.dataset.view === name));
  document.querySelector('main').scrollTop = 0;
}
async function bootstrap() {
  boot = await api('/api/bootstrap');
  document.title = boot.config.title; $('station-title').textContent = boot.config.title;
  $('station-subtitle').textContent = boot.config.subtitle || '';
  for (const [key, value] of Object.entries(boot.config.theme || {})) {
    if (/^#[a-fA-F0-9]{6}$/.test(value) && ['accent','street_sign'].includes(key)) document.documentElement.style.setProperty('--' + (key === 'street_sign' ? 'street' : key), value);
  }
  $('config-path').textContent = boot.config_path;
  $('config-editor').value = JSON.stringify(boot.config, null, 2);
  renderButtons(); renderControls();
}
function renderButtons() {
  $('buttons').replaceChildren();
  boot.config.buttons.filter(button => button.enabled !== false).forEach(button => {
    const el = node('button', 'tool-card' + (button.primary ? ' primary' : ''));
    if (['orange','green','blue'].includes(button.accent)) el.classList.add('accent-' + button.accent);
    el.dataset.action = button.action;
    const icon = node('span', 'icon-box'); icon.setAttribute('aria-hidden','true'); icon.innerHTML = icons[button.icon] || icons.tool;
    const copy = node('div'); copy.append(node('strong', '', button.label), node('p', '', button.description || ''));
    el.append(icon, copy); if (button.primary) el.append(node('span','arrow','↗'));
    el.addEventListener('click', () => runAction(button.action)); $('buttons').append(el);
  });
}
function formatted(control, value) { return control.format === 'percent' ? Math.round(value * 100) + '%' : String(value); }
async function saveSetting(key, value) {
  try {
    const data = await api('/api/settings', {values:{[key]:value}}); boot.settings = data.settings;
    $('settings-status').textContent = 'Saved on this Pi.'; return true;
  } catch(error) { toast(error.message); renderControls(); return false; }
}
function renderControls() {
  $('controls').replaceChildren();
  boot.config.controls.filter(control => control.enabled !== false).forEach(control => {
    const card = node('div','control-card'), label = node('label','',control.label), description = node('p','',control.description || '');
    const id = 'control-' + control.id; label.htmlFor = id; const inputRow = node('div','control-input');
    let input;
    if (control.type === 'toggle') {
      input = node('button','switch'); input.type = 'button'; input.setAttribute('role','switch'); input.setAttribute('aria-checked', String(boot.settings[control.id]));
      input.setAttribute('aria-label',control.label);
      const valueLabel = node('output','',boot.settings[control.id] ? 'On' : 'Off');
      input.addEventListener('click', async () => {
        const value = !boot.settings[control.id]; input.disabled = true;
        if(await saveSetting(control.id,value)) { input.setAttribute('aria-checked',String(value)); valueLabel.textContent = value ? 'On' : 'Off'; }
        input.disabled = false;
      }); inputRow.append(input,valueLabel);
    } else if(control.type === 'slider') {
      input = node('input'); input.type = 'range'; input.min = control.min; input.max = control.max; input.step = control.step || 1; input.value = boot.settings[control.id];
      const output = node('output','',formatted(control,Number(input.value))); output.htmlFor = id;
      input.addEventListener('input', () => output.textContent = formatted(control,Number(input.value)));
      input.addEventListener('change', () => saveSetting(control.id,Number(input.value))); inputRow.append(input,output);
    } else {
      input = node('select'); control.options.forEach((option,index) => {const el=node('option','',option.label);el.value=index; input.append(el);});
      input.value = control.options.findIndex(option => option.value === boot.settings[control.id]);
      input.addEventListener('change', () => saveSetting(control.id,control.options[Number(input.value)].value)); inputRow.append(input);
    }
    input.id = id; card.append(label,description,inputRow);
    if (control.action) {
      const apply = node('button','secondary-button control-apply',control.apply_label || 'Apply');
      apply.addEventListener('click', async () => {
        const value = control.type === 'slider' ? Number(input.value) : control.type === 'select' ? control.options[Number(input.value)].value : input.getAttribute('aria-checked') === 'true';
        if (await saveSetting(control.id,value)) runAction(control.action,value);
      }); card.append(apply);
    }
    $('controls').append(card);
  });
}
async function runAction(action, value) {
  try {
    const definition = boot.config.actions[action];
    if (definition.type === 'show_log') { logBackend = definition.backend; await refreshLog(); $('log-dialog').showModal(); return; }
    await api('/api/action',{action, value}); await poll();
  } catch(error) { toast(error.message); }
}
async function refreshLog() { $('log-content').textContent = (await api('/api/log/' + encodeURIComponent(logBackend))).text; }
async function poll() {
  if (polling) return; polling = true;
  try {
    state = await api('/api/state'); const job = state.job;
    $('job-status').textContent = job.message;
    $('status-pill').textContent = job.error ? 'Check log' : job.busy ? 'Starting…' : job.phase === 'complete' ? 'Open' : 'Ready';
    $('status-pill').classList.toggle('error',job.error);
    document.querySelectorAll('[data-action]').forEach(el => el.disabled = job.busy);
    ['backend','ready','browser'].forEach((name,index) => {
      const phase = {backend:0,ready:1,browser:2,complete:3}[job.phase] ?? -1;
      $('step-' + name).classList.toggle('active',job.busy && phase === index);
      $('step-' + name).classList.toggle('done',phase > index);
    });
    if(currentView === 'activity') {
      $('activity-list').replaceChildren();
      if(!state.events.length) $('activity-list').append(node('p','muted','Your next launch will show up here.'));
      state.events.slice().reverse().forEach(event => {const row=node('div','activity-row'); row.append(node('time','',event.time),node('span','',event.message)); $('activity-list').append(row);});
    }
  } catch(error) { $('job-status').textContent = 'Launchpad connection lost. Reopen the desktop shortcut.'; }
  finally { polling = false; }
}
document.querySelectorAll('.nav-button').forEach(el => el.addEventListener('click', () => {showView(el.dataset.view); poll();}));
$('desktop').addEventListener('click', () => api('/api/desktop',{}).then(() => window.close()).catch(error => toast(error.message)));
$('close-log').addEventListener('click', () => $('log-dialog').close());
$('refresh-log').addEventListener('click', () => refreshLog().catch(error => toast(error.message)));
$('reload-config').addEventListener('click', async () => {try {await api('/api/reload',{}); await bootstrap(); $('config-status').textContent = 'Layout reloaded.';}catch(error){toast(error.message);}});
$('save-config').addEventListener('click', async () => {
  try {const config=JSON.parse($('config-editor').value); await api('/api/config',{config}); await bootstrap(); $('config-status').textContent='Saved. Previous layout backed up.';}
  catch(error) {$('config-status').textContent=error.message; toast(error.message);}
});
setInterval(() => $('clock').textContent = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}),1000);
bootstrap().then(poll).catch(error => toast('Cannot load the launchpad: ' + error.message));
setInterval(poll,1000);
