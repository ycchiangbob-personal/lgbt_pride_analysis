#!/usr/bin/env python3
"""Inject 遊行隊伍 tab into index.html"""
import json, re

with open("parade_groups.json", encoding="utf-8") as f:
    GROUPS = json.load(f)

with open("index.html", encoding="utf-8") as f:
    html = f.read()

# ── 1. CSS ────────────────────────────────────────────────────────────────────
CSS = """
/* ── Parade Groups tab ── */
.grp-yr-row { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
.grp-yr-btn { padding:4px 13px; border-radius:20px; border:1px solid var(--border);
  background:var(--bg2); cursor:pointer; font-size:13px; color:var(--text); }
.grp-yr-btn.active { background:#2d2d2d; color:#fff; border-color:#2d2d2d; }
.grp-sec-row { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:12px; }
.grp-sec-btn { padding:3px 12px; border-radius:20px; border:1px solid var(--border);
  background:var(--bg2); cursor:pointer; font-size:12px; color:var(--text); }
.grp-sec-btn.active { background:#555; color:#fff; border-color:#555; }
.grp-sec-btn[data-sec="商業車"].active { background:#c0392b; border-color:#c0392b; }
.grp-sec-btn[data-sec="社團車"].active { background:#2c4baa; border-color:#2c4baa; }
.grp-sec-btn[data-sec="隊伍"].active   { background:#2E9B55; border-color:#2E9B55; }
.grp-stats { font-size:12px; color:#888; margin-bottom:14px; }
.grp-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:14px; }
.grp-color-card { border:1px solid var(--border); border-radius:8px; overflow:hidden; background:var(--bg2); }
.grp-color-hdr { padding:9px 14px; font-weight:600; font-size:14px;
  display:flex; align-items:center; gap:8px; border-bottom:1px solid var(--border); }
.grp-color-dot { width:12px; height:12px; border-radius:50%; flex-shrink:0; }
.grp-row { padding:7px 14px; }
.grp-row + .grp-row { border-top:1px solid var(--border); }
.grp-row-label { font-size:10px; font-weight:700; letter-spacing:.05em;
  text-transform:uppercase; color:#999; margin-bottom:5px; }
.grp-chips { display:flex; flex-wrap:wrap; gap:4px; }
.grp-chip { font-size:11px; padding:2px 8px; border-radius:11px; line-height:1.5; }
.grp-chip-com  { background:#fff0f2; color:#b52a3e; border:1px solid #ffc8d0; }
.grp-chip-ngo  { background:#eef2ff; color:#2c4baa; border:1px solid #c5d0f5; }
.grp-chip-team { background:#f2f8f4; color:#1f6e3a; border:1px solid #b8dfc7; }
.grp-chip-2021 { background:#f5f5f5; color:#444; border:1px solid #ddd; }
.grp-more-btn { font-size:11px; color:#888; cursor:pointer; margin-top:4px;
  padding:1px 6px; border:1px solid #ddd; border-radius:10px; background:none;
  line-height:1.6; white-space:nowrap; }
.grp-more-btn:hover { background:#f5f5f5; }
.grp-2021-wrap { padding:10px 14px; }
.grp-2021-title { font-size:12px; color:#888; margin-bottom:8px; }
"""

html = html.replace("</style>", CSS + "\n</style>", 1)

# ── 2. Tab button ─────────────────────────────────────────────────────────────
html = html.replace(
    '<button class="tab-btn" onclick="showTab(\'participants\', this)">遊行參與者</button>',
    '<button class="tab-btn" onclick="showTab(\'participants\', this)">遊行參與者</button>\n'
    '      <button class="tab-btn" onclick="showTab(\'groups\', this)">遊行隊伍</button>'
)

# ── 3. Panel HTML ──────────────────────────────────────────────────────────────
YEAR_BTNS = "\n          ".join(
    f'<button class="grp-yr-btn" data-yr="{y}" onclick="setGrpYear({y},this)">{y}</button>'
    for y in [2019,2020,2021,2022,2023,2024,2025]
)

PANEL_HTML = f"""
  <div class="tab-panel" id="panel-groups">
    <div class="section-card">
      <div class="grp-yr-row">
          {YEAR_BTNS}
      </div>
      <div class="grp-sec-row">
        <button class="grp-sec-btn active" data-sec="all"  onclick="setGrpSec('all',this)">全部</button>
        <button class="grp-sec-btn" data-sec="商業車" onclick="setGrpSec('商業車',this)">商業車</button>
        <button class="grp-sec-btn" data-sec="社團車" onclick="setGrpSec('社團車',this)">社團車</button>
        <button class="grp-sec-btn" data-sec="隊伍"   onclick="setGrpSec('隊伍',this)">隊伍</button>
      </div>
      <div class="grp-stats" id="grp-stats"></div>
      <div class="grp-grid" id="grp-content"></div>
    </div>
  </div>
"""

# Insert before </body>
html = html.replace("</body>", PANEL_HTML + "\n</body>", 1)

# ── 4. showTab hook ────────────────────────────────────────────────────────────
html = html.replace(
    "if (id === 'participants') {",
    "if (id === 'groups') {\n"
    "    try { renderGroups(); } catch(e) { console.error('renderGroups error:', e); }\n"
    "  }\n"
    "  if (id === 'participants') {"
)

# ── 5. Script block with GROUPS_DATA ──────────────────────────────────────────
COLOR_CSS = {
    "紅色":"#e8445a","橙色":"#f07030","黃色":"#c8960c",
    "綠色":"#2E9B55","藍色":"#4472C4","紫色":"#8B5CF6"
}

groups_json = json.dumps(GROUPS, ensure_ascii=False)

SCRIPT = f"""
<script>
// ── Parade Groups tab ──────────────────────────────────────────────────────
const GROUPS_DATA = {groups_json};

const GRP_COLOR_CSS = {json.dumps(COLOR_CSS, ensure_ascii=False)};

let _grpYear = 2025;
let _grpSec  = 'all';

function setGrpYear(y, btn) {{
  _grpYear = y;
  document.querySelectorAll('.grp-yr-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderGroups();
}}

function setGrpSec(s, btn) {{
  _grpSec = s;
  document.querySelectorAll('.grp-sec-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderGroups();
}}

function grpChips(names, cls, limit) {{
  if (!names || names.length === 0) return '<span style="color:#ccc;font-size:11px">—</span>';
  const show = (limit && names.length > limit) ? names.slice(0, limit) : names;
  const hidden = (limit && names.length > limit) ? names.slice(limit) : [];
  const uid = 'grp' + Math.random().toString(36).slice(2);
  let h = show.map(n => `<span class="grp-chip ${{cls}}">${{n}}</span>`).join('');
  if (hidden.length) {{
    h += `<span id="${{uid}}-more" class="grp-chips" style="display:none">${{
      hidden.map(n=>`<span class="grp-chip ${{cls}}">${{n}}</span>`).join('')
    }}</span>`;
    h += `<button class="grp-more-btn" onclick="
      document.getElementById('${{uid}}-more').style.display='inline-flex';
      document.getElementById('${{uid}}-more').style.flexWrap='wrap';
      document.getElementById('${{uid}}-more').style.gap='4px';
      this.style.display='none'
    ">+${{hidden.length}} 顯示全部</button>`;
  }}
  return h;
}}

function buildColorCard(color, sections) {{
  const css = GRP_COLOR_CSS[color] || '#888';
  let body = '';
  const showCom  = _grpSec === 'all' || _grpSec === '商業車';
  const showNgo  = _grpSec === 'all' || _grpSec === '社團車';
  const showTeam = _grpSec === 'all' || _grpSec === '隊伍';

  if (showCom) {{
    body += `<div class="grp-row">
      <div class="grp-row-label">商業車 ${{(sections['商業車']||[]).length}}</div>
      <div class="grp-chips">${{grpChips(sections['商業車'],'grp-chip-com', null)}}</div>
    </div>`;
  }}
  if (showNgo) {{
    body += `<div class="grp-row">
      <div class="grp-row-label">社團車 ${{(sections['社團車']||[]).length}}</div>
      <div class="grp-chips">${{grpChips(sections['社團車'],'grp-chip-ngo', null)}}</div>
    </div>`;
  }}
  if (showTeam) {{
    body += `<div class="grp-row">
      <div class="grp-row-label">隊伍 ${{(sections['隊伍']||[]).length}}</div>
      <div class="grp-chips">${{grpChips(sections['隊伍'],'grp-chip-team', 10)}}</div>
    </div>`;
  }}

  return `<div class="grp-color-card">
    <div class="grp-color-hdr">
      <span class="grp-color-dot" style="background:${{css}}"></span>
      ${{color}}大隊
    </div>
    ${{body}}
  </div>`;
}}

function renderGroups() {{
  const yr  = _grpYear;
  const yrData = GROUPS_DATA[String(yr)];

  // Sync year buttons
  document.querySelectorAll('.grp-yr-btn').forEach(b => {{
    b.classList.toggle('active', parseInt(b.dataset.yr) === yr);
  }});

  const statsEl   = document.getElementById('grp-stats');
  const contentEl = document.getElementById('grp-content');
  if (!yrData) {{ contentEl.innerHTML = ''; return; }}

  // 2021 special
  if (yrData.all) {{
    const all = yrData.all['全體參與'] || [];
    statsEl.textContent = `${{yr}} 年  共 ${{all.length}} 個參與團體（未區分大隊）`;
    contentEl.innerHTML = `<div class="grp-2021-wrap">
      <div class="grp-2021-title">所有參與團體</div>
      <div class="grp-chips">${{grpChips(all,'grp-chip-2021', 20)}}</div>
    </div>`;
    return;
  }}

  // Normal years
  let comTotal=0, ngoTotal=0, teamTotal=0;
  Object.values(yrData).forEach(s => {{
    comTotal  += (s['商業車']||[]).length;
    ngoTotal  += (s['社團車']||[]).length;
    teamTotal += (s['隊伍']||[]).length;
  }});
  statsEl.textContent = `${{yr}} 年  ${{Object.keys(yrData).length}} 個大隊 ｜ 商業車 ${{comTotal}} 組 ｜ 社團車 ${{ngoTotal}} 組 ｜ 隊伍 ${{teamTotal}} 組`;

  const COLORS = ["紅色","橙色","黃色","綠色","藍色","紫色"];
  let html = '';
  COLORS.forEach(color => {{
    const s = yrData[color];
    if (!s) return;
    // Skip if filter doesn't match
    if (_grpSec === '商業車' && (s['商業車']||[]).length===0) return;
    if (_grpSec === '社團車' && (s['社團車']||[]).length===0) return;
    if (_grpSec === '隊伍'   && (s['隊伍']  ||[]).length===0) return;
    html += buildColorCard(color, s);
  }});

  contentEl.innerHTML = html || '<p style="color:#999">無符合資料</p>';
}}

// Init
if (document.readyState === 'loading') {{
  document.addEventListener('DOMContentLoaded', () => {{ try {{ renderGroups(); }} catch(e) {{}} }});
}} else {{
  try {{ renderGroups(); }} catch(e) {{}}
}}
</script>
"""

# Append before </body>
html = html.replace("</body>", SCRIPT + "\n</body>", 1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# Quick check
import subprocess
result = subprocess.run(
    ["grep", "-n", "<script\|</script>", "index.html"],
    capture_output=True, text=True
)
print(result.stdout)
print("Done. Lines:", html.count("\n"))
