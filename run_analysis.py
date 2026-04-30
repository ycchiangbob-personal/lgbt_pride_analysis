#!/usr/bin/env python3
"""
run_analysis.py — 2016–2025 Taiwan LGBT Pride Sponsorship Analyses
Runs 6 analyses (D/A/B/C/E/F) and injects results into index.html.
Re-runnable: strips previous sections before re-injecting.
"""
import json, math
from pathlib import Path
from collections import defaultdict

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
    '花車': '花車', '單買': '單買',
    '友善飯店': '其他', '其他': '其他', '市集': '市集',
}

MARKET_HOTEL_TIERS = {'市集', '友善飯店', '其他'}

def fmt_ntd(n):
    if n >= 1_000_000: return f'{n/1_000_000:.2f}M'
    if n >= 1_000:     return f'{n/1_000:.0f}k'
    return str(int(n))

def jd(obj):
    return json.dumps(obj, ensure_ascii=False)

def tier_badge(tier):
    colors = {
        'T1':'#B8860B','T2':'#E8A600','T3':'#4472C4','T4':'#70AD47','T5':'#ED7D31',
        '單購':'#5BC0EB','花車':'#5BC0EB','單買':'#5BC0EB',
        '其他':'#aaa','市集':'#aaa','—':'#ddd','?':'#ccc'
    }
    c = colors.get(tier, '#ddd')
    return f'<span class="tier-chip" style="background:{c}20;color:{c}">{tier}</span>'

# ── Analysis D: Loyalists ─────────────────────────────────────────────────────

def analyze_D(dp, id_to_name, ext):
    window = ['2022', '2023', '2024', '2025']

    # Build per-name lookup from ext: {name_lower: {year: {tier, amount, industry}}}
    name_ext = {}
    for yr in window:
        for r in ext.get(yr, []):
            n = r['name_canonical'].lower()
            name_ext.setdefault(n, {})[yr] = {
                'tier':     r.get('tier_orig', ''),
                'amount':   r.get('amount', 0) or 0,
                'industry': r.get('industry', '') or '',
            }

    JUNK_INDUSTRIES = {'A','B','C','Ｖ','個別廠商業務統計',''}

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
        nl   = name.lower()
        amounts = {yr: ydata[yr] for yr in window if yr in ydata and ydata[yr]}
        avg_amt = sum(amounts.values()) / len(amounts) if amounts else 0
        total_years = len([v for v in ydata.values() if v])

        # Tier hist: preserve 花車/單買 distinction
        tier_hist = {}
        for yr in window:
            ei = name_ext.get(nl, {}).get(yr)
            if ei:
                raw = ei['tier']
                tier_hist[yr] = TIER_NORM.get(raw, '—') or '—'
            elif yr in ydata and ydata[yr]:
                tier_hist[yr] = '?'
            else:
                tier_hist[yr] = '—'

        # Per-year amounts from ext (preferred) then dp
        ext_amounts = {}
        for yr in window:
            ei = name_ext.get(nl, {}).get(yr)
            if ei and ei['amount']:
                ext_amounts[yr] = round(ei['amount'])
            elif yr in ydata and ydata[yr]:
                ext_amounts[yr] = round(ydata[yr])

        # Industry: prefer latest year
        industry = ''
        for yr in reversed(window):
            ei = name_ext.get(nl, {}).get(yr)
            if ei and ei['industry'] not in JUNK_INDUSTRIES:
                industry = ei['industry']
                break

        results.append({
            'id': did, 'name': name, 'industry': industry,
            'max_run': max_run, 'total_years': total_years,
            'avg_amount': round(avg_amt),
            'total_amount': round(sum(amounts.values())),
            'ext_amounts': ext_amounts,
            'tier_hist': tier_hist,
            'score': round(max_run * avg_amt),
        })

    results.sort(key=lambda x: -x['score'])
    return results

# ── Analysis A: Retention + Churn Amount ──────────────────────────────────────

def analyze_A(dp):
    pairs = [('2019','2020'),('2020','2021'),('2021','2022'),
             ('2022','2023'),('2023','2024'),('2024','2025')]
    results = []
    for y1, y2 in pairs:
        s1 = {d for d, v in dp.items() if y1 in v and v[y1]}
        s2 = {d for d, v in dp.items() if y2 in v and v[y2]}
        ret     = s1 & s2
        churned = s1 - s2
        rate    = len(ret) / len(s1) if s1 else 0

        # Amount analysis only for reliable years
        if y1 >= '2022':
            c_amts = [dp[d].get(y1, 0) or 0 for d in churned]
            r_amts = [dp[d].get(y1, 0) or 0 for d in ret]
            churned_total = round(sum(c_amts))
            retained_total = round(sum(r_amts))
            churned_avg  = round(churned_total / len(churned)) if churned else 0
            retained_avg = round(retained_total / len(ret))   if ret     else 0
        else:
            churned_total = retained_total = churned_avg = retained_avg = None

        results.append({
            'label': f'{y1}→{y2}', 'y1': y1, 'y2': y2,
            'y1_count': len(s1), 'retained': len(ret), 'churned': len(churned),
            'rate': round(rate * 100, 1),
            'reliable': y1 >= '2022',
            'churned_total':  churned_total,
            'retained_total': retained_total,
            'churned_avg':    churned_avg,
            'retained_avg':   retained_avg,
        })
    return results

# ── Analysis B: Win-back (filtered + multi-year) ──────────────────────────────

def analyze_B(dp, id_to_name, ext):
    in25 = {d for d, v in dp.items() if '2025' in v and v['2025']}
    LOOKBACK = ['2024', '2023', '2022']

    # Build per-year tier and industry from ext
    tier_by_yr  = {}   # {yr: {name_lower: tier_orig}}
    ind_lookup  = {}   # {name_lower: industry}
    JUNK = {'A','B','C','Ｖ','個別廠商業務統計',''}
    for yr in LOOKBACK:
        tier_by_yr[yr] = {}
        for r in ext.get(yr, []):
            n = r['name_canonical'].lower()
            tier_by_yr[yr][n] = r.get('tier_orig', '其他') or '其他'
            ind = r.get('industry', '') or ''
            if ind not in JUNK:
                ind_lookup[n] = ind

    WEIGHT = {
        '鈦金級': 1.5, '白金級': 1.5, '黃金級': 1.5,
        '銀級': 1.2, '白銀級': 1.2,
        '銅級': 1.0,
        '花車': 0.8, '單買': 0.8,
        '友善飯店': 0.4, '其他': 0.4, '市集': 0.4,
    }

    by_year = defaultdict(list)

    for did, ydata in dp.items():
        if did in in25:
            continue

        # Find last active year within lookback window
        last_active = None
        for yr in LOOKBACK:
            if yr in ydata and ydata[yr]:
                last_active = yr
                break
        if not last_active:
            continue

        name = id_to_name.get(did, did)
        nl   = name.lower()
        tier_last = tier_by_yr.get(last_active, {}).get(nl, '其他')

        # Skip donors whose last-year tier is market/hotel category
        if tier_last in MARKET_HOTEL_TIERS:
            continue

        amt_last   = round(dp[did].get(last_active, 0) or 0)
        yrs_active = len([v for v in ydata.values() if v])
        tw = WEIGHT.get(tier_last, 0.4)
        lb = 1.0 + min(yrs_active - 1, 5) * 0.1
        one_time = yrs_active == 1
        score = (amt_last / 10000) * lb * tw * (0.5 if one_time else 1.0)

        by_year[last_active].append({
            'name': name, 'industry': ind_lookup.get(nl, ''),
            'amount_last': amt_last, 'tier_last': tier_last,
            'last_active': last_active, 'years_attended': yrs_active,
            'one_time': one_time,
            'score': round(score, 1),
        })

    # Sort each group by score desc, assign ranks
    result = {}
    for yr in LOOKBACK:
        grp = by_year.get(yr, [])
        grp.sort(key=lambda x: -x['score'])
        for i, r in enumerate(grp):
            r['rank'] = i + 1
        result[yr] = grp
    return result

# ── Analysis C: Tier Movement ─────────────────────────────────────────────────

def analyze_C(ext):
    CATS = {'鈦金級', '銀級', '銅級'}
    RANK  = {'鈦金級': 3, '銀級': 2, '銅級': 1}
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
        nxt  = years[i + 1]
        prior = years[:i]
        new_set  = {did for did, v in dp.items()
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
            'top3_amts':  [round(a) for _, a in top3],
        })
    r25 = by_year[-1]
    top3_total = sum(r25['top3_amts'])
    remaining  = r25['total'] - top3_total
    whatif = {
        'top3_names':    r25['top3_names'],
        'top3_total':    top3_total,
        'remaining':     remaining,
        'remaining_pct': round(remaining / r25['total'] * 100, 1) if r25['total'] else 0,
    }
    return {'by_year': by_year, 'whatif_2025': whatif}

# ── Section D ─────────────────────────────────────────────────────────────────

def section_D(data):
    names_j   = jd([d['name']          for d in data])
    amounts_j = jd([d['total_amount']  for d in data])

    loyalists_js = jd([{
        'name':        d['name'],
        'industry':    d['industry'],
        'maxRun':      d['max_run'],
        'totalYears':  d['total_years'],
        'tiers':       d['tier_hist'],
        'amounts':     d['ext_amounts'],
        'avgAmount':   d['avg_amount'],
        'totalAmount': d['total_amount'],
    } for d in data])

    h = min(len(data) * 30 + 60, 700)

    html = f"""
  <!-- Section: Analysis D -->
  <div class="section-title">忠實贊助商輪廓</div>
  <div class="chart-card">
    <h3>2022–2025 年連續贊助 3 年以上的廠商（共 {len(data)} 家）</h3>
    <p class="plain-desc">
      這 {len(data)} 家廠商是最穩定的收入來源，連續贊助 3 年以上。
      圖表依「年均金額 × 連續年數」排序；表格可切換顯示各年度贊助類別或實際金額。
    </p>
    <div style="position:relative;width:100%;height:{h}px;margin-bottom:20px;">
      <canvas id="loyalistChart"></canvas>
    </div>
    <div class="toggle-group" style="margin-bottom:12px;">
      <button class="toggle-btn active loyalist-toggle" onclick="toggleLoyalistView('tier',this)">各年贊助類別</button>
      <button class="toggle-btn loyalist-toggle" onclick="toggleLoyalistView('amount',this)">各年贊助金額</button>
    </div>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr>
          <th>廠商名稱</th><th style="text-align:center">產業</th>
          <th style="text-align:center">連續/參與</th>
          <th style="text-align:center">2022</th><th style="text-align:center">2023</th>
          <th style="text-align:center">2024</th><th style="text-align:center">2025</th>
          <th class="right">年均金額</th>
        </tr></thead>
        <tbody id="loyalist-tbody"></tbody>
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
    const DATA_LOYALISTS = {loyalists_js};
    let loyalistView = 'tier';
    const TCOL = {{ T1:'#B8860B',T2:'#E8A600',T3:'#4472C4',T4:'#70AD47',T5:'#ED7D31',
                    '花車':'#5BC0EB','單買':'#5BC0EB','單購':'#5BC0EB',
                    '其他':'#aaa','市集':'#aaa','—':'#ddd','?':'#ccc' }};

    function fmtA(v) {{
      if (!v) return '—';
      return v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(0)+'k':String(v);
    }}

    function renderLoyalistTable() {{
      const tbody = document.getElementById('loyalist-tbody');
      if (!tbody) return;
      const YRS = ['2022','2023','2024','2025'];
      const maxAmt = Math.max(...DATA_LOYALISTS.map(d => d.avgAmount));
      tbody.innerHTML = DATA_LOYALISTS.map(d => {{
        const cells = YRS.map(yr => {{
          if (loyalistView === 'tier') {{
            const t = d.tiers[yr] || '—';
            const c = TCOL[t] || '#ddd';
            return `<td style="text-align:center"><span class="tier-chip" style="background:${{c}}20;color:${{c}}">${{t}}</span></td>`;
          }} else {{
            const amt = d.amounts[yr] || 0;
            const barW = maxAmt > 0 ? Math.round(amt/maxAmt*48) : 0;
            return `<td style="text-align:right;font-size:12px;white-space:nowrap;">
              <span style="display:inline-block;width:${{barW}}px;height:7px;background:#B8860B40;border-radius:2px;margin-right:3px;vertical-align:middle;"></span>${{fmtA(amt)}}
            </td>`;
          }}
        }}).join('');
        const indCell = `<td style="text-align:center;font-size:11px;color:var(--text-muted)">${{d.industry||''}}</td>`;
        const runCell = `<td style="text-align:center;white-space:nowrap"><span style="font-weight:700">${{d.maxRun}}連</span><br><span style="font-size:10px;color:#888">共${{d.totalYears}}年</span></td>`;
        return `<tr><td><strong>${{d.name}}</strong></td>${{indCell}}${{runCell}}${{cells}}<td class="right">NTD ${{fmtA(d.avgAmount)}}</td></tr>`;
      }}).join('');
    }}

    window.toggleLoyalistView = function(view, btn) {{
      loyalistView = view;
      renderLoyalistTable();
      document.querySelectorAll('.loyalist-toggle').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }};

    renderLoyalistTable();

    const loyalistLabelPlugin = {{
      id: 'loyalistLabel',
      afterDatasetsDraw(chart) {{
        const {{ ctx }} = chart;
        const meta = chart.getDatasetMeta(0);
        meta.data.forEach((bar, i) => {{
          const v = chart.data.datasets[0].data[i];
          if (!v) return;
          const lbl = v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(0)+'k':String(v);
          ctx.save(); ctx.textAlign='left'; ctx.font='bold 9px sans-serif'; ctx.fillStyle='#555';
          ctx.fillText(lbl, bar.x+4, bar.y+3.5); ctx.restore();
        }});
      }}
    }};

    new Chart(document.getElementById('loyalistChart'), {{
      type: 'bar',
      data: {{ labels: {names_j}, datasets: [{{ label:'贊助總金額（2022–2025）', data:{amounts_j}, backgroundColor:'#B8860B', borderRadius:4 }}] }},
      plugins: [loyalistLabelPlugin],
      options: {{
        indexAxis:'y', responsive:true, maintainAspectRatio:false,
        layout:{{ padding:{{ right:60 }} }},
        plugins:{{ legend:{{display:false}}, tooltip:{{callbacks:{{label: ctx=>' NTD '+ctx.raw.toLocaleString('zh-TW')}}}} }},
        scales:{{
          x:{{ ticks:{{callback: v=>v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(0)+'k':String(v)}}, grid:{{color:'rgba(0,0,0,0.05)'}} }},
          y:{{ ticks:{{font:{{size:11}}}}, grid:{{display:false}} }}
        }}
      }}
    }});
  }})();
"""
    return html, js

# ── Section A ─────────────────────────────────────────────────────────────────

def section_A(data):
    reliable = [d for d in data if d['reliable']]
    labels_j  = jd([d['label'] for d in data])
    rates_j   = jd([d['rate']  for d in data])
    colors_j  = jd(['#cccccc' if not d['reliable'] else '#4472C4' for d in data])

    # Churn amount chart data (reliable only)
    churn_labels_j  = jd([d['label']        for d in reliable])
    churned_avg_j   = jd([d['churned_avg']   for d in reliable])
    retained_avg_j  = jd([d['retained_avg']  for d in reliable])

    rows = []
    for d in data:
        note = '' if d['reliable'] else ' <span style="font-size:11px;color:var(--text-muted);font-style:italic">（參考）</span>'
        cls  = '' if d['reliable'] else ' class="unreliable"'
        amt_cells = ''
        if d['reliable'] and d['churned_avg'] is not None:
            amt_cells = (
                f'<td class="right" style="color:#c62828">NTD {fmt_ntd(d["churned_avg"])}</td>'
                f'<td class="right" style="color:#2e7d32">NTD {fmt_ntd(d["retained_avg"])}</td>'
            )
        else:
            amt_cells = '<td class="right" colspan="2" style="color:var(--text-muted);font-size:11px">資料不完整</td>'
        rows.append(
            f'<tr{cls}><td>{d["label"]}{note}</td>'
            f'<td class="right">{d["y1_count"]}</td>'
            f'<td class="right">{d["retained"]}</td>'
            f'<td class="right">{d["churned"]}</td>'
            f'<td class="right"><strong>{d["rate"]}%</strong></td>'
            f'{amt_cells}</tr>'
        )

    last_r = next((d for d in reversed(data) if d['reliable']), None)
    last_label = last_r['label'] if last_r else '—'
    last_rate  = last_r['rate']  if last_r else '—'

    html = f"""
  <!-- Section: Analysis A -->
  <div class="section-title">年度留存率趨勢</div>
  <div class="chart-card">
    <h3>每年有多少去年的廠商今年繼續贊助？（2019–2025）</h3>
    <p class="plain-desc">
      留存率 = 去年有贊助的廠商中，今年繼續合作的比例。
      灰色柱子（2019–2021）因原始資料不完整，數字僅供參考。
      <strong>{last_label} 的留存率為 {last_rate}%，是近四年最低點。</strong>
    </p>
    <div style="position:relative;width:100%;height:220px;">
      <canvas id="retentionChart"></canvas>
    </div>

    <h3 style="margin-top:24px">流失廠商 vs 留存廠商——上一年平均贊助金額（2022–2025）</h3>
    <p class="plain-desc">
      若流失廠商的平均金額低於留存廠商，代表高價值廠商的黏著度較高；
      若相近，則說明任何層級廠商都有流失風險，需全面加強關係維護。
    </p>
    <div style="position:relative;width:100%;height:200px;">
      <canvas id="churnAmtChart"></canvas>
    </div>

    <div style="overflow-x:auto;margin-top:16px;">
      <table class="data-table">
        <thead><tr>
          <th>年度</th><th class="right">前年廠商數</th>
          <th class="right">續簽</th><th class="right">流失</th>
          <th class="right">留存率</th>
          <th class="right" style="color:#c62828">流失廠商均額</th>
          <th class="right" style="color:#2e7d32">留存廠商均額</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <div class="action-box">
      <span class="act-icon">📉</span>
      <div><strong>行動建議：</strong>
      留存率下滑是 2026 缺口的主要成因之一。若流失廠商均額接近留存廠商，
      代表需對所有級別加強早期續約溝通；若流失以小額廠商為主，則聚焦挽回大廠即可。
      建議在合約到期前 3 個月主動啟動溝通。</div>
    </div>
  </div>
"""
    js = f"""
  (function() {{
    const retPctPlugin = {{
      id:'retPctLabel',
      afterDatasetsDraw(chart) {{
        const {{ctx}} = chart;
        chart.data.datasets.forEach((ds,di) => {{
          const meta = chart.getDatasetMeta(di);
          meta.data.forEach((bar,i) => {{
            const v = ds.data[i];
            if (!v) return;
            ctx.save(); ctx.textAlign='center'; ctx.font='bold 10px sans-serif';
            ctx.fillStyle='#333'; ctx.fillText(v+'%', bar.x, bar.y-4); ctx.restore();
          }});
        }});
      }}
    }};

    new Chart(document.getElementById('retentionChart'), {{
      type:'bar',
      data:{{ labels:{labels_j}, datasets:[{{ label:'留存率（%）', data:{rates_j}, backgroundColor:{colors_j}, borderRadius:4 }}] }},
      plugins:[retPctPlugin],
      options:{{
        responsive:true, maintainAspectRatio:false,
        layout:{{ padding:{{ top:20 }} }},
        plugins:{{ legend:{{display:false}}, tooltip:{{callbacks:{{label: ctx=>' 留存率：'+ctx.raw+'%'}}}} }},
        scales:{{
          y:{{ max:100, ticks:{{callback: v=>v+'%'}}, grid:{{color:'rgba(0,0,0,0.05)'}} }},
          x:{{ grid:{{display:false}} }}
        }}
      }}
    }});

    const amtLabelPlugin = {{
      id:'amtLabel',
      afterDatasetsDraw(chart) {{
        const {{ctx}} = chart;
        chart.data.datasets.forEach((ds,di) => {{
          const meta = chart.getDatasetMeta(di);
          meta.data.forEach((bar,i) => {{
            const v = ds.data[i];
            if (!v) return;
            const lbl = v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(0)+'k':String(v);
            ctx.save(); ctx.textAlign='center'; ctx.font='bold 9px sans-serif';
            ctx.fillStyle=ds.backgroundColor; ctx.fillText(lbl, bar.x, bar.y-4); ctx.restore();
          }});
        }});
      }}
    }};

    new Chart(document.getElementById('churnAmtChart'), {{
      type:'bar',
      data:{{
        labels:{churn_labels_j},
        datasets:[
          {{ label:'流失廠商（上一年均額）', data:{churned_avg_j}, backgroundColor:'#e8445a', borderRadius:4 }},
          {{ label:'留存廠商（上一年均額）', data:{retained_avg_j}, backgroundColor:'#4472C4', borderRadius:4 }},
        ]
      }},
      plugins:[amtLabelPlugin],
      options:{{
        responsive:true, maintainAspectRatio:false,
        layout:{{ padding:{{ top:22 }} }},
        plugins:{{
          legend:{{ display:true, position:'top', labels:{{font:{{size:12}},usePointStyle:true}} }},
          tooltip:{{callbacks:{{label: ctx=>' '+ctx.dataset.label+': NTD '+ctx.raw.toLocaleString('zh-TW')}}}}
        }},
        scales:{{
          y:{{ ticks:{{callback: v=>v>=1000000?(v/1000000).toFixed(1)+'M':v>=1000?(v/1000).toFixed(0)+'k':String(v)}}, grid:{{color:'rgba(0,0,0,0.05)'}} }},
          x:{{ grid:{{display:false}} }}
        }}
      }}
    }});
  }})();
"""
    return html, js

# ── Section B ─────────────────────────────────────────────────────────────────

def section_B(by_year):
    LOOKBACK = ['2024', '2023', '2022']
    total_all = sum(sum(r['amount_last'] for r in by_year.get(yr, [])) for yr in LOOKBACK)

    def make_rows(grp):
        rows = []
        for d in grp:
            tier_disp = TIER_NORM.get(d['tier_last'], d['tier_last'] or '其他')
            ind_cell = f'<td style="font-size:11px;color:var(--text-muted)">{d["industry"]}</td>' if d.get('industry') else '<td></td>'
            row_style = ' style="opacity:0.65"' if d.get('one_time') else ''
            yrs_cell = (
                f'<td class="right"><span style="color:#aaa;font-size:10px">僅1次 ↓</span></td>'
                if d.get('one_time') else
                f'<td class="right">{d["years_attended"]} 年</td>'
            )
            rows.append(
                f'<tr{row_style}>'
                f'<td style="text-align:center;color:var(--text-muted);font-size:12px">{d["rank"]}</td>'
                f'<td><strong>{d["name"]}</strong></td>'
                f'{ind_cell}'
                f'<td>{tier_badge(tier_disp)}</td>'
                f'<td class="right">NTD {d["amount_last"]:,}</td>'
                f'{yrs_cell}'
                f'<td class="right"><strong>{d["score"]:.1f}</strong></td>'
                f'</tr>'
            )
        return ''.join(rows)

    grp24 = by_year.get('2024', [])
    grp23 = by_year.get('2023', [])
    grp22 = by_year.get('2022', [])

    total24 = sum(r['amount_last'] for r in grp24)
    total23 = sum(r['amount_last'] for r in grp23)
    total22 = sum(r['amount_last'] for r in grp22)

    def year_block(yr, grp, total, open_tag=''):
        if not grp:
            return ''
        label_map = {'2024': '2024 年流失（最高優先）',
                     '2023': '2023 年流失（中期目標）',
                     '2022': '2022 年流失（長期重啟）'}
        return f"""
    <details {open_tag}>
      <summary>▸ {label_map.get(yr,yr+'年流失')}（{len(grp)} 家，上一年合計 NTD {fmt_ntd(total)}）</summary>
      <div style="overflow-x:auto;margin-top:8px;">
        <table class="data-table">
          <thead><tr>
            <th style="text-align:center">#</th><th>廠商名稱</th><th>產業</th><th>類型</th>
            <th class="right">最後金額</th><th class="right">歷年</th><th class="right">優先分</th>
          </tr></thead>
          <tbody>{make_rows(grp)}</tbody>
        </table>
      </div>
    </details>"""

    html = f"""
  <!-- Section: Analysis B -->
  <div class="section-title">流失廠商挽回優先清單</div>
  <div class="chart-card">
    <h3>2022–2024 年曾贊助、但 2025 年未出現的廠商（市集／飯店類已排除）</h3>
    <p class="plain-desc">
      共追蹤 {sum(len(by_year.get(yr,[])) for yr in LOOKBACK)} 家廠商，上一年合計貢獻 NTD {fmt_ntd(total_all)}。
      依最後活躍年度分組，優先聯繫 2024 年流失的廠商，再逐步往前追蹤。
      優先分數 = （金額 ÷ 10,000）×（出席加成）×（類型權重），數字越高越值得優先聯繫。
    </p>
    <div class="note" style="margin-bottom:16px;">
      <strong>優先分數：</strong> 類型權重：鈦金=1.5、銀=1.2、銅=1.0、花車/單買=0.8；出席加成每年+10%，最高+50%；僅參與過一次者分數折半（×0.5），列表中以灰色標示
    </div>
    {year_block('2024', grp24, total24, 'open')}
    {year_block('2023', grp23, total23)}
    {year_block('2022', grp22, total22)}
    <div class="action-box">
      <span class="act-icon">📞</span>
      <div><strong>行動建議：</strong>
      先集中火力挽回 2024 年流失廠商（最近一年），再逐年往前聯繫 2023 及 2022 年流失廠商。
      曾在多年前流失的廠商若重新接洽，建議以新合作形式（升級或特別方案）重新吸引。</div>
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

    badges = (badge_html(s['new'],        '新加入', 'new-badge') +
              badge_html(s['upgraded'],   '升級',   'up')        +
              badge_html(s['stayed'],     '維持',   '')           +
              badge_html(s['downgraded'], '降級',   'down')       +
              badge_html(s['dropped'],    '離開',   'drop'))

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
  <div class="section-title">級別異動 2024 → 2025</div>
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
    <details><summary>▸ 離開廠商（{s['dropped']} 家，已列入挽回清單）</summary>{detail_tbl(data['dropped'])}</details>
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
    labels_j = jd([d['cohort'] for d in data])
    rates_j  = jd([d['rate']   for d in data])
    colors_j = jd(['#cccccc' if not d['reliable'] else '#5BC0EB' for d in data])

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
  <div class="section-title">新廠商隔年存活率</div>
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
    const survPctPlugin = {{
      id:'survPctLabel',
      afterDatasetsDraw(chart) {{
        const {{ctx}} = chart;
        const meta = chart.getDatasetMeta(0);
        meta.data.forEach((bar,i) => {{
          const v = chart.data.datasets[0].data[i];
          if (!v) return;
          ctx.save(); ctx.textAlign='center'; ctx.font='bold 10px sans-serif';
          ctx.fillStyle='#333'; ctx.fillText(v+'%', bar.x, bar.y-4); ctx.restore();
        }});
      }}
    }};
    new Chart(document.getElementById('survivalChart'), {{
      type:'bar',
      data:{{ labels:{labels_j}, datasets:[{{ label:'新廠商隔年存活率（%）', data:{rates_j}, backgroundColor:{colors_j}, borderRadius:4 }}] }},
      plugins:[survPctPlugin],
      options:{{
        responsive:true, maintainAspectRatio:false,
        layout:{{ padding:{{ top:20 }} }},
        plugins:{{ legend:{{display:false}}, tooltip:{{callbacks:{{label: ctx=>' 存活率：'+ctx.raw+'%'}}}} }},
        scales:{{
          y:{{ max:100, ticks:{{callback: v=>v+'%'}}, grid:{{color:'rgba(0,0,0,0.05)'}} }},
          x:{{ grid:{{display:false}} }}
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
  <div class="section-title">贊助收入集中度風險</div>
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
    const concLabelPlugin = {{
      id:'concLabel',
      afterDatasetsDraw(chart) {{
        const {{ctx}} = chart;
        chart.data.datasets.forEach((ds,di) => {{
          if (ds.type === 'line') return;
          const meta = chart.getDatasetMeta(di);
          meta.data.forEach((bar,i) => {{
            const v = ds.data[i];
            if (!v) return;
            ctx.save(); ctx.textAlign='center'; ctx.font='bold 9px sans-serif';
            ctx.fillStyle='#555'; ctx.fillText(v+'%', bar.x, bar.y-4); ctx.restore();
          }});
        }});
      }}
    }};
    new Chart(document.getElementById('concentrationChart'), {{
      type:'bar',
      data:{{
        labels:{years_j},
        datasets:[
          {{ type:'bar',  label:'前 3 家佔比（%）', data:{top3_j}, backgroundColor:'#B8860B', borderRadius:4, yAxisID:'y' }},
          {{ type:'bar',  label:'前 5 家佔比（%）', data:{top5_j}, backgroundColor:'#E8A600', borderRadius:4, yAxisID:'y' }},
          {{ type:'line', label:'HHI 集中度指數',   data:{hhi_j},  borderColor:'#e8445a', backgroundColor:'transparent',
             pointBackgroundColor:'#e8445a', borderWidth:2.5, pointRadius:5, yAxisID:'y2' }},
        ]
      }},
      plugins:[concLabelPlugin],
      options:{{
        responsive:true, maintainAspectRatio:false,
        layout:{{ padding:{{ top:20 }} }},
        plugins:{{
          legend:{{ display:true, position:'top', labels:{{font:{{size:12}},usePointStyle:true}} }},
          tooltip:{{ mode:'index' }}
        }},
        scales:{{
          y:  {{ position:'left',  max:60, ticks:{{callback: v=>v+'%'}}, title:{{display:true,text:'佔總收入比例（%）',font:{{size:11}}}}, grid:{{color:'rgba(0,0,0,0.05)'}} }},
          y2: {{ position:'right', title:{{display:true,text:'HHI 指數',font:{{size:11}}}}, grid:{{display:false}} }},
          x:  {{ grid:{{display:false}} }}
        }}
      }}
    }});
  }})();
"""
    return html, js

# ── Inject into index.html ─────────────────────────────────────────────────────

def inject(html_path, sections, panel_ids):
    html = html_path.read_text()

    # Strip existing analysis panel sections
    START = '\n\n  <div class="tab-panel" id="panel-analysis-d">'
    END   = '\n\n  <div class="tab-panel" id="panel-methodology">'
    if START in html:
        si = html.index(START)
        ei = html.index(END) if END in html else -1
        if ei > si:
            html = html[:si] + '\n' + html[ei:]
            print("Stripped existing analysis sections.")

    # Strip existing analysis JS block
    JS_START = '  /* ANALYSIS_JS_START */'
    JS_END   = '  /* ANALYSIS_JS_END */'
    if JS_START in html and JS_END in html:
        jsi = html.index(JS_START)
        jei = html.index(JS_END) + len(JS_END)
        html = html[:jsi] + html[jei:]

    # Build wrapped panel HTML + JS
    all_html = ''
    all_js   = ''
    for (sec_html, sec_js), pid in zip(sections, panel_ids):
        all_html += f'\n\n  <div class="tab-panel" id="panel-{pid}">\n{sec_html}\n  </div><!-- /panel-{pid} -->'
        all_js   += sec_js

    # Insert HTML before methodology panel
    if END not in html:
        print("ERROR: methodology panel marker not found in index.html")
        return False
    html = html.replace(END, all_html + END, 1)

    # Insert JS before final </script>
    js_block = f'\n  {JS_START}\n{all_js}\n  {JS_END}\n'
    last_script = html.rfind('</script>')
    html = html[:last_script] + js_block + html[last_script:]

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
    print("A — Retention + Churn Amount...")
    rA = analyze_A(dp)
    print("B — Win-back (filtered, multi-year)...")
    rB = analyze_B(dp, id_to_name, ext)
    print("C — Tier Movement...")
    rC = analyze_C(ext)
    print("E — New Entrant Survival...")
    rE = analyze_E(dp)
    print("F — Concentration Risk...")
    rF = analyze_F(dp, id_to_name, ext, cys)

    print("\n=== VERIFICATION ===")
    print(f"[D] Loyalists: {len(rD)}")
    ad = {r['label']: r for r in rA}
    for lbl in ['2022→2023','2023→2024','2024→2025']:
        r = ad.get(lbl)
        if r:
            print(f"[A] {lbl}: {r['rate']}% retained  |  churned_avg={r['churned_avg']}  retained_avg={r['retained_avg']}")
    for yr in ['2024','2023','2022']:
        grp = rB.get(yr, [])
        print(f"[B] {yr} lapsed (excl. mkt/hotel): {len(grp)}")
    s = rC['summary']
    print(f"[C] upgraded={s['upgraded']} stayed={s['stayed']} downgraded={s['downgraded']} dropped={s['dropped']} new={s['new']}")
    ed = {r['cohort']: r['rate'] for r in rE}
    print(f"[E] 2022: {ed.get('2022')}%  2023: {ed.get('2023')}%  2024: {ed.get('2024')}%")

    print("\nGenerating HTML sections...")
    sections = [
        section_D(rD),
        section_A(rA),
        section_B(rB),
        section_C(rC),
        section_E(rE),
        section_F(rF),
    ]
    panel_ids = ['analysis-d','analysis-a','analysis-b','analysis-c','analysis-e','analysis-f']

    ok = inject(BASE / 'index.html', sections, panel_ids)
    if ok:
        print("index.html updated — 6 sections injected.")
    else:
        print("No changes made.")

if __name__ == '__main__':
    main()
