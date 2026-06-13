/*
 * NetworkzeroMonitor - Mobile PWA logic
 * Ionity (Pty) Ltd - www.ionity.today
 *
 * Talks to the Flask API on the same origin, renders the full network
 * stack (interfaces -> connectivity -> cellular/wifi -> satellite -> GNSS)
 * and provides interactive ping / DNS / port tools.
 */

const api = (path) => fetch(path, { headers: { 'Accept': 'application/json' } }).then((r) => r.json());

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html !== undefined) n.innerHTML = html;
  return n;
};

function fmtBytes(n) {
  if (n == null) return '—';
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  let i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(1)} ${units[i]}`;
}

function card(title, pill) {
  const c = el('div', 'card');
  const h = el('h2', null, title);
  if (pill) {
    const p = el('span', `pill ${pill.cls || ''}`, pill.text);
    h.appendChild(p);
  }
  c.appendChild(h);
  return c;
}

function kv(parent, k, v) {
  const row = el('div', 'kv');
  row.appendChild(el('span', 'k', k));
  row.appendChild(el('span', 'v', v == null || v === '' ? '—' : String(v)));
  parent.appendChild(row);
}

/* ----------------------------- Tab switching ---------------------------- */
document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.view').forEach((v) => v.classList.remove('active'));
    tab.classList.add('active');
    $(`#view-${tab.dataset.view}`).classList.add('active');
  });
});

/* ------------------------------- Dashboard ------------------------------ */
async function loadDashboard() {
  const grid = $('#dashboard-grid');
  grid.innerHTML = '';
  let data;
  try {
    data = await api('/api/overview');
  } catch (e) {
    setStatus('bad', 'Cannot reach NetworkzeroMonitor server');
    return;
  }

  const conn = data.connectivity || {};
  const qual = conn.quality || 'Unknown';
  const cls = !conn.connected ? 'bad' : (qual === 'Excellent' ? 'ok' : 'warn');
  setStatus(cls, `Internet: ${conn.connected ? qual : 'No Connection'}`);

  // Network info card
  const net = data.network || {};
  const c1 = card('🖥 Host & Network');
  kv(c1, 'Hostname', net.hostname);
  kv(c1, 'Local IP', net.local_ip);
  kv(c1, 'Public IP', net.public_ip);
  kv(c1, 'Platform', net.platform);
  grid.appendChild(c1);

  // Connectivity card
  const c2 = card('🌐 Connectivity', { cls, text: qual });
  (conn.tests || []).forEach((t) => kv(c2, t.domain, t.reachable ? '✓ reachable' : '✗ down'));
  grid.appendChild(c2);

  // Quick WAN summary from extended layers
  const ext = data.extended || {};
  grid.appendChild(summaryCellular(ext.cellular));
  grid.appendChild(summarySatellite(ext.satellite_internet));
  grid.appendChild(summaryGnss(ext.gnss));

  $('#foot-meta').textContent = `NetworkzeroMonitor v${data.version || ''} · ${net.timestamp || ''}`;
}

function summaryCellular(cell) {
  if (!cell || !cell.available) {
    const c = card('📶 Cellular', { cls: 'warn', text: 'n/a' });
    c.appendChild(el('div', 'muted', (cell && cell.reason) || 'No cellular modem'));
    return c;
  }
  const m = cell.modems[0] || {};
  const c = card('📶 Cellular', { cls: 'ok', text: m.generation || '—' });
  kv(c, 'Operator', m.operator);
  kv(c, 'Generation', m.generation);
  kv(c, 'Signal', m.signal_percent != null ? `${m.signal_percent}%` : '—');
  kv(c, 'State', m.state);
  return c;
}

function summarySatellite(sat) {
  if (!sat) return card('🛰 Satellite Internet', { cls: 'warn', text: 'n/a' });
  if (!sat.available) {
    const c = card('🛰 Satellite Internet', { cls: 'warn', text: 'n/a' });
    c.appendChild(el('div', 'muted', sat.reason || 'No satellite link'));
    return c;
  }
  const c = card('🛰 Satellite Internet', { cls: 'ok', text: sat.provider || 'link' });
  kv(c, 'Provider', sat.provider);
  kv(c, 'Dish reachable', sat.dish_reachable ? 'yes' : 'no');
  if (sat.ping_latency_ms != null) kv(c, 'Latency', `${sat.ping_latency_ms.toFixed?.(1) ?? sat.ping_latency_ms} ms`);
  if (sat.downlink_bps != null) kv(c, 'Downlink', `${fmtBytes(sat.downlink_bps)}/s`);
  if (sat.obstruction_fraction != null) kv(c, 'Obstruction', `${(sat.obstruction_fraction * 100).toFixed(2)}%`);
  return c;
}

function summaryGnss(gnss) {
  if (!gnss || !gnss.available) {
    const c = card('📡 GNSS Positioning', { cls: 'warn', text: 'n/a' });
    c.appendChild(el('div', 'muted', (gnss && gnss.reason) || 'No GNSS receiver'));
    return c;
  }
  const fix = gnss.fix || {};
  const sats = gnss.satellites || {};
  const c = card('📡 GNSS Positioning', { cls: 'ok', text: fix.mode || 'fix' });
  kv(c, 'Fix', fix.mode);
  kv(c, 'Latitude', fix.latitude);
  kv(c, 'Longitude', fix.longitude);
  kv(c, 'Satellites', `${sats.used ?? 0}/${sats.in_view ?? 0} used`);
  return c;
}

/* ------------------------------ Layers view ----------------------------- */
async function loadLayers() {
  const grid = $('#layers-grid');
  grid.innerHTML = '<div class="muted">Loading layers…</div>';
  let layers, traffic;
  try {
    [layers, traffic] = await Promise.all([api('/api/extended/all'), api('/api/traffic')]);
  } catch (e) {
    grid.innerHTML = '<div class="muted">Failed to load network layers.</div>';
    return;
  }
  grid.innerHTML = '';

  // Wi-Fi
  const wifi = layers.wifi || {};
  if (wifi.available && wifi.networks.length) {
    const w = wifi.networks[0];
    const c = card('📡 Wi-Fi Link', { cls: 'ok', text: w.band });
    kv(c, 'SSID', w.ssid);
    kv(c, 'Signal', w.signal_percent != null ? `${w.signal_percent}%` : '—');
    kv(c, 'Band', w.band);
    kv(c, 'Frequency', w.frequency_mhz ? `${w.frequency_mhz} MHz` : '—');
    kv(c, 'Rate', w.rate);
    kv(c, 'Security', w.security);
    grid.appendChild(c);
  } else {
    const c = card('📡 Wi-Fi Link', { cls: 'warn', text: 'n/a' });
    c.appendChild(el('div', 'muted', wifi.reason || 'No active Wi-Fi'));
    grid.appendChild(c);
  }

  // Cellular (full)
  grid.appendChild(summaryCellular(layers.cellular));
  // Satellite internet (full)
  grid.appendChild(summarySatellite(layers.satellite_internet));

  // Per-interface traffic
  const ifaces = (traffic && traffic.interfaces) || {};
  Object.keys(ifaces).forEach((name) => {
    const d = ifaces[name];
    const c = card(`🔌 ${name}`);
    kv(c, 'Sent', fmtBytes(d.bytes_sent));
    kv(c, 'Received', fmtBytes(d.bytes_recv));
    kv(c, 'Packets out/in', `${d.packets_sent} / ${d.packets_recv}`);
    kv(c, 'Errors out/in', `${d.errout} / ${d.errin}`);
    kv(c, 'Drops out/in', `${d.dropout} / ${d.dropin}`);
    grid.appendChild(c);
  });
}

/* ------------------------------- GNSS view ------------------------------ */
async function loadGnss() {
  const panel = $('#gnss-panel');
  panel.innerHTML = '<div class="muted">Querying GNSS receiver…</div>';
  let gnss;
  try {
    gnss = await api('/api/extended/gnss');
  } catch (e) {
    panel.innerHTML = '<div class="muted">Failed to query GNSS.</div>';
    return;
  }
  panel.innerHTML = '';

  if (!gnss.available) {
    const c = card('📡 GNSS / Satellite Positioning', { cls: 'warn', text: 'unavailable' });
    c.appendChild(el('div', 'muted', gnss.reason || 'No GNSS receiver detected.'));
    c.appendChild(el('div', 'muted', 'Connect a GNSS receiver and run gpsd to view live fix and satellites.'));
    panel.appendChild(c);
    return;
  }

  const fix = gnss.fix || {};
  const cFix = card('🛰 Position Fix', { cls: 'ok', text: fix.mode || 'fix' });
  kv(cFix, 'Fix mode', fix.mode);
  kv(cFix, 'Latitude', fix.latitude);
  kv(cFix, 'Longitude', fix.longitude);
  kv(cFix, 'Altitude', fix.altitude_m != null ? `${fix.altitude_m} m` : '—');
  kv(cFix, 'Speed', fix.speed_mps != null ? `${fix.speed_mps} m/s` : '—');
  kv(cFix, 'UTC time', fix.time);
  panel.appendChild(cFix);

  const sats = gnss.satellites || {};
  const cSat = card('📡 Satellites', { cls: 'ok', text: `${sats.used ?? 0}/${sats.in_view ?? 0}` });
  kv(cSat, 'In view', sats.in_view);
  kv(cSat, 'Used in fix', sats.used);
  kv(cSat, 'HDOP / VDOP', `${sats.hdop ?? '—'} / ${sats.vdop ?? '—'}`);

  const detail = sats.detail || [];
  if (detail.length) {
    const table = el('table', 'sat-table');
    table.innerHTML = '<thead><tr><th>PRN</th><th>System</th><th>Elev</th><th>SNR</th><th>Used</th></tr></thead>';
    const tb = el('tbody');
    detail.sort((a, b) => (b.snr || 0) - (a.snr || 0)).forEach((s) => {
      const tr = el('tr');
      tr.innerHTML =
        `<td>${s.prn ?? '—'}</td>` +
        `<td>${s.constellation ?? '—'}</td>` +
        `<td>${s.elevation ?? '—'}°</td>` +
        `<td>${s.snr ?? '—'}</td>` +
        `<td>${s.used ? '✓' : ''}</td>`;
      tb.appendChild(tr);
    });
    table.appendChild(tb);
    cSat.appendChild(table);
  }
  panel.appendChild(cSat);
}

/* ------------------------------- Tools ---------------------------------- */
document.querySelectorAll('[data-tool]').forEach((btn) => {
  btn.addEventListener('click', () => runTool(btn.dataset.tool));
});

async function runTool(tool) {
  if (tool === 'ping') {
    const host = encodeURIComponent($('#ping-host').value.trim());
    show('#ping-out', 'Pinging…');
    const r = await api(`/api/ping?host=${host}`);
    show('#ping-out', JSON.stringify(r, null, 2));
  } else if (tool === 'dns') {
    const domain = encodeURIComponent($('#dns-domain').value.trim());
    const server = encodeURIComponent($('#dns-server').value.trim());
    show('#dns-out', 'Resolving…');
    const r = await api(`/api/dns?domain=${domain}${server ? `&server=${server}` : ''}`);
    show('#dns-out', JSON.stringify(r, null, 2));
  } else if (tool === 'ports') {
    const host = encodeURIComponent($('#ports-host').value.trim());
    const ports = encodeURIComponent($('#ports-list').value.trim());
    show('#ports-out', 'Scanning…');
    const r = await api(`/api/ports?host=${host}${ports ? `&ports=${ports}` : ''}`);
    show('#ports-out', JSON.stringify(r, null, 2));
  }
}

function show(sel, text) { $(sel).textContent = text; }

/* ------------------------------- Status --------------------------------- */
function setStatus(cls, text) {
  $('#status-dot').className = `dot ${cls}`;
  $('#status-text').textContent = text;
}

/* ----------------------------- Orchestration ---------------------------- */
function refreshActive() {
  const view = document.querySelector('.tab.active').dataset.view;
  if (view === 'dashboard') return loadDashboard();
  if (view === 'layers') return loadLayers();
  if (view === 'gnss') return loadGnss();
}

$('#refresh').addEventListener('click', async () => {
  const btn = $('#refresh');
  btn.classList.add('spin');
  try { await refreshActive(); } finally { btn.classList.remove('spin'); }
});

// Re-load a view's data the first time its tab is opened.
document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => refreshActive());
});

// Register service worker for offline shell + installability.
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('service-worker.js').catch(() => {});
  });
}

// Initial load + light auto-refresh of the dashboard.
loadDashboard();
setInterval(() => {
  if (document.querySelector('.tab.active').dataset.view === 'dashboard') loadDashboard();
}, 15000);
