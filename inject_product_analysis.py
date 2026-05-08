#!/usr/bin/env python3
"""Inject product analysis cards (retention / pricing gap / flaw summary) into panel-analysis-c"""
import json

with open('product_analysis.json', encoding='utf-8') as f:
    PA = json.load(f)

with open('index.html', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS ─────────────────────────────────────────────────────────────────────
CSS = """
/* ── Product analysis cards ── */
.pa-card { border:1px solid var(--border); border-radius:8px; padding:16px 18px;
  background:var(--bg2); margin-bottom:16px; }
.pa-card h4 { margin:0 0 12px 0; font-size:14px; color:#333; }
.pa-two-col { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.pa-ret-table { width:100%; border-collapse:collapse; font-size:12px; }
.pa-ret-table th { padding:5px 8px; text-align:left; border-bottom:2px solid var(--border);
  color:#888; font-weight:600; font-size:11px; white-space:nowrap; }
.pa-ret-table td { padding:4px 8px; border-bottom:1px solid var(--border); }
.pa-ret-bar { display:inline-block; height:6px; border-radius:3px; vertical-align:middle; margin-right:5px; }
.pa-ret-high { background:#2c7be5; }
.pa-ret-med  { background:#f6c90e; }
.pa-ret-low  { background:#e74c3c; }
.pa-ret-zero { background:#ddd; }
.pa-gap-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:10px; }
.pa-gap-card { border:1px solid var(--border); border-radius:8px; padding:10px 14px;
  background:var(--bg2); }
.pa-gap-label { font-size:11px; color:#888; margin-bottom:6px; }
.pa-gap-val { font-size:18px; font-weight:700; margin-bottom:4px; }
.pa-gap-desc { font-size:11px; color:#777; line-height:1.5; }
.pa-insight-box { background:#fffbea; border:1px solid #f6d860; border-radius:8px;
  padding:14px 18px; margin-top:16px; }
.pa-insight-box h4 { margin:0 0 10px 0; font-size:13px; color:#7a6000; }
.pa-insight-list { margin:0; padding-left:18px; font-size:12px; color:#555; line-height:1.9; }
.pa-sponsor-loyalty { display:flex; flex-wrap:wrap; gap:8px; }
.pa-sl-item { border:1px solid var(--border); border-radius:8px; padding:8px 12px;
  background:var(--bg2); min-width:160px; flex:1; }
.pa-sl-name { font-size:12px; font-weight:700; margin-bottom:4px; }
.pa-sl-score { font-size:11px; color:#888; margin-bottom:4px; }
.pa-sl-core { font-size:10px; color:#2c4baa; line-height:1.6; }
"""
html = html.replace('</style>', CSS + '\n</style>', 1)

# ── 2. Build analysis HTML ─────────────────────────────────────────────────────
retention = PA['retention']
value_gaps = PA['value_gaps']
loyalty = PA['loyalty']

# ── Card 1: Product stickiness table (split: high/medium/low/zero retention) ──
def ret_bar(pct):
    width = max(4, pct)
    cls = 'pa-ret-high' if pct >= 70 else 'pa-ret-med' if pct >= 40 else 'pa-ret-low' if pct >= 1 else 'pa-ret-zero'
    return f'<span class="pa-ret-bar {cls}" style="width:{width}px"></span>'

# Segment items
SKIP_ITEMS = {'LOGO 曝光', 'LOGO 曝光（線上）', 'LOGO 曝光（現場）',  # price=0, tier-included
              '企業品牌空間使用權', '主視覺使用權', '主持人唱名', '新聞稿置入',  # tier-only
              '線上轉播外框-贊助商LOGO圖卡、固定Bar、跑馬燈',
              '官方網站滾動式廣告欄位 A', '官方網站滾動式廣告欄位 B',
              '轉播LED大螢幕之橫幅帆布廣告版位', '行前記者會新聞稿適當置入',
              '企業打卡牆', '遊行講座品牌置入', '協會Logo影像授權', '年度素材授權',
              'IG 9月貼文', 'IG 9月 Reels', 'FB 9月貼文', 'FB 貼文', 'IG 貼文'}

top_items = [r for r in retention
             if r['adopters'] >= 4 and r['item'] not in SKIP_ITEMS]

rows_left = ''
rows_right = ''
half = (len(top_items) + 1) // 2
for i, r in enumerate(top_items):
    pct = r['retention_pct']
    price_str = f"NT${r['price']:,}" if r['price'] else '（級別含）'
    row = (f'<tr><td>{r["item"]}</td>'
           f'<td style="white-space:nowrap">{ret_bar(pct)}{pct}%</td>'
           f'<td style="color:#888">{r["adopters"]}</td>'
           f'<td style="color:#888">{price_str}</td></tr>')
    if i < half:
        rows_left += row
    else:
        rows_right += row

TH = '<tr><th>品項</th><th>保留率</th><th>採購者</th><th>定價</th></tr>'
RET_CARD = f"""
<div class="pa-card">
  <h4>品項黏著度 — 跨年保留率</h4>
  <p style="font-size:11px;color:#888;margin:0 0 12px">連續兩年皆採購同一品項的比率。僅含實際可單購品項（排除級別含）。</p>
  <div class="pa-two-col">
    <table class="pa-ret-table">{TH}{rows_left}</table>
    <table class="pa-ret-table">{TH}{rows_right}</table>
  </div>
</div>
"""

# ── Card 2: Pricing gap analysis ──────────────────────────────────────────────
# Pattern analysis from value_gaps
high_spend_single = [(g['sponsor'], g['year'], g['actual'], g['tier_label'], g['tier_price'], g['gap'], g['items'])
                     for g in value_gaps if g['actual'] >= 120000 and g['gap'] > 0]

# Float-only pattern: spent NT$120k on just float, T5 copper only NT$12k more
float_only_count = sum(1 for g in value_gaps
                       if g['actual'] == 120000 and '商業花車' in g['items'] and len(g['items']) <= 2)
float_only_sponsors = list(set(g['sponsor'] for g in value_gaps
                               if g['actual'] == 120000 and '商業花車' in g['items']))

# Space-only pattern
space_only = [(g['sponsor'], g['year'], g['actual'])
              for g in value_gaps if '企業品牌空間 A' in g['items'] and g['actual'] >= 200000]

# Oversized single packages (paid near/above tier)
oversized = [(g['sponsor'], g['year'], g['actual'], g['tier_label'], g['tier_price'])
             for g in value_gaps if g['gap'] <= 0]

GAP_CARD = f"""
<div class="pa-card">
  <h4>單購 vs 級別定價缺口</h4>
  <p style="font-size:11px;color:#888;margin:0 0 12px">以下廠商選擇單購品項，其花費與最接近級別的差距。</p>
  <div class="pa-gap-grid">
    <div class="pa-gap-card">
      <div class="pa-gap-label">花車定價倒置（Flaw 1）</div>
      <div class="pa-gap-val" style="color:#c0392b">{len(set(g['sponsor'] for g in value_gaps if g['actual']==120000 and '商業花車' in g['items']))} 家</div>
      <div class="pa-gap-desc">商業花車單價 NT$120,000 高於 T5銅 NT$108,000。花車買家每年多付 NT$12k，卻少得 T5 的其他所有項目。<br><strong>建議：調低花車單購至 NT$108k，或主動向花車買家推薦 T5。</strong></div>
    </div>
    <div class="pa-gap-card">
      <div class="pa-gap-label">品牌空間孤島（Flaw 2）</div>
      <div class="pa-gap-val" style="color:#7b3f9e">{len(set(s for s,y,a in space_only))} 家 × {len(space_only)} 次</div>
      <div class="pa-gap-desc">可口可樂等廠商每年 NT$250,000 只買「企業品牌空間A」，升 T3（NT$400,000）僅多花 NT$150k 可獲得 10+ 項。<br><strong>建議：將品牌空間 A 納入 T3+ 限定或推出體驗型中階包。</strong></div>
    </div>
    <div class="pa-gap-card">
      <div class="pa-gap-label">超額單購（Flaw 3）</div>
      <div class="pa-gap-val" style="color:#b52a3e">{len(oversized)} 次</div>
      <div class="pa-gap-desc">{'<br>'.join(f'{s} {y}: NT${a:,}（超過 {tl} NT${tp:,}）' for s,y,a,tl,tp in oversized[:3])}<br><strong>建議：設計「實體體驗套包」（花車首位＋品牌空間＋打卡牆）約 NT$550k。</strong></div>
    </div>
    <div class="pa-gap-card">
      <div class="pa-gap-label">社群品項流失率 100%（Flaw 4）</div>
      <div class="pa-gap-val" style="color:#888">9 類</div>
      <div class="pa-gap-desc">9月貼文、Reels、9/11月社群等 9 種品項跨年保留率為 0%，廠商每年重新選擇組合。<br><strong>建議：將零散社群品項整合為套包，提升確定性與交叉銷售機會。</strong></div>
    </div>
  </div>
</div>
"""

# ── Card 3: Per-sponsor loyalty top picks ─────────────────────────────────────
# Top sponsors by loyalty score with 2+ years
top_loyal = [s for s in loyalty if s['years_count'] >= 3 and s['core_items']][:12]
loyalty_chips = ''
for s in top_loyal:
    score = s['loyalty_score']
    core_str = '、'.join(s['core_items'][:4])
    if len(s['core_items']) > 4: core_str += f' 等{len(s["core_items"])}項'
    loyalty_chips += f'''<div class="pa-sl-item">
      <div class="pa-sl-name">{s["sponsor"]}</div>
      <div class="pa-sl-score">{s["years_count"]} 年出現｜品項忠誠度 {score}%</div>
      <div class="pa-sl-core">核心品項：{core_str}</div>
    </div>'''

LOYALTY_CARD = f"""
<div class="pa-card">
  <h4>廠商品項忠誠度（3年以上、有核心品項）</h4>
  <p style="font-size:11px;color:#888;margin:0 0 12px">「核心品項」＝每年皆採購的品項。忠誠度 = 核心品項數 / 曾採購品項總數。</p>
  <div class="pa-sponsor-loyalty">{loyalty_chips}</div>
</div>
"""

# ── Card 4: Insight summary ────────────────────────────────────────────────────
INSIGHT_BOX = """
<div class="pa-insight-box">
  <h4>💡 定價與包裝設計的關鍵發現</h4>
  <ul class="pa-insight-list">
    <li><strong>商業花車是最黏的單品（保留率 92%）</strong> — 但定價高於最低級別，導致花車買家每年多付 NT$12k 卻得到更少；這群人是 T5 最容易升購的對象。</li>
    <li><strong>可口可樂型廠商（只買品牌空間）是潛在 T3 客戶</strong> — 他們連續 3 年花 NT$250k，再加 NT$150k 就能到 T3，應設計「實體體驗限時升級方案」。</li>
    <li><strong>犀牛盾型廠商（自組高額單購）付了 T2 的錢卻沒有 T2 的名分</strong> — 他們要的是實體佈局（空間＋花車首位＋打卡牆），而非數位曝光；現有級別設計未能滿足此偏好。</li>
    <li><strong>社群類品項保留率普遍為 0%</strong> — 廠商每年重新拼湊，說明這類品項沒有粘性；考慮整合成「社群套包」固定銷售。</li>
    <li><strong>活動看板（83%）、轉播螢幕（72%）、手冊版位（72%）是最穩定的非花車品項</strong> — 這三項是跨類型廠商的共同偏好，建議納入所有級別包的基本配備。</li>
  </ul>
</div>
"""

NEW_SECTION = f"""
    <div class="co-section-title">品項採購深度分析</div>
    {RET_CARD}
    {GAP_CARD}
    {LOYALTY_CARD}
    {INSIGHT_BOX}
"""

# ── 3. Inject before closing tag ──────────────────────────────────────────────
CLOSE_TAG = '</div><!-- /panel-analysis-c -->'
if CLOSE_TAG in html:
    html = html.replace(CLOSE_TAG, NEW_SECTION + '\n  ' + CLOSE_TAG, 1)
    print('Injected product analysis section')
else:
    print('ERROR: closing tag not found')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done. Lines:', html.count('\n'))
print('pa-card in html:', html.count('pa-card'), 'instances')
