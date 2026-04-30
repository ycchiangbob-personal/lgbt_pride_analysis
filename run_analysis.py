#!/usr/bin/env python3
"""
run_analysis.py — 2016–2025 Taiwan LGBT Pride Sponsorship Analyses
Runs 6 analyses (D/A/B/C/E/F) and injects results into index.html.
"""
import json, math
from pathlib import Path

BASE = Path(__file__).parent

# ── Data loading ───────────────────────────────────────────────────────────────

def load_all():
    files = {
        'dp':    'donor_presence.json',
        'ids':   'id_state.json',
        'ext':   'all_extracted_v2.json',
        'y2021': '2021_final.json',
        'y2019': '2019_classified.json',
        'y2020': '2020_classified.json',
        'y2016': '2016_classified_v2.json',
        'y2017': '2017_classified.json',
        'y2018': '2018_classified_v2.json',
        'cys':   'cross_year_summary.json',
    }
    return {k: json.loads((BASE / v).read_text()) for k, v in files.items()}

def build_id_to_name(ids):
    result = {}
    for name, did in ids['all_donors'].items():
        if did not in result:
            result[did] = name
    return result

def build_name_to_id(ids):
    return {name.lower(): did for name, did in ids['all_donors'].items()}

TIER_NORM = {
    '白金級': 'T1', '黃金級': 'T2', '白銀級': 'T3', '鈦金級': 'T3',
    '銀級': 'T4', '銅級': 'T5',
    '花車': '單購', '單買': '單購',
    '友善飯店': '其他', '其他': '其他', '市集': '市集',
}

def fmt_ntd(n):
    if n >= 1_000_000: return f'{n/1_000_000:.2f}M'
    if n >= 1_000:     return f'{n/1_000:.0f}k'
    return str(int(n))

# ── Analysis D: Loyalists ─────────────────────────────────────────────────────

def analyze_D(dp, id_to_name, ext):
    window = ['2022', '2023', '2024', '2025']
    tier_lookup = {}
    for yr in window:
        for r in ext.get(yr, []):
            n = r['name_canonical'].lower()
            tier_lookup.setdefault(n, {})[yr] = r.get('tier_orig', '')

    results = []
    for did, ydata in dp.items():
        bools = [yr in ydata and bool(ydata[yr]) for yr in window]
        max_run = cur = 0
        for b in bools:
            cur = cur + 1 if b else 0
            max_run = max(max_run, cur)
        if max_run < 3:
            continue

        name = id_to_name.get(did, did)
        amounts = {yr: ydata[yr] for yr in window if yr in ydata and ydata[yr]}
        avg_amt = sum(amounts.values()) / len(amounts) if amounts else 0
        total_years = len([v for v in ydata.values() if v])

        nl = name.lower()
        tier_hist = {yr: TIER_NORM.get(tier_lookup.get(nl, {}).get(yr, ''), '—') or '—'
                     for yr in window}

        results.append({
            'id': did, 'name': name,
            'max_run': max_run, 'total_years': total_years,
            'avg_amount': round(avg_amt),
            'amounts': {yr: round(v) for yr, v in amounts.items()},
            'tier_hist': tier_hist,
            'score': round(max_run * avg_amt),
        })

    results.sort(key=lambda x: -x['score'])
    return results

# ── Analysis A: Retention ─────────────────────────────────────────────────────

def analyze_A(dp):
    pairs = [('2019','2020'),('2020','2021'),('2021','2022'),
             ('2022','2023'),('2023','2024'),('2024','2025')]
    results = []
    for y1, y2 in pairs:
        s1 = {d for d, v in dp.items() if y1 in v and v[y1]}
        s2 = {d for d, v in dp.items() if y2 in v and v[y2]}
        ret = s1 & s2
        rate = len(ret) / len(s1) if s1 else 0
        results.append({
            'label': f'{y1}→{y2}', 'y1': y1, 'y2': y2,
            'y1_count': len(s1), 'retained': len(ret),
            'rate': round(rate * 100, 1),
            'reliable': y1 >= '2022',
        })
    return results

# ── Analysis B: Win-back ──────────────────────────────────────────────────────

def analyze_B(dp, id_to_name, ext):
    in24 = {d for d, v in dp.items() if '2024' in v and v['2024']}
    in25 = {d for d, v in dp.items() if '2025' in v and v['2025']}
    winback = in24 - in25

    tier24 = {r['name_canonical'].lower(): r.get('tier_orig', '其他')
              for r in ext.get('2024', [])}

    WEIGHT = {
        '鈦金級': 1.5, '白金級': 1.5, '黃金級': 1.5,
        '銀級': 1.2, '白銀級': 1.2,
        '銅級': 1.0,
        '花車': 0.8, '單買': 0.8,
        '友善飯店': 0.6, '其他': 0.6, '市集': 0.6,
    }

    results = []
    for did in winback:
        name = id_to_name.get(did, did)
        amt = dp[did].get('2024') or 0
        yrs = len([v for v in dp[did].values() if v])
        tier = tier24.get(name.lower(), '其他')
        tw = WEIGHT.get(tier, 0.6)
        lb = 1.0 + min(yrs - 1, 5) * 0.1
        score = (amt / 10000) * lb * tw
        results.append({
            'id': did, 'name': name, 'amount_2024': round(amt),
            'tier_orig': tier, 'years_attended': yrs,
            'tier_weight': tw, 'loyalty_bonus': round(lb, 2),
            'score': round(score, 1),
        })

    results.sort(key=lambda x: -x['score'])
    for i, r in enumerate(results): r['rank'] = i + 1
    return results

# ── Analysis C: Tier Movement ─────────────────────────────────────────────────

def analyze_C(ext):
    CATS = {'鈦金級', '銀級', '銅級'}
    RANK = {'鈦金級': 3, '銀級': 2, '銅級': 1}
    LABEL = {'鈦金級': 'T3 鈦金', '銀級': 'T4 銀', '銅級': 'T5 銅'}

    t24 = {r['name_canonical']: r['tier_orig']
           for r in ext.get('2024', []) if r.get('tier_orig') in CATS}
    t25 = {r['name_canonical']: r['tier_orig']
           for r in ext.get('2025', []) if r.get('tier_orig') in CATS}

    upgraded, stayed, downgraded, dropped, new_in = [], [], [], [], []
    for name, tier in t24.items():
        if name in t25:
            t = t25[name]
            if   RANK[t] > RANK[tier]: upgraded.append({'name': name, 'from': LABEL[tier], 'to': LABEL[t]})
            elif RANK[t] < RANK[tier]: downgraded.append({'name': name, 'from': LABEL[tier], 'to': LABEL[t]})
            else:                       stayed.append({'name': name, 'tier': LABEL[tier]})
        else:
            dropped.append({'name': name, 'tier': LABEL[tier]})
    for name, tier in t25.items():
        if name not in t24:
            new_in.append({'name': name, 'tier': LABEL[tier]})

    return {
        'summary': {'upgraded': len(upgraded), 'stayed': len(stayed),
                    'downgraded': len(downgraded), 'dropped': len(dropped), 'new': len(new_in)},
        'upgraded': upgraded, 'stayed': stayed,
        'downgraded': downgraded, 'dropped': dropped, 'new': new_in,
    }

# ── Analysis E: New Entrant Survival ─────────────────────────────────────────

def analyze_E(dp):
    years = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
    results = []
    for i, yr in enumerate(years[:-1]):
        nxt = years[i + 1]
        prior = years[:i]
        new_set = {did for did, v in dp.items()
                   if yr in v and v[yr] and not any(py in v and v[py] for py in prior)}
        survived = sum(1 for did in new_set if nxt in dp[did] and dp[did][nxt])
        rate = survived / len(new_set) * 100 if new_set else 0
        results.append({
            'cohort': yr, 'next': nxt,
            'new_count': len(new_set), 'survived': survived,
            'rate': round(rate, 1), 'reliable': yr >= '2022',
        })
    return results

# ── Analysis F: Concentration ─────────────────────────────────────────────────

def analyze_F(dp, id_to_name, ext, cys):
    years = ['2022', '2023', '2024', '2025']
    by_year = []
    for yr in years:
        total = sum((cys[yr][c].get('amount') or 0) for c in cys[yr]) if yr in cys else 0
        donor_amts = {}
        for r in ext.get(yr, []):
            n = r['name_canonical']
            donor_amts[n] = donor_amts.get(n, 0) + (r.get('amount') or 0)
        sorted_d = sorted(donor_amts.items(), key=lambda x: -x[1])
        top3 = sorted_d[:3]; top5 = sorted_d[:5]
        top3_amt = sum(a for _, a in top3)
        top5_amt = sum(a for _, a in top5)
        hhi = round(sum((a / total * 100) ** 2 for _, a in sorted_d)) if total else 0
        by_year.append({
            'year': yr, 'total': round(total), 'n_donors': len(donor_amts),
            'top3_pct': round(top3_amt / total * 100, 1) if total else 0,
            'top5_pct': round(top5_amt / total * 100, 1) if total else 0,
            'hhi': hhi,
            'top3_names': [n for n, _ in top3],
            'top3_amts': [round(a) for _, a in top3],
        })
    r25 = by_year[-1]
    top3_total = sum(r25['top3_amts'])
    remaining = r25['total'] - top3_total
    whatif = {
        'top3_names': r25['top3_names'],
        'top3_total': top3_total,
        'remaining': remaining,
        'remaining_pct': round(remaining / r25['total'] * 100, 1) if r25['total'] else 0,
    }
    return {'by_year': by_year, 'whatif_2025': whatif}

# ── HTML / CSS helpers ─────────────────────────────────────────────────────────

EXTRA_CSS = """
  .action-box {
    background: #edf7ed; border: 1px solid #81c784;
    border-left: 4px solid #388e3c; border-radius: var(--radius);
    padding: 14px 18px; margin-top: 16px; font-size: 13px;
    color: #1b5e20; display: flex; gap: 12px;
    align-items: flex-start; line-height: 1.7;
  }
  .action-box .act-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }
  .plain-desc { font-size: 13px; color: var(--text-secondary); padding: 6px 0 12px; line-height: 1.75; }
  .badge-row { display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }
  .badge-item { flex: 1; min-width: 80px; background: #f5f4f0; border-radius: 8px; padding: 12px 16px; text-align: center; }
  .badge-item .badge-num { font-size: 26px; font-weight: 700; letter-spacing: -0.03em; }
  .badge-item .badge-label { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
  .badge-item.up .badge-num { color: #2e7d32; }
  .badge-item.down .badge-num { color: #c62828; }
  .badge-item.drop .badge-num { color: #e65100; }
  .badge-item.new-badge .badge-num { color: #1565c0; }
  .tier-chip { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 12px; background: #f0ede8; color: var(--text-secondary); }
  .unreliable { opacity: 0.55; }
  .callout-box { background: #fff3e0; border: 1px solid #ffb74d; border-left: 4px solid #e65100; border-radius: var(--radius); padding: 14px 18px; margin-top: 16px; font-size: 13px; color: #bf360c; line-height: 1.7; }
  details summary { cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text-secondary); padding: 6px 0; user-select: none; }
  details summary:hover { color: var(--text-primary); }
"""

def jd(obj):
    return json.dumps(obj, ensure_ascii=False)

def tier_badge(tier):
    colors = {'T1':'#B8860B','T2':'#E8A600','T3':'#4472C4','T4':'#70AD47','T5':'#ED7D31','單購':'#5BC0EB','其他':'#aaa','市集':'#aaa','—':'#ddd'}
    c = colors.get(tier, '#ddd')
    return f'<span class="tier-chip" style="background:{c}20;color:{c}">{tier}</span>'

# ── Section D ─────────────────────────────────────────────────────────────────

def section_D(data):
    names   = jd([d['name'] for d in data])
    amounts = jd([d['avg_amount'] for d in data])

    rows = []
    for d in data:
        th = d['tier_hist']
        tcells = ''.join(f'<td style="text-align:center">{tier_badge(th.get(yr,"—"))}</td>'
                         for yr in ['2022','2023','2024','2025'])
        rows.append(
            f'<tr><td><strong>{d["name"]}</strong></td>'
            f'<td style="text-align:center">{d["max_run"]} 年</td>'
            f'<td style="text-align:center">{d["total_years"]} 年</td>'
            f'{tcells}'
            f'<td class="right">NTD {fmt_ntd(d["avg_amount"])}</td></tr>'
        )

    h = min(len(data) * 30 + 60, 560)
    html = f"""
  <!-- Section: Analysis D -->
  <div class="section-title">分析 D：忠實贊助商輪廓</div>
  <div class="chart-card">
    <h3>2022–2025 年連續贊助 3 年以上的廠商（共 {len(data)} 家）</h3>
    <p class="plain-desc">
      這 {len(data)} 家廠商是我們最穩定的收入來源，在 2022–2025 年間連續贊助了 3 年以上。
      圖表依「年平均贊助金額 × 連續年數」排序，排越前面的廠商，對 2026 的價值越高。
    </p>
    <div style="position:relative;width:100%;height:{h}px;margin-bottom:20px;">
      <canvas id="loyalistChart"></canvas>
    </div>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr>
          <th>廠商名稱</th><th style="text-align:center">最長連續</th><th style="text-align:center">歷年出席</th>
          <th style="text-align:center">2022</th><th style="text-align:center">2023</th>
          <th style="text-align:center">2024</th><th style="text-align:center">2025</th>
          <th class="right">平均金額</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <div class="action-box">
      <span class="act-icon">🎯</span>
      <div><strong>行動建議：</strong>
      這份名單是 2026 業務的第一優先拜訪清單。第一季前確認每一家是否延續合作，
      並詢問是否有升級意願。鞏固這 {len(data)} 家，等同於保住收入基礎的主要部分。</div>
    </div>
  </div>
"""
    js = f"""
  (function() {{
    new Chart(document.getElementById('loyalistChart'), {{
      type: 'bar',
      data: {{ labels: {names}, datasets: [{{ label: '年平均贊助金額', data: {amounts}, backgroundColor: '#B8860B', borderRadius: 4 }}] }},
      options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ' NTD ' + ctx.raw.toLocaleString('zh-TW') }} }} }},
        scales: {{
          x: {{ ticks: {{ callback: v => v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(0)+'k':String(v) }}, grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
          y: {{ ticks: {{ font: {{ size: 11 }} }}, grid: {{ display: false }} }}
        }}
      }}
    }});
  }})();
"""
    return html, js

# ── Section A ─────────────────────────────────────────────────────────────────

def section_A(data):
    labels  = jd([d['label'] for d in data])
    rates   = jd([d['rate'] for d in data])
    colors  = jd(['#cccccc' if not d['reliable'] else '#4472C4' for d in data])

    rows = []
    for d in data:
        note = '' if d['reliable'] else ' <span style="font-size:11px;color:var(--text-muted);font-style:italic">（參考）</span>'
        cls  = '' if d['reliable'] else ' class="unreliable"'
        rows.append(
            f'<tr{cls}><td>{d["label"]}{note}</td>'
            f'<td class="right">{d["y1_count"]}</td>'
            f'<td class="right">{d["retained"]}</td>'
            f'<td class="right"><strong>{d["rate"]}%</strong></td></tr>'
        )

    html = f"""
  <!-- Section: Analysis A -->
  <div class="section-title">分析 A：年度留存率趨勢</div>
  <div class="chart-card">
    <h3>每年有多少去年的廠商今年繼續贊助？（2019–2025）</h3>
    <p class="plain-desc">
      留存率 = 去年有贊助的廠商中，今年繼續合作的比例。
      灰色柱子（2019–2021）因原始資料不完整，數字僅供參考。
      <strong>2024→2025 的留存率從 53% 掉到 41%，是近四年最低點——相當於每 10 家去年的廠商，有 6 家沒有回來。</strong>
    </p>
    <div style="position:relative;width:100%;height:240px;">
      <canvas id="retentionChart"></canvas>
    </div>
    <div style="overflow-x:auto;margin-top:16px;">
      <table class="data-table">
        <thead><tr>
          <th>年度</th><th class="right">前一年廠商數</th><th class="right">續簽數</th><th class="right">留存率</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <div class="action-box">
      <span class="act-icon">📉</span>
      <div><strong>行動建議：</strong>
      留存率下滑是 2026 缺口的主要成因之一。建議在 2026 年合約到期前 3 個月主動啟動續簽溝通，
      並針對 2024 年仍在、2025 年流失的廠商（見分析 B），排定電話或拜訪計畫。</div>
    </div>
  </div>
"""
    js = f"""
  (function() {{
    new Chart(document.getElementById('retentionChart'), {{
      type: 'bar',
      data: {{ labels: {labels}, datasets: [{{ label: '留存率（%）', data: {rates}, backgroundColor: {colors}, borderRadius: 4 }}] }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ' 留存率：' + ctx.raw + '%' }} }} }},
        scales: {{
          y: {{ max: 100, ticks: {{ callback: v => v + '%' }}, grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
          x: {{ grid: {{ display: false }} }}
        }}
      }}
    }});
  }})();
"""
    return html, js

# ── Section B ─────────────────────────────────────────────────────────────────

def section_B(data):
    total_pot = sum(d['amount_2024'] for d in data)
    half      = total_pot // 2

    rows = []
    for d in data:
        rows.append(
            f'<tr>'
            f'<td style="text-align:center;color:var(--text-muted);font-size:12px">{d["rank"]}</td>'
            f'<td><strong>{d["name"]}</strong></td>'
            f'<td>{tier_badge(TIER_NORM.get(d["tier_orig"], d["tier_orig"] or "其他"))}</td>'
            f'<td class="right">NTD {d["amount_2024"]:,}</td>'
            f'<td class="right">{d["years_attended"]} 年</td>'
            f'<td class="right"><strong>{d["score"]:.1f}</strong></td>'
            f'</tr>'
        )

    html = f"""
  <!-- Section: Analysis B -->
  <div class="section-title">分析 B：2024 流失廠商挽回優先清單</div>
  <div class="chart-card">
    <h3>2024 年有贊助、但 2025 年沒有出現的廠商（共 {len(data)} 家）</h3>
    <p class="plain-desc">
      這 {len(data)} 家廠商在 2024 年合計貢獻了 NTD {fmt_ntd(total_pot)}。
      優先分數越高，代表挽回後的潛在收益越大，請從第 1 名開始依序聯繫。
    </p>
    <div class="note" style="margin-bottom:16px;">
      <strong>優先分數計算方式：</strong>（2024 年金額 ÷ 10,000）×（出席年數加成，最高 +50%）×（類型權重：T3 鈦金=1.5、T4 銀=1.2、T5 銅=1.0、單購=0.8、其他/市集=0.6）
    </div>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr>
          <th style="text-align:center">#</th><th>廠商名稱</th><th>2024 年類型</th>
          <th class="right">2024 年金額</th><th class="right">歷年出席</th><th class="right">優先分數</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <div class="action-box">
      <span class="act-icon">📞</span>
      <div><strong>行動建議：</strong>
      挽回這 {len(data)} 家的一半，預計可補回約 NTD {fmt_ntd(half)} 的收入缺口，
      直接有助於達成 2026 年 9.5M 的目標。建議業務組依排名分配拜訪任務，每人負責前幾名。</div>
    </div>
  </div>
"""
    return html, ''

# ── Section C ─────────────────────────────────────────────────────────────────

def section_C(data):
    s = data['summary']

    def badge_html(count, label, cls):
        return (f'<div class="badge-item {cls}">'
                f'<div class="badge-num">{count}</div>'
                f'<div class="badge-label">{label}</div></div>')

    badges = (badge_html(s['new'],       '新加入', 'new-badge') +
              badge_html(s['upgraded'],  '升級',   'up') +
              badge_html(s['stayed'],    '維持',   '') +
              badge_html(s['downgraded'],'降級',   'down') +
              badge_html(s['dropped'],   '離開',   'drop'))

    def detail_tbl(items):
        if not items:
            return '<p style="color:var(--text-muted);font-size:13px;padding:6px 0">無</p>'
        rows = []
        for item in items:
            if 'from' in item:
                rows.append(f'<tr><td>{item["name"]}</td><td>'
                            f'{tier_badge(item["from"])} → {tier_badge(item["to"])}</td></tr>')
            else:
                rows.append(f'<tr><td>{item["name"]}</td><td>{tier_badge(item.get("tier",""))}</td></tr>')
        return f'<table class="data-table" style="margin-top:6px">{"".join(rows)}</table>'

    html = f"""
  <!-- Section: Analysis C -->
  <div class="section-title">分析 C：級別異動 2024 → 2025</div>
  <div class="chart-card">
    <h3>在 2024 和 2025 年都有簽級別合約的廠商，級別有什麼變化？</h3>
    <p class="plain-desc">
      以下僅統計簽有 T3 鈦金 / T4 銀 / T5 銅 級別合約的廠商。
      依廠商名稱精確比對，若廠商有更名或分拆，可能未納入統計。
    </p>
    <div class="badge-row">{badges}</div>
    <details><summary>▸ 升級廠商（{s['upgraded']} 家）</summary>{detail_tbl(data['upgraded'])}</details>
    <details><summary>▸ 降級廠商（{s['downgraded']} 家）</summary>{detail_tbl(data['downgraded'])}</details>
    <details><summary>▸ 維持廠商（{s['stayed']} 家）</summary>{detail_tbl(data['stayed'])}</details>
    <details><summary>▸ 離開廠商（{s['dropped']} 家，已列入分析 B 挽回清單）</summary>{detail_tbl(data['dropped'])}</details>
    <details><summary>▸ 2025 年新加入廠商（{s['new']} 家）</summary>{detail_tbl(data['new'])}</details>
    <div class="action-box">
      <span class="act-icon">📊</span>
      <div><strong>行動建議：</strong>
      主動了解降級廠商的原因（預算縮減？服務不符預期？），並針對升級廠商探詢是否願意進一步深化合作。
      新加入的廠商是 2026 的重點培養對象，請在活動後三個月內安排感謝回訪。</div>
    </div>
  </div>
"""
    return html, ''

# ── Section E ─────────────────────────────────────────────────────────────────

def section_E(data):
    labels = jd([d['cohort'] for d in data])
    rates  = jd([d['rate'] for d in data])
    colors = jd(['#cccccc' if not d['reliable'] else '#5BC0EB' for d in data])

    rate24 = next((d['rate'] for d in data if d['cohort'] == '2024'), '—')

    rows = []
    for d in data:
        note = '' if d['reliable'] else ' <span style="font-size:11px;color:var(--text-muted);font-style:italic">（參考）</span>'
        cls  = '' if d['reliable'] else ' class="unreliable"'
        rows.append(
            f'<tr{cls}><td>{d["cohort"]} 年新廠商{note}</td>'
            f'<td class="right">{d["new_count"]}</td>'
            f'<td class="right">{d["survived"]}</td>'
            f'<td class="right"><strong>{d["rate"]}%</strong></td></tr>'
        )

    html = f"""
  <!-- Section: Analysis E -->
  <div class="section-title">分析 E：新廠商隔年存活率</div>
  <div class="chart-card">
    <h3>第一次合作的廠商，隔年還會繼續嗎？（2022–2024 年新客）</h3>
    <p class="plain-desc">
      每年首次加入的廠商，隔年繼續合作的比例正在下降。
      <strong>2024 年新加入的廠商，隔年只有 {rate24}% 留了下來</strong>——
      代表大多數新廠商只合作了一次就離開了。灰色柱子（2016–2021）因資料不完整，僅供參考。
    </p>
    <div style="position:relative;width:100%;height:220px;">
      <canvas id="survivalChart"></canvas>
    </div>
    <div style="overflow-x:auto;margin-top:16px;">
      <table class="data-table">
        <thead><tr>
          <th>新廠商加入年度</th><th class="right">新廠商數</th>
          <th class="right">隔年存活</th><th class="right">存活率</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <div class="action-box">
      <span class="act-icon">🌱</span>
      <div><strong>行動建議：</strong>
      對 2025 年首次贊助的廠商，建立「新客跟進三步驟」：
      ①活動結束後一個月內發送感謝函、②三個月內電話回訪了解體驗、③六個月前發出 2026 邀請。
      若能把存活率從 14% 提升到 30%，等同於多留住約 10 家新廠商。</div>
    </div>
  </div>
"""
    js = f"""
  (function() {{
    new Chart(document.getElementById('survivalChart'), {{
      type: 'bar',
      data: {{ labels: {labels}, datasets: [{{ label: '新廠商隔年存活率（%）', data: {rates}, backgroundColor: {colors}, borderRadius: 4 }}] }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ' 存活率：' + ctx.raw + '%' }} }} }},
        scales: {{
          y: {{ max: 100, ticks: {{ callback: v => v + '%' }}, grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
          x: {{ grid: {{ display: false }} }}
        }}
      }}
    }});
  }})();
"""
    return html, js

# ── Section F ─────────────────────────────────────────────────────────────────

def section_F(data):
    by_year = data['by_year']
    whatif  = data['whatif_2025']

    years_j = jd([d['year']     for d in by_year])
    top3_j  = jd([d['top3_pct'] for d in by_year])
    top5_j  = jd([d['top5_pct'] for d in by_year])
    hhi_j   = jd([d['hhi']      for d in by_year])

    rows = []
    for d in by_year:
        top3_names = '、'.join(d['top3_names'][:3])
        rows.append(
            f'<tr><td>{d["year"]}</td>'
            f'<td class="right">{d["n_donors"]}</td>'
            f'<td class="right">NTD {fmt_ntd(d["total"])}</td>'
            f'<td class="right">{d["top3_pct"]}%</td>'
            f'<td class="right">{d["top5_pct"]}%</td>'
            f'<td class="right">{d["hhi"]}</td>'
            f'<td style="font-size:12px;color:var(--text-muted)">{top3_names}</td></tr>'
        )

    top3_str = '、'.join(whatif['top3_names'])

    html = f"""
  <!-- Section: Analysis F -->
  <div class="section-title">分析 F：贊助收入集中度風險</div>
  <div class="chart-card">
    <h3>前幾大廠商佔了多少收入？萬一他們不來了呢？（2022–2025）</h3>
    <p class="plain-desc">
      集中度越高代表我們越依賴少數廠商。HHI 指數是衡量集中度的通用標準，數字越大風險越高
      （1,500 以上屬高度集中）。前三大廠商通常佔總收入的 15–25%，任何一家不續約都會造成顯著缺口。
    </p>
    <div style="position:relative;width:100%;height:260px;">
      <canvas id="concentrationChart"></canvas>
    </div>
    <div style="overflow-x:auto;margin-top:16px;">
      <table class="data-table">
        <thead><tr>
          <th>年度</th><th class="right">廠商數</th><th class="right">總金額</th>
          <th class="right">前 3 家佔比</th><th class="right">前 5 家佔比</th>
          <th class="right">HHI 指數</th><th>前 3 大廠商</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <div class="callout-box">
      <strong>⚠️ 情境模擬：2025 年若前三大廠商（{top3_str}）全數不續約</strong><br>
      預計損失 NTD {whatif['top3_total']:,}，剩餘收入約 NTD {whatif['remaining']:,}，
      僅佔原本的 <strong>{whatif['remaining_pct']}%</strong>。
    </div>
    <div class="action-box">
      <span class="act-icon">⚖️</span>
      <div><strong>行動建議：</strong>
      大廠續約是 2026 最優先的任務，必須在所有其他業務之前確認。
      同時積極開發新的中型廠商（T4–T5 級）以分散風險：
      每增加 5 家 T4 廠商（每家約 16 萬），就能補回約 80 萬元，並降低對單一大廠的依賴。</div>
    </div>
  </div>
"""
    js = f"""
  (function() {{
    new Chart(document.getElementById('concentrationChart'), {{
      type: 'bar',
      data: {{
        labels: {years_j},
        datasets: [
          {{ type: 'bar',  label: '前 3 家佔比（%）', data: {top3_j}, backgroundColor: '#B8860B', borderRadius: 4, yAxisID: 'y' }},
          {{ type: 'bar',  label: '前 5 家佔比（%）', data: {top5_j}, backgroundColor: '#E8A600', borderRadius: 4, yAxisID: 'y' }},
          {{ type: 'line', label: 'HHI 集中度指數',   data: {hhi_j},  borderColor: '#e8445a', backgroundColor: 'transparent',
             pointBackgroundColor: '#e8445a', borderWidth: 2.5, pointRadius: 5, yAxisID: 'y2' }},
        ]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: true, position: 'top', labels: {{ font: {{ size: 12 }}, usePointStyle: true }} }},
          tooltip: {{ mode: 'index' }}
        }},
        scales: {{
          y:  {{ position: 'left',  max: 60, ticks: {{ callback: v => v + '%' }}, title: {{ display: true, text: '佔總收入比例（%）', font: {{ size: 11 }} }}, grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
          y2: {{ position: 'right', title: {{ display: true, text: 'HHI 指數', font: {{ size: 11 }} }}, grid: {{ display: false }} }},
          x:  {{ grid: {{ display: false }} }}
        }}
      }}
    }});
  }})();
"""
    return html, js

# ── Inject into index.html ─────────────────────────────────────────────────────

def inject(html_path, sections, css):
    html = html_path.read_text()

    if '<!-- Section: Analysis D -->' in html:
        print("WARNING: Analysis sections already present. Remove them first to re-inject.")
        return False

    # Add CSS
    html = html.replace('</style>', css + '\n</style>', 1)

    # Collect all HTML + JS
    all_html = ''.join(s[0] for s in sections)
    all_js   = ''.join(s[1] for s in sections)

    # Insert HTML before methodology marker
    marker = '  <!-- Section: Methodology -->'
    html = html.replace(marker, all_html + '\n' + marker, 1)

    # Insert JS before final </script>
    last_script = html.rfind('</script>')
    html = html[:last_script] + '\n' + all_js + '\n' + html[last_script:]

    html_path.write_text(html)
    return True

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("Loading data files...")
    d = load_all()
    dp, ids, ext, cys = d['dp'], d['ids'], d['ext'], d['cys']
    id_to_name = build_id_to_name(ids)

    print("D — Loyalists...")
    rD = analyze_D(dp, id_to_name, ext)
    print("A — Retention...")
    rA = analyze_A(dp)
    print("B — Win-back...")
    rB = analyze_B(dp, id_to_name, ext)
    print("C — Tier Movement...")
    rC = analyze_C(ext)
    print("E — New Entrant Survival...")
    rE = analyze_E(dp)
    print("F — Concentration Risk...")
    rF = analyze_F(dp, id_to_name, ext, cys)

    print("\n=== VERIFICATION ===")
    print(f"[D] Loyalists: {len(rD)}  (expect ~27)")
    ad = {r['label']: r['rate'] for r in rA}
    print(f"[A] 2022→2023: {ad.get('2022→2023')}%  (expect 46%)")
    print(f"[A] 2023→2024: {ad.get('2023→2024')}%  (expect 53%)")
    print(f"[A] 2024→2025: {ad.get('2024→2025')}%  (expect 41%)")
    print(f"[B] Win-back count: {len(rB)}  (expect 47)")
    s = rC['summary']
    print(f"[C] upgraded={s['upgraded']} stayed={s['stayed']} downgraded={s['downgraded']} dropped={s['dropped']} new={s['new']}")
    ed = {r['cohort']: r['rate'] for r in rE}
    print(f"[E] 2022→2023: {ed.get('2022')}%  (expect 27%)")
    print(f"[E] 2023→2024: {ed.get('2023')}%  (expect 29%)")
    print(f"[E] 2024→2025: {ed.get('2024')}%  (expect 14%)")

    print("\nGenerating HTML sections...")
    sections = [
        section_D(rD),
        section_A(rA),
        section_B(rB),
        section_C(rC),
        section_E(rE),
        section_F(rF),
    ]

    ok = inject(BASE / 'index.html', sections, EXTRA_CSS)
    if ok:
        print("index.html updated — 6 sections injected before 統計口徑說明.")
    else:
        print("No changes made.")

if __name__ == '__main__':
    main()
