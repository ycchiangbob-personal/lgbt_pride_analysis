#!/usr/bin/env python3
"""Append 2025 cohort sections to panel-analysis-c in index.html"""
import json

with open('cohort_2025.json', encoding='utf-8') as f:
    COHORT = json.load(f)

with open('index.html', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS ─────────────────────────────────────────────────────────────────────
CSS = """
/* ── Cohort 2025 sections ── */
.co-section-title { font-size:13px; font-weight:700; color:#555; margin:18px 0 10px 0;
  padding-bottom:6px; border-bottom:1px solid var(--border); }
.co-cat-row { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px; }
.co-cat-block { border:1px solid var(--border); border-radius:8px; padding:10px 14px;
  background:var(--bg2); flex:1; min-width:150px; }
.co-cat-hdr { font-size:11px; font-weight:700; text-transform:uppercase;
  letter-spacing:.05em; color:#999; margin-bottom:8px; }
.co-cat-hdr.tier   { color:#2c4baa; }
.co-cat-hdr.single { color:#b52a3e; }
.co-cat-hdr.market { color:#1f6e3a; }
.co-cat-hdr.other  { color:#888; }
.co-chips { display:flex; flex-wrap:wrap; gap:4px; }
.co-chip { font-size:11px; padding:2px 8px; border-radius:10px; line-height:1.6; }
.co-chip-tier   { background:#eef2ff; color:#2c4baa; border:1px solid #c5d0f5; }
.co-chip-single { background:#fff0f2; color:#b52a3e; border:1px solid #ffc8d0; }
.co-chip-market { background:#f2f8f4; color:#1f6e3a; border:1px solid #b8dfc7; }
.co-chip-other  { background:#f5f5f5; color:#777;    border:1px solid #ddd; }
.co-ret-table { width:100%; border-collapse:collapse; font-size:13px; }
.co-ret-table th { padding:6px 10px; text-align:left; border-bottom:2px solid var(--border);
  font-size:12px; color:#888; font-weight:600; }
.co-ret-table td { padding:6px 10px; border-bottom:1px solid var(--border); vertical-align:middle; }
.co-ret-table tr:hover { background:rgba(0,0,0,.03); }
.co-change-badge { display:inline-block; padding:1px 8px; border-radius:10px;
  font-size:10px; font-weight:700; white-space:nowrap; }
.co-badge-same      { background:#f0f0f0; color:#666; }
.co-badge-upgrade   { background:#eef2ff; color:#2c4baa; }
.co-badge-downgrade { background:#fff0f2; color:#b52a3e; }
.co-badge-other     { background:#fff9e6; color:#a06020; }
.co-summary-pills { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
.co-summary-pill { padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; }
"""
html = html.replace('</style>', CSS + '\n</style>', 1)

# ── 2. Build new card HTML ─────────────────────────────────────────────────────
new_2025     = COHORT['new_2025']
returning    = COHORT['returning_2025']
same_list    = [r for r in returning if r['change_type'] == 'same']
upgrade_list = [r for r in returning if r['change_type'] == 'upgrade']
downgrade_list=[r for r in returning if r['change_type'] == 'downgrade']
other_list   = [r for r in returning if r['change_type'] == 'other']

CAT_CSS = {'TIER':'tier','SINGLE':'single','MARKET':'market','OTHER':'other'}
CHIP_CSS = {'TIER':'co-chip-tier','SINGLE':'co-chip-single','MARKET':'co-chip-market','OTHER':'co-chip-other'}

def new_chip(r):
    cls = CHIP_CSS.get(r['cat'], 'co-chip-other')
    amt = f"NT${r['amount']:,}" if r['amount'] else ''
    lbl = r['label']
    name = r['name']
    return f'<span class="{cls} co-chip" title="{lbl} {amt}">{name}</span>'

# Group new entrants by category
from collections import defaultdict
cat_groups = defaultdict(list)
for r in new_2025:
    if r['cat'] not in ('HOTEL',):
        cat_groups[r['cat']].append(r)

cat_order = ['TIER','SINGLE','MARKET','OTHER']
cat_label = {'TIER':'級別贊助','SINGLE':'單購花車','MARKET':'彩虹市集','OTHER':'其他'}

new_cat_html = ''
for cat in cat_order:
    recs = cat_groups.get(cat, [])
    if not recs: continue
    cls = CAT_CSS[cat]
    chips = ''.join(new_chip(r) for r in recs)
    new_cat_html += f'''<div class="co-cat-block">
      <div class="co-cat-hdr {cls}">{cat_label[cat]} ({len(recs)})</div>
      <div class="co-chips">{chips}</div>
    </div>'''

# Returning buyer table rows
def change_badge(change_type):
    MAP = {
        'same':      ('<span class="co-change-badge co-badge-same">維持</span>', ''),
        'upgrade':   ('<span class="co-change-badge co-badge-upgrade">↑ 升購</span>', 'rgba(44,75,170,.05)'),
        'downgrade': ('<span class="co-change-badge co-badge-downgrade">↓ 降購</span>', 'rgba(181,42,62,.05)'),
        'other':     ('<span class="co-change-badge co-badge-other">轉換</span>', 'rgba(160,96,32,.05)'),
    }
    return MAP.get(change_type, ('', ''))

CHIP_SHORT = {
    'TIER': lambda lbl: f'<span class="co-chip co-chip-tier">{lbl}</span>',
    'SINGLE': lambda lbl: f'<span class="co-chip co-chip-single">{lbl}</span>',
    'MARKET': lambda lbl: f'<span class="co-chip co-chip-market">{lbl}</span>',
    'OTHER':  lambda lbl: f'<span class="co-chip co-chip-other">{lbl}</span>',
}
def make_chip(cat, lbl):
    fn = CHIP_SHORT.get(cat, CHIP_SHORT['OTHER'])
    return fn(lbl)

ret_rows = ''
# Upgrades first, then same, then downgrades, then other
for r in upgrade_list + same_list + downgrade_list + other_list:
    badge, bg = change_badge(r['change_type'])
    style = f' style="background:{bg}"' if bg else ''
    prev_chip = make_chip(r['prev_cat'], r['prev_label'])
    curr_chip = make_chip(r['curr_cat'], r['curr_label'])
    amt = f"NT${r['curr_amount']:,}" if r['curr_amount'] else '—'
    ret_rows += f'<tr{style}><td>{r["name"]}</td><td style="color:#aaa;font-size:12px">{r["prev_yr"]}</td><td>{prev_chip}</td><td>{curr_chip}</td><td style="text-align:right;font-size:12px;color:#555">{amt}</td><td>{badge}</td></tr>'

summary_pills = (
    f'<span class="co-summary-pill" style="background:#f0f0f0;color:#555">維持 {len(same_list)} 家</span>'
    f'<span class="co-summary-pill" style="background:#eef2ff;color:#2c4baa">↑ 升購 {len(upgrade_list)} 家</span>'
    f'<span class="co-summary-pill" style="background:#fff0f2;color:#b52a3e">↓ 降購 {len(downgrade_list)} 家</span>'
)
if other_list:
    summary_pills += f'<span class="co-summary-pill" style="background:#fff9e6;color:#a06020">轉換 {len(other_list)} 家</span>'

NEW_CARDS = f"""
    <div class="co-section-title">2025 首次購買廠商（{len(new_2025)} 家）</div>
    <div class="co-cat-row">
      {new_cat_html}
    </div>
    <div class="co-section-title">2025 回訪廠商購買延續性（{len(returning)} 家）</div>
    <div class="co-summary-pills">
      {summary_pills}
    </div>
    <div style="overflow-x:auto">
      <table class="co-ret-table">
        <thead><tr>
          <th>廠商</th><th>前次年份</th><th>前次採購</th><th>2025 採購</th><th style="text-align:right">2025 金額</th><th>變化</th>
        </tr></thead>
        <tbody>{ret_rows}</tbody>
      </table>
    </div>
"""

# ── 3. Insert before </div><!-- /panel-analysis-c --> ─────────────────────────
CLOSE_TAG = '</div><!-- /panel-analysis-c -->'
if CLOSE_TAG in html:
    html = html.replace(CLOSE_TAG, NEW_CARDS + '\n  ' + CLOSE_TAG, 1)
    print('Inserted 2025 cohort sections into panel-analysis-c')
else:
    print('ERROR: closing tag not found')

# ── 4. Embed COHORT_DATA in PB script block ────────────────────────────────────
cohort_json = json.dumps(COHORT, ensure_ascii=False)
COHORT_CONST = f'const COHORT_2025 = {cohort_json};\n'
# Insert right after PB_DATA const line
pb_marker = 'const PB_YEARS = '
if pb_marker in html:
    idx = html.index(pb_marker)
    # Find end of that line
    line_end = html.index('\n', idx) + 1
    html = html[:line_end] + '\n' + COHORT_CONST + html[line_end:]
    print('Injected COHORT_2025 const')
else:
    print('WARNING: PB_YEARS marker not found')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Lines:', html.count('\n'))
