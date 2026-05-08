#!/usr/bin/env python3
"""Inject 採購行為分析 tab into index.html (replaces panel-analysis-c)"""
import json, re

with open('purchase_behavior.json', encoding='utf-8') as f:
    PB_DATA = json.load(f)

with open('index.html', encoding='utf-8') as f:
    html = f.read()

# ── 1. Rename nav button ──────────────────────────────────────────────────────
html = html.replace(
    '<button class="tab-btn" onclick="showTab(\'analysis-c\', this)">級別異動</button>',
    '<button class="tab-btn" onclick="showTab(\'analysis-c\', this)">採購行為</button>'
)

# ── 2. CSS ────────────────────────────────────────────────────────────────────
CSS = """
/* ── Purchase Behavior tab ── */
.pb-filter-row { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:14px; }
.pb-filter-btn { padding:4px 14px; border-radius:20px; border:1px solid var(--border);
  background:var(--bg2); cursor:pointer; font-size:13px; color:var(--text); }
.pb-filter-btn.active { background:#2d2d2d; color:#fff; border-color:#2d2d2d; }
.pb-stats-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:18px; }
.pb-stat { border:1px solid var(--border); border-radius:8px; padding:10px 18px;
  background:var(--bg2); text-align:center; min-width:90px; }
.pb-stat-num { font-size:22px; font-weight:700; }
.pb-stat-lbl { font-size:11px; color:#888; margin-top:2px; }
.pb-stat.tier-color  .pb-stat-num { color:#2c4baa; }
.pb-stat.single-color .pb-stat-num { color:#c0392b; }
.pb-stat.switch-color .pb-stat-num { color:#7b3f9e; }
.pb-table-wrap { overflow-x:auto; margin-bottom:18px; }
.pb-table { border-collapse:collapse; width:100%; font-size:13px; }
.pb-table th { padding:6px 10px; text-align:center; border-bottom:2px solid var(--border);
  white-space:nowrap; color:#888; font-weight:600; font-size:12px; }
.pb-table th.name-col { text-align:left; }
.pb-table td { padding:5px 8px; border-bottom:1px solid var(--border); vertical-align:middle; }
.pb-table td.name-col { white-space:nowrap; font-size:13px; }
.pb-table tr:hover { background:rgba(0,0,0,.03); }
.pb-chip { display:inline-block; padding:2px 7px; border-radius:10px;
  font-size:10px; font-weight:600; white-space:nowrap; line-height:1.6; }
.pb-chip-tier   { background:#eef2ff; color:#2c4baa; border:1px solid #c5d0f5; }
.pb-chip-single { background:#fff0f2; color:#b52a3e; border:1px solid #ffc8d0; }
.pb-chip-market { background:#f2f8f4; color:#1f6e3a; border:1px solid #b8dfc7; }
.pb-chip-other  { background:#f5f5f5; color:#777; border:1px solid #ddd; }
.pb-switcher-box { border:1px solid var(--border); border-radius:8px; padding:14px 18px;
  background:var(--bg2); margin-top:6px; }
.pb-switcher-box h4 { margin:0 0 12px 0; font-size:14px; color:#555; }
.pb-switch-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:10px; }
.pb-switch-item { border:1px solid var(--border); border-radius:6px; padding:8px 12px; background:#fff; }
.pb-switch-label { font-size:11px; color:#888; margin-bottom:4px; }
.pb-switch-val { font-size:18px; font-weight:700; }
.pb-switch-names { font-size:10px; color:#aaa; margin-top:3px; line-height:1.5; }
"""
html = html.replace('</style>', CSS + '\n</style>', 1)

# ── 3. Replace panel-analysis-c content ──────────────────────────────────────
YEARS = ['2019', '2020', '2022', '2023', '2024', '2025']

pb_json = json.dumps(PB_DATA, ensure_ascii=False)

PANEL_INNER = f"""
  <!-- Section: Analysis C (reworked) -->
  <div class="section-title">採購行為分析 2019–2025</div>
  <div class="chart-card">
    <p class="plain-desc">
      各廠商在 2019–2025 年間實際採購品項（級別贊助 / 單購花車 / 彩虹市集）。
      可篩選特定族群，並觀察廠商是否有在「級別贊助」與「單購」之間切換。2021 年因 COVID-19 縮小辦理，無分類資料，故不納入。
    </p>
    <div class="pb-filter-row">
      <button class="pb-filter-btn active" data-f="all"     onclick="setPbFilter('all',this)">全部</button>
      <button class="pb-filter-btn"         data-f="tier"   onclick="setPbFilter('tier',this)">級別贊助者</button>
      <button class="pb-filter-btn"         data-f="single" onclick="setPbFilter('single',this)">單購者</button>
      <button class="pb-filter-btn"         data-f="switch" onclick="setPbFilter('switch',this)">曾切換行為</button>
    </div>
    <div class="pb-stats-row" id="pb-stats"></div>
    <div class="pb-table-wrap">
      <table class="pb-table">
        <thead>
          <tr>
            <th class="name-col">廠商</th>
            {''.join(f'<th>{y}</th>' for y in YEARS)}
            <th>出現年數</th>
          </tr>
        </thead>
        <tbody id="pb-tbody"></tbody>
      </table>
    </div>
    <div class="pb-switcher-box" id="pb-switcher"></div>
  </div>
"""

# Replace everything inside panel-analysis-c
old_panel = re.search(
    r'(<div class="tab-panel" id="panel-analysis-c">)(.*?)(</div><!-- /panel-analysis-c -->)',
    html, re.DOTALL
)
if old_panel:
    html = html[:old_panel.start()] + \
           f'<div class="tab-panel" id="panel-analysis-c">\n{PANEL_INNER}\n  </div><!-- /panel-analysis-c -->' + \
           html[old_panel.end():]
    print('Replaced panel-analysis-c content')
else:
    print('ERROR: panel-analysis-c not found')

# ── 4. showTab hook ────────────────────────────────────────────────────────────
# Fix duplicate 'groups' check and add analysis-c hook
old_hook = (
    "  if (id === 'groups') {\n"
    "    try { renderGroups(); } catch(e) { console.error('renderGroups error:', e); }\n"
    "  }\n"
    "  if (id === 'groups') {\n"
    "    try { renderGroups(); } catch(e) { console.error('renderGroups error:', e); }\n"
    "  }\n"
    "  if (id === 'participants') {\n"
    "    try { renderParticipants(); } catch(e) { console.error('renderParticipants error:', e); }\n"
    "  }"
)
new_hook = (
    "  if (id === 'groups') {\n"
    "    try { renderGroups(); } catch(e) { console.error('renderGroups error:', e); }\n"
    "  }\n"
    "  if (id === 'analysis-c') {\n"
    "    try { renderPurchaseBehavior(); } catch(e) { console.error('renderPurchaseBehavior error:', e); }\n"
    "  }\n"
    "  if (id === 'participants') {\n"
    "    try { renderParticipants(); } catch(e) { console.error('renderParticipants error:', e); }\n"
    "  }"
)
if old_hook in html:
    html = html.replace(old_hook, new_hook)
    print('Updated showTab hook (fixed duplicate groups + added analysis-c)')
else:
    # Fallback: just add analysis-c before participants
    fallback_old = (
        "  if (id === 'participants') {\n"
        "    try { renderParticipants(); } catch(e) { console.error('renderParticipants error:', e); }\n"
        "  }"
    )
    fallback_new = (
        "  if (id === 'analysis-c') {\n"
        "    try { renderPurchaseBehavior(); } catch(e) { console.error('renderPurchaseBehavior error:', e); }\n"
        "  }\n"
        "  if (id === 'participants') {\n"
        "    try { renderParticipants(); } catch(e) { console.error('renderParticipants error:', e); }\n"
        "  }"
    )
    if fallback_old in html:
        html = html.replace(fallback_old, fallback_new)
        print('Updated showTab hook (fallback: added analysis-c)')
    else:
        print('WARNING: showTab hook pattern not found')

# ── 5. New script block ────────────────────────────────────────────────────────
SCRIPT = f"""
<script>
// ── Purchase Behavior tab ─────────────────────────────────────────────────────
const PB_DATA = {pb_json};
const PB_YEARS = {json.dumps(YEARS)};

let _pbFilter = 'all';

function setPbFilter(f, btn) {{
  _pbFilter = f;
  document.querySelectorAll('.pb-filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderPurchaseBehavior();
}}

function pbChip(yearEntry) {{
  if (!yearEntry) return '<td></td>';
  const cls = {{TIER:'pb-chip-tier', SINGLE:'pb-chip-single', MARKET:'pb-chip-market', OTHER:'pb-chip-other'}}[yearEntry.cat] || 'pb-chip-other';
  return `<td style="text-align:center"><span class="pb-chip ${{cls}}">${{yearEntry.label}}</span></td>`;
}}

function renderPurchaseBehavior() {{
  const donors = Object.values(PB_DATA);

  function isTier(d)   {{ return Object.values(d.years).some(v => v.cat === 'TIER'); }}
  function isSingle(d) {{ return Object.values(d.years).some(v => v.cat === 'SINGLE'); }}
  function isSwitcher(d) {{ return isTier(d) && isSingle(d); }}

  let filtered = donors;
  if (_pbFilter === 'tier')   filtered = donors.filter(isTier);
  if (_pbFilter === 'single') filtered = donors.filter(isSingle);
  if (_pbFilter === 'switch') filtered = donors.filter(isSwitcher);

  // Stats
  const tierCount   = donors.filter(isTier).length;
  const singleCount = donors.filter(isSingle).length;
  const swCount     = donors.filter(isSwitcher).length;
  document.getElementById('pb-stats').innerHTML = `
    <div class="pb-stat"><div class="pb-stat-num">${{filtered.length}}</div><div class="pb-stat-lbl">顯示廠商數</div></div>
    <div class="pb-stat tier-color"><div class="pb-stat-num">${{tierCount}}</div><div class="pb-stat-lbl">有級別贊助</div></div>
    <div class="pb-stat single-color"><div class="pb-stat-num">${{singleCount}}</div><div class="pb-stat-lbl">有單購紀錄</div></div>
    <div class="pb-stat switch-color"><div class="pb-stat-num">${{swCount}}</div><div class="pb-stat-lbl">曾切換行為</div></div>
  `;

  // Table rows
  let tbody = '';
  filtered.forEach(d => {{
    const sw = isSwitcher(d) ? ' style="background:rgba(139,92,246,.04)"' : '';
    const cells = PB_YEARS.map(yr => pbChip(d.years[yr])).join('');
    const yrsCount = Object.keys(d.years).length;
    tbody += `<tr${{sw}}><td class="name-col">${{d.name}}</td>${{cells}}<td style="text-align:center;color:#888;font-size:12px">${{yrsCount}}</td></tr>`;
  }});
  document.getElementById('pb-tbody').innerHTML = tbody || '<tr><td colspan="8" style="text-align:center;color:#999;padding:20px">無符合資料</td></tr>';

  // Switcher analysis
  const switcherDonors = donors.filter(isSwitcher);

  // Count transitions across consecutive year pairs
  const YR_LIST = PB_YEARS.map(Number);
  let t2s = [], s2t = [], t2out = [], s2out = [];

  switcherDonors.forEach(d => {{
    const yrs = Object.keys(d.years).map(Number).sort((a,b)=>a-b);
    for (let i = 0; i < yrs.length - 1; i++) {{
      // Only consecutive tracked years
      const a = String(yrs[i]), b = String(yrs[i+1]);
      const catA = d.years[a]?.cat, catB = d.years[b]?.cat;
      if (catA === 'TIER'   && catB === 'SINGLE') t2s.push(d.name);
      if (catA === 'SINGLE' && catB === 'TIER')   s2t.push(d.name);
    }}
    // Check exit after TIER or SINGLE
    const lastYr = String(Math.max(...yrs));
    if (d.years[lastYr]?.cat === 'TIER'   && lastYr !== '2025') t2out.push(d.name);
    if (d.years[lastYr]?.cat === 'SINGLE' && lastYr !== '2025') s2out.push(d.name);
  }});

  function switchCard(label, names, color) {{
    const nameStr = names.length ? names.slice(0,5).join('、') + (names.length > 5 ? ` 等${{names.length}}家` : '') : '—';
    return `<div class="pb-switch-item">
      <div class="pb-switch-label">${{label}}</div>
      <div class="pb-switch-val" style="color:${{color}}">${{names.length}}</div>
      <div class="pb-switch-names">${{nameStr}}</div>
    </div>`;
  }}

  document.getElementById('pb-switcher').innerHTML = `
    <h4>切換行為統計（12 家切換廠商）</h4>
    <div class="pb-switch-grid">
      ${{switchCard('級別 → 單購（降購）', t2s, '#c0392b')}}
      ${{switchCard('單購 → 級別（升購）', s2t, '#2c4baa')}}
      ${{switchCard('末年為級別後流失', t2out, '#888')}}
      ${{switchCard('末年為單購後流失', s2out, '#888')}}
    </div>
  `;
}}

// Init
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', () => {{ try {{ renderPurchaseBehavior(); }} catch(e) {{}} }});
}} else {{
  try {{ renderPurchaseBehavior(); }} catch(e) {{}}
}}
</script>
"""

html = html.replace('</body>', SCRIPT + '\n</body>', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Total lines:', html.count('\n'))
print('Verify: nav button renamed:', '採購行為' in html)
print('Verify: panel updated:', 'pb-filter-row' in html)
print('Verify: script added:', 'PB_DATA' in html)
