#!/usr/bin/env python3
"""Add PRODUCT_HISTORY data and expandable item rows to the 採購行為 matrix."""
import json, re

with open('product_history.json', encoding='utf-8') as f:
    PH = json.load(f)

with open('index.html', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS ─────────────────────────────────────────────────────────────────────
CSS = """
/* ── Product history drill-down ── */
.pb-table tr.pb-data-row { cursor:pointer; }
.pb-table tr.pb-data-row:hover td { background:rgba(44,75,170,.04); }
.pb-table tr.pb-detail-row td { padding:8px 10px 12px 20px; background:#fafafa; }
.pb-detail-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:8px; }
.pb-detail-yr { }
.pb-detail-yr-hdr { font-size:10px; font-weight:700; color:#aaa; margin-bottom:5px; text-transform:uppercase; }
.pb-item-tag { display:inline-block; font-size:10px; padding:1px 6px; border-radius:8px; margin:1px 2px 1px 0;
  background:#f0f4ff; color:#3a5cb5; border:1px solid #d0dcf5; line-height:1.7; }
.pb-item-tag.new-item  { background:#e8f5e9; color:#2e7d32; border-color:#b8dfbf; }
.pb-item-tag.lost-item { background:#fff3e0; color:#e65100; border-color:#ffcc80; }
.pb-expand-hint { font-size:10px; color:#bbb; margin-left:6px; }
"""
html = html.replace('</style>', CSS + '\n</style>', 1)

# ── 2. Embed PRODUCT_HISTORY const ─────────────────────────────────────────────
ph_json = json.dumps(PH, ensure_ascii=False)
PH_CONST = f'const PRODUCT_HISTORY = {ph_json};\n'

# Insert after COHORT_2025 const
marker = 'const COHORT_2025 = '
idx = html.index(marker)
line_end = html.index('\n', idx) + 1
html = html[:line_end] + PH_CONST + html[line_end:]
print('Injected PRODUCT_HISTORY const')

# ── 3. Replace renderPurchaseBehavior function with expanded version ────────────
OLD_RENDER_START = 'function renderPurchaseBehavior() {'
OLD_RENDER_END   = "// Init\nif (document.readyState === 'loading') {"

# Find and extract the old function
start_idx = html.index(OLD_RENDER_START)
end_idx   = html.index(OLD_RENDER_END)

NEW_RENDER = r"""function togglePbDetail(name) {
  const detailId = 'pb-detail-' + name.replace(/[^a-zA-Z0-9一-鿿]/g, '_');
  const existing = document.getElementById(detailId);
  if (existing) { existing.remove(); return; }

  const hist = PRODUCT_HISTORY[name] || {};
  const PB_YEARS_SHOWN = ['2022','2023','2024','2025'];

  let gridCols = '';
  PB_YEARS_SHOWN.forEach(yr => {
    const items = hist[yr];
    if (!items || items.length === 0) return;
    // Compare with adjacent year to highlight new/lost
    const prevYr = PB_YEARS_SHOWN[PB_YEARS_SHOWN.indexOf(yr) - 1];
    const prevItems = prevYr ? (hist[prevYr] || []) : [];
    const tags = items.map(it => {
      const isNew  = prevItems.length > 0 && !prevItems.includes(it) ? ' new-item' : '';
      return `<span class="pb-item-tag${isNew}">${it}</span>`;
    }).join('');
    gridCols += `<div class="pb-detail-yr">
      <div class="pb-detail-yr-hdr">${yr}</div>
      ${tags}
    </div>`;
  });

  if (!gridCols) gridCols = '<span style="color:#ccc;font-size:11px">無品項資料</span>';

  const tr = document.createElement('tr');
  tr.id = detailId;
  tr.className = 'pb-detail-row';
  tr.innerHTML = `<td colspan="8"><div class="pb-detail-grid">${gridCols}</div></td>`;

  // Insert after the clicked row
  const tbody = document.getElementById('pb-tbody');
  const rows = Array.from(tbody.querySelectorAll('tr.pb-data-row'));
  const clickedRow = rows.find(r => r.dataset.name === name);
  if (clickedRow && clickedRow.nextSibling) {
    tbody.insertBefore(tr, clickedRow.nextSibling);
  } else if (clickedRow) {
    tbody.appendChild(tr);
  }
}

function renderPurchaseBehavior() {
  const donors = Object.values(PB_DATA);

  function isTier(d)   { return Object.values(d.years).some(v => v.cat === 'TIER'); }
  function isSingle(d) { return Object.values(d.years).some(v => v.cat === 'SINGLE'); }
  function isSwitcher(d) { return isTier(d) && isSingle(d); }

  let filtered = donors;
  if (_pbFilter === 'tier')   filtered = donors.filter(isTier);
  if (_pbFilter === 'single') filtered = donors.filter(isSingle);
  if (_pbFilter === 'switch') filtered = donors.filter(isSwitcher);

  // Stats
  const tierCount   = donors.filter(isTier).length;
  const singleCount = donors.filter(isSingle).length;
  const swCount     = donors.filter(isSwitcher).length;
  document.getElementById('pb-stats').innerHTML = `
    <div class="pb-stat"><div class="pb-stat-num">${filtered.length}</div><div class="pb-stat-lbl">顯示廠商數</div></div>
    <div class="pb-stat tier-color"><div class="pb-stat-num">${tierCount}</div><div class="pb-stat-lbl">有級別贊助</div></div>
    <div class="pb-stat single-color"><div class="pb-stat-num">${singleCount}</div><div class="pb-stat-lbl">有單購紀錄</div></div>
    <div class="pb-stat switch-color"><div class="pb-stat-num">${swCount}</div><div class="pb-stat-lbl">曾切換行為</div></div>
  `;

  // Table rows
  let tbody = '';
  filtered.forEach(d => {
    const sw = isSwitcher(d) ? ' style="background:rgba(139,92,246,.04)"' : '';
    const cells = PB_YEARS.map(yr => pbChip(d.years[yr])).join('');
    const yrsCount = Object.keys(d.years).length;
    const hasDetail = !!PRODUCT_HISTORY[d.name];
    const hint = hasDetail ? '<span class="pb-expand-hint">▸ 品項</span>' : '';
    tbody += `<tr class="pb-data-row"${sw} data-name="${d.name.replace(/"/g,'&quot;')}" onclick="togglePbDetail('${d.name.replace(/'/g,"\\'")}')">
      <td class="name-col">${d.name}${hint}</td>${cells}
      <td style="text-align:center;color:#888;font-size:12px">${yrsCount}</td>
    </tr>`;
  });
  document.getElementById('pb-tbody').innerHTML = tbody || '<tr><td colspan="8" style="text-align:center;color:#999;padding:20px">無符合資料</td></tr>';

  // Switcher analysis
  const switcherDonors = donors.filter(isSwitcher);
  const YR_LIST = PB_YEARS.map(Number);
  let t2s = [], s2t = [], t2out = [], s2out = [];
  switcherDonors.forEach(d => {
    const yrs = Object.keys(d.years).map(Number).sort((a,b)=>a-b);
    for (let i = 0; i < yrs.length - 1; i++) {
      const a = String(yrs[i]), b = String(yrs[i+1]);
      const catA = d.years[a]?.cat, catB = d.years[b]?.cat;
      if (catA === 'TIER'   && catB === 'SINGLE') t2s.push(d.name);
      if (catA === 'SINGLE' && catB === 'TIER')   s2t.push(d.name);
    }
    const lastYr = String(Math.max(...yrs));
    if (d.years[lastYr]?.cat === 'TIER'   && lastYr !== '2025') t2out.push(d.name);
    if (d.years[lastYr]?.cat === 'SINGLE' && lastYr !== '2025') s2out.push(d.name);
  });

  function switchCard(label, names, color) {
    const nameStr = names.length ? names.slice(0,5).join('、') + (names.length > 5 ? ` 等${names.length}家` : '') : '—';
    return `<div class="pb-switch-item">
      <div class="pb-switch-label">${label}</div>
      <div class="pb-switch-val" style="color:${color}">${names.length}</div>
      <div class="pb-switch-names">${nameStr}</div>
    </div>`;
  }

  document.getElementById('pb-switcher').innerHTML = `
    <h4>切換行為統計（${switcherDonors.length} 家切換廠商）</h4>
    <div class="pb-switch-grid">
      ${switchCard('級別 → 單購（降購）', t2s, '#c0392b')}
      ${switchCard('單購 → 級別（升購）', s2t, '#2c4baa')}
      ${switchCard('末年為級別後流失', t2out, '#888')}
      ${switchCard('末年為單購後流失', s2out, '#888')}
    </div>
  `;
}

"""

html = html[:start_idx] + NEW_RENDER + html[end_idx:]
print('Replaced renderPurchaseBehavior with expandable version')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open('index.html') as f:
    final = f.read()
print('PRODUCT_HISTORY in html:', 'PRODUCT_HISTORY' in final)
print('togglePbDetail in html:', 'togglePbDetail' in final)
print('pb-detail-row in html:', 'pb-detail-row' in final)
print('Total lines:', final.count('\n'))
