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
            elif RANK[t] < RANK[tier]: downgraded.append({'name': name, 'from': LABEL[tier], 'to': LABEL[t], 'delta': RANK[tier] - RANK[t]})
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

def analyze_E(dp, id_to_name, ext):
    years = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']

    # Tier display mapping for first-year product comparison
    FIRST_TIER = {
        '鈦金級': 'T3 鈦金', '白銀級': 'T3 鈦金', '白金級': 'T3+',
        '銀級': 'T4 銀',
        '銅級': 'T5 銅',
        '花車': '花車/單買', '單買': '花車/單買',
        '友善飯店': '其他', '市集': '其他', '其他': '其他',
    }
    TIER_ORDER = ['T3+', 'T3 鈦金', 'T4 銀', 'T5 銅', '花車/單買', '其他', '不明']

    # Build name→tier lookup per year from ext (for reliable years only)
    name_tier_yr = {}  # {yr: {name_lower: tier_disp}}
    for yr in ['2022', '2023', '2024']:
        name_tier_yr[yr] = {}
        for r in ext.get(yr, []):
            n = r['name_canonical'].lower()
            raw = r.get('tier_orig', '') or ''
            name_tier_yr[yr][n] = FIRST_TIER.get(raw, '不明')

    results = []
    tier_combined = {t: {'new': 0, 'survived': 0} for t in TIER_ORDER}

    for i, yr in enumerate(years[:-1]):
        nxt   = years[i + 1]
        prior = years[:i]
        new_set  = {did for did, v in dp.items()
                    if yr in v and v[yr] and not any(py in v and v[py] for py in prior)}
        survived = sum(1 for did in new_set if nxt in dp[did] and dp[did][nxt])
        rate = survived / len(new_set) * 100 if new_set else 0

        # Product breakdown for reliable cohorts
        if yr in name_tier_yr:
            lookup = name_tier_yr[yr]
            for did in new_set:
                name = id_to_name.get(did, '').lower()
                t = lookup.get(name, '不明')
                did_survived = did in dp and nxt in dp[did] and bool(dp[did][nxt])
                tier_combined[t]['new'] += 1
                if did_survived:
                    tier_combined[t]['survived'] += 1

        results.append({
            'cohort': yr, 'next': nxt,
            'new_count': len(new_set), 'survived': survived,
            'rate': round(rate, 1), 'reliable': yr >= '2022',
        })

    # Filter out empty tiers, keep order
    tier_rows = [
        {'tier': t, **tier_combined[t],
         'rate': round(tier_combined[t]['survived'] / tier_combined[t]['new'] * 100, 1)
                 if tier_combined[t]['new'] else 0}
        for t in TIER_ORDER if tier_combined[t]['new'] > 0
    ]
    return results, tier_rows

# ── Analysis F: Concentration ─────────────────────────────────────────────────

# Reliability flags: 2019–2021 have incomplete per-donor data
_F_RELIABLE = {'2016', '2017', '2018', '2022', '2023', '2024', '2025'}
_F_PARTIAL  = {'2019', '2020', '2021'}

def _donor_amts_yr(d, ext, yr):
    """Return {name: amount} for any year 2016–2025."""
    if yr in ('2022', '2023', '2024', '2025'):
        result = {}
        for r in ext.get(yr, []):
            n = r['name_canonical']
            result[n] = result.get(n, 0) + (r.get('amount') or 0)
        return result
    if yr == '2016':
        return {r['sponsor']: (r.get('total_quote') or 0)
                for r in d['y2016'].get('classification', [])}
    if yr == '2017':
        return {r['sponsor']: (r.get('total_quote') or 0)
                for r in d['y2017'].get('classification', [])}
    if yr == '2018':
        return {r['sponsor_canonical']: (r.get('total_quote') or 0)
                for r in d['y2018'].get('classification', [])}
    if yr == '2019':
        result = {}
        for r in d['y2019'].get('records', []):
            n = r.get('sponsor_canonical', '')
            result[n] = result.get(n, 0) + (r.get('amount') or 0)
        return result
    if yr == '2020':
        result = {}
        for r in d['y2020'].get('records', []):
            n = r.get('sponsor_canonical', '')
            result[n] = result.get(n, 0) + (r.get('amount') or 0)
        return result
    if yr == '2021':
        result = {}
        for group, items in d['y2021'].items():
            for item in items:
                name, amt = item[1], item[3]
                if amt:
                    result[name] = result.get(name, 0) + amt
        return result
    return {}

def analyze_F(dp, id_to_name, ext, cys, d):
    ALL_YEARS = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
    CYS_TOTAL_2021 = 2_120_000  # from cross_year_summary (not in cys file)

    by_year = []
    for yr in ALL_YEARS:
        donor_amts = _donor_amts_yr(d, ext, yr)
        # Authoritative total from cys; fall back to 2021 known total
        if yr in cys:
            total = sum((cys[yr][c].get('amount') or 0) for c in cys[yr] if isinstance(cys[yr][c], dict))
        elif yr == '2021':
            total = CYS_TOTAL_2021
        else:
            total = sum(donor_amts.values())

        sorted_d = sorted(((n, a) for n, a in donor_amts.items() if a > 0), key=lambda x: -x[1])
        top3 = sorted_d[:3]; top5 = sorted_d[:5]
        top3_amt = sum(a for _, a in top3)
        top5_amt = sum(a for _, a in top5)
        hhi = round(sum((a / total * 100) ** 2 for _, a in sorted_d)) if total else 0
        reliable = yr in _F_RELIABLE

        by_year.append({
            'year': yr, 'total': round(total), 'n_donors': len(sorted_d),
            'top3_pct': round(top3_amt / total * 100, 1) if total else 0,
            'top5_pct': round(top5_amt / total * 100, 1) if total else 0,
            'hhi': hhi,
            'top3_names': [n for n, _ in top3],
            'top3_amts':  [round(a) for _, a in top3],
            'reliable': reliable,
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
                delta = item.get('delta', 0)
                if delta == 2:
                    row_style = ' style="background:#FEE8E8;border-left:3px solid #D93025"'
                    badge = '<span style="font-size:10px;color:#D93025;font-weight:700;margin-left:6px">▼▼ 降兩級</span>'
                elif delta == 1:
                    row_style = ' style="background:#FFF8E6;border-left:3px solid #F6B93B"'
                    badge = '<span style="font-size:10px;color:#B8860B;font-weight:700;margin-left:6px">▼ 降一級</span>'
                else:
                    row_style = ''
                    badge = ''
                rows.append(f'<tr{row_style}><td>{item["name"]}</td>'
                            f'<td style="color:#111;font-size:13px">{item["from"]} → {item["to"]}{badge}</td></tr>')
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

def section_E(payload):
    data, tier_rows = payload
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

    # Tier product comparison table (2022–2024 combined)
    def rate_color(r):
        if r >= 40: return '#1B7A3E'
        if r >= 25: return '#F6B93B'
        return '#D93025'

    tier_tbl_rows = []
    for t in tier_rows:
        rc = rate_color(t['rate'])
        tier_tbl_rows.append(
            f'<tr>'
            f'<td><strong>{t["tier"]}</strong></td>'
            f'<td class="right">{t["new"]}</td>'
            f'<td class="right">{t["survived"]}</td>'
            f'<td class="right" style="color:{rc};font-weight:700">{t["rate"]}%</td>'
            f'</tr>'
        )

    html = f"""
  <!-- Section: Analysis E -->
  <div class="section-title">新品牌續約率</div>
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
          <th class="right">隔年續約</th><th class="right">續約率</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>

    <h3 style="margin-top:28px">首年購買類型 vs 隔年續約率（2022–2024 合計）</h3>
    <p class="plain-desc">
      同樣是第一次合作的廠商，簽了哪種合約，決定了他們隔年回來的機率。
    </p>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr>
          <th>首年購買類型</th><th class="right">新廠商數</th>
          <th class="right">隔年續約</th><th class="right">續約率</th>
        </tr></thead>
        <tbody>{''.join(tier_tbl_rows)}</tbody>
      </table>
    </div>
    <p class="plain-desc" style="margin-top:10px">
      ▸ 綠色 ≥ 40%　橘色 25–39%　紅色 &lt; 25%
    </p>

    <div class="action-box">
      <span class="act-icon">🌱</span>
      <div><strong>行動建議：</strong>
      新廠商開發時，優先引導簽訂級別合約（T4 銀以上），而非花車或單次活動，
      因為級別廠商的隔年續約率明顯更高。
      對 2025 年首次贊助的廠商，建立三步跟進：
      ①活動後一個月發感謝函、②三個月電話回訪、③六個月前發出 2026 邀請。</div>
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
    # Bar colors: gray for unreliable years, colored for reliable
    top3_colors_j = jd(['#cccccc' if not d['reliable'] else '#B8860B' for d in by_year])
    top5_colors_j = jd(['#e0e0e0' if not d['reliable'] else '#E8A600' for d in by_year])
    hhi_point_j   = jd(['#cccccc' if not d['reliable'] else '#e8445a' for d in by_year])

    rows = []
    for d in by_year:
        top3_names = '、'.join(d['top3_names'][:3])
        note = '' if d['reliable'] else ' <span style="font-size:10px;color:var(--text-muted);font-style:italic">（參考）</span>'
        row_cls = '' if d['reliable'] else ' class="unreliable"'
        rows.append(
            f'<tr{row_cls}><td>{d["year"]}{note}</td>'
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
    <h3>前幾大廠商佔了多少收入？萬一他們不來了呢？（2016–2025）</h3>
    <p class="plain-desc">
      集中度越高代表我們越依賴少數廠商。HHI 指數是衡量集中度的通用標準，數字越大風險越高
      （1,500 以上屬高度集中）。灰色柱子（2019–2021）因各廠商金額資料不完整，僅供趨勢參考。
    </p>
    <div style="position:relative;width:100%;height:280px;">
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
          {{ type:'bar',  label:'前 3 家佔比（%）', data:{top3_j}, backgroundColor:{top3_colors_j}, borderRadius:4, yAxisID:'y' }},
          {{ type:'bar',  label:'前 5 家佔比（%）', data:{top5_j}, backgroundColor:{top5_colors_j}, borderRadius:4, yAxisID:'y' }},
          {{ type:'line', label:'HHI 集中度指數',   data:{hhi_j},  borderColor:'#e8445a', backgroundColor:'transparent',
             pointBackgroundColor:{hhi_point_j}, borderWidth:2.5, pointRadius:5, yAxisID:'y2' }},
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

# ── Analysis: Gap / Opportunities ─────────────────────────────────────────────

def analyze_opportunities(dp, id_to_name, ext, loyalists_data, winback_data):
    TARGET      = 9_500_000
    ACTUAL_2025 = 8_274_000
    GAP         = TARGET - ACTUAL_2025  # 1,226,000

    # 2026 tier pricing (from 2026 guidebook)
    PRICE_2026 = {
        '白金級': 1_000_000, '黃金級': 700_000, '鈦金級': 450_000,
        '銀級': 220_000, '銅級': 120_000,
    }
    TIER_NEXT = {
        '銅級':  ('銀級',  220_000),
        '銀級':  ('鈦金級', 450_000),
        '鈦金級':('黃金級', 700_000),
    }

    id_to_lower = {did: name.lower() for did, name in id_to_name.items()}
    loyalist_lower = {d['name'].lower() for d in loyalists_data}
    in_2024_lower  = {id_to_lower.get(did, '') for did, v in dp.items()
                      if '2024' in v and v['2024']}

    # 2025 sponsor list
    s25 = {}
    for r in ext.get('2025', []):
        n = r['name_canonical']
        s25[n.lower()] = {'name': n, 'amount': r.get('amount') or 0,
                          'tier': r.get('tier_orig', '')}

    # Segment + renewal forecast
    PROBS   = {'loyalist': 0.85, 'returning': 0.53, 'new_2025': 0.20}
    SEG_LBL = {'loyalist': '忠實廠商（連續 3 年以上）',
                'returning': '回頭廠商（2024 及 2025 皆有）',
                'new_2025':  '新廠商（2025 年首次）'}
    agg = {s: {'n': 0, 'total': 0.0, 'expected': 0.0} for s in PROBS}
    for nl, info in s25.items():
        seg = ('loyalist' if nl in loyalist_lower
               else 'returning' if nl in in_2024_lower
               else 'new_2025')
        agg[seg]['n']        += 1
        agg[seg]['total']    += info['amount']
        agg[seg]['expected'] += info['amount'] * PROBS[seg]
    for seg in agg:
        agg[seg]['total']    = round(agg[seg]['total'])
        agg[seg]['expected'] = round(agg[seg]['expected'])
        agg[seg]['at_risk']  = agg[seg]['total'] - agg[seg]['expected']

    total_expected = sum(v['expected'] for v in agg.values())
    renewal_gap    = TARGET - total_expected

    # B: top win-back (2024 lapsed, non-one-time, top 5)
    top_wb = [r for r in winback_data.get('2024', []) if not r.get('one_time')][:5]
    wb_potential = round(sum(r['amount_last'] for r in top_wb) * 0.35)

    # C: upsell candidates (loyalist or returning, upgradeable tier)
    upsell = []
    for nl, info in s25.items():
        is_stable = nl in loyalist_lower or nl in in_2024_lower
        if not is_stable:
            continue
        t = info['tier']
        if t in TIER_NEXT:
            nt, np = TIER_NEXT[t]
            gain = np - info['amount']
            if gain > 0:
                upsell.append({'name': info['name'], 'curr_tier': t,
                               'next_tier': nt, 'curr_amount': info['amount'],
                               'next_price': np, 'gain': gain})
    upsell.sort(key=lambda x: -x['gain'])
    top_upsell   = upsell[:6]
    upsell_pot   = round(sum(u['gain'] for u in top_upsell) * 0.40)

    # New 2026 items (from guidebook – completely new products)
    new_items = [
        {'name': '活動打卡牆（中型）', 'price': 220_000, 'qty': 2, 'note': '全新品項，2026 年首次推出'},
        {'name': '活動打卡牆（小型）', 'price': 150_000, 'qty': 1, 'note': '全新品項，2026 年首次推出'},
        {'name': '轉播螢幕看板',       'price': 200_000, 'qty': 1, 'note': '現場主螢幕旁平面廣告'},
        {'name': '活動手冊 A6 版位',   'price':  25_000, 'qty': 6, 'note': '中英文各 2,500／1,500 本'},
    ]
    new_items_pot = sum(i['price'] * i['qty'] for i in new_items)

    # D: new prospects (curated estimate)
    new_prospects_pot = 2 * 220_000  # 2 新廠商 at 銀級

    total_proj = total_expected + wb_potential + upsell_pot + new_items_pot + new_prospects_pot

    return {
        'target': TARGET, 'actual_2025': ACTUAL_2025, 'gap': GAP,
        'agg': agg, 'seg_lbl': SEG_LBL, 'probs': PROBS,
        'total_expected': total_expected, 'renewal_gap': renewal_gap,
        'top_wb': top_wb, 'wb_potential': wb_potential,
        'top_upsell': top_upsell, 'upsell_pot': upsell_pot,
        'new_items': new_items, 'new_items_pot': new_items_pot,
        'new_prospects_pot': new_prospects_pot,
        'total_proj': total_proj,
    }


def section_opportunities(data):
    T  = data['target']
    A  = data['actual_2025']
    G  = data['gap']
    agg = data['agg']
    sl  = data['seg_lbl']
    pr  = data['probs']

    te  = data['total_expected']
    rg  = data['renewal_gap']
    wb  = data['wb_potential']
    up  = data['upsell_pot']
    ni  = data['new_items_pot']
    np_ = data['new_prospects_pot']
    tp  = data['total_proj']
    short = T - tp

    # ── Segment table rows ──────────────────────────────────────────────────
    seg_rows = ''
    grand_tot = grand_exp = grand_risk = 0
    for seg in ('loyalist', 'returning', 'new_2025'):
        v = agg[seg]
        pct = pr[seg] * 100
        risk_pct = round(v['at_risk'] / v['total'] * 100) if v['total'] else 0
        seg_rows += (
            f'<tr><td>{sl[seg]}</td>'
            f'<td class="right">{v["n"]}</td>'
            f'<td class="right">NTD {fmt_ntd(v["total"])}</td>'
            f'<td class="right">{pct:.0f}%</td>'
            f'<td class="right" style="color:#1B7A3E;font-weight:700">NTD {fmt_ntd(v["expected"])}</td>'
            f'<td class="right" style="color:#D93025">−NTD {fmt_ntd(v["at_risk"])}（{risk_pct}%）</td>'
            f'</tr>'
        )
        grand_tot  += v['total']
        grand_exp  += v['expected']
        grand_risk += v['at_risk']
    seg_rows += (
        f'<tr style="font-weight:700;border-top:2px solid #ddd">'
        f'<td>合計</td><td class="right">{sum(v["n"] for v in agg.values())}</td>'
        f'<td class="right">NTD {fmt_ntd(grand_tot)}</td><td class="right">—</td>'
        f'<td class="right" style="color:#1B7A3E">NTD {fmt_ntd(grand_exp)}</td>'
        f'<td class="right" style="color:#D93025">−NTD {fmt_ntd(grand_risk)}</td>'
        f'</tr>'
    )

    # ── Win-back table ──────────────────────────────────────────────────────
    wb_rows = ''
    for r in data['top_wb']:
        td = TIER_NORM.get(r['tier_last'], r['tier_last'])
        wb_rows += (
            f'<tr><td><strong>{r["name"]}</strong></td>'
            f'<td style="font-size:11px;color:var(--text-muted)">{r.get("industry","")}</td>'
            f'<td>{tier_badge(td)}</td>'
            f'<td class="right">NTD {r["amount_last"]:,}</td>'
            f'<td class="right">{r["years_attended"]} 年</td></tr>'
        )

    # ── Upsell table ────────────────────────────────────────────────────────
    up_rows = ''
    for u in data['top_upsell']:
        ct = TIER_NORM.get(u['curr_tier'], u['curr_tier'])
        nt = TIER_NORM.get(u['next_tier'], u['next_tier'])
        up_rows += (
            f'<tr><td><strong>{u["name"]}</strong></td>'
            f'<td>{tier_badge(ct)} → {tier_badge(nt)}</td>'
            f'<td class="right">NTD {u["curr_amount"]:,}</td>'
            f'<td class="right">NTD {u["next_price"]:,}</td>'
            f'<td class="right" style="color:#1B7A3E;font-weight:700">+NTD {u["gain"]:,}</td></tr>'
        )

    # ── New items table ─────────────────────────────────────────────────────
    ni_rows = ''
    for item in data['new_items']:
        ni_rows += (
            f'<tr><td><strong>{item["name"]}</strong></td>'
            f'<td class="right">NTD {item["price"]:,}</td>'
            f'<td class="right">{item["qty"]}</td>'
            f'<td class="right" style="color:#1B7A3E;font-weight:700">NTD {item["price"]*item["qty"]:,}</td>'
            f'<td style="font-size:11px;color:var(--text-muted)">{item["note"]}</td></tr>'
        )

    # ── Gap fill waterfall ──────────────────────────────────────────────────
    bar_max = T
    def pct_w(v): return round(v / bar_max * 100, 1)

    short_note = (f'距目標仍差 NTD {fmt_ntd(short)}，須透過更多新廠商或更積極的挽回補足。'
                  if short > 0 else f'已超過目標 NTD {fmt_ntd(-short)}。')

    html = f"""
  <!-- Section: Opportunities -->
  <div class="section-title">機會識別與缺口分析</div>
  <div class="chart-card">

    <!-- Summary header -->
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px;">
      <div style="flex:1;min-width:140px;padding:16px;background:#f8f5f0;border-radius:10px;text-align:center">
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px">2025 年實際收入</div>
        <div style="font-size:22px;font-weight:800">NTD {fmt_ntd(A)}</div>
      </div>
      <div style="flex:1;min-width:140px;padding:16px;background:#e8f5e9;border-radius:10px;text-align:center">
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px">2026 年目標</div>
        <div style="font-size:22px;font-weight:800;color:#1B7A3E">NTD {fmt_ntd(T)}</div>
      </div>
      <div style="flex:1;min-width:140px;padding:16px;background:#fdecea;border-radius:10px;text-align:center">
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px">需新增收入</div>
        <div style="font-size:22px;font-weight:800;color:#D93025">+NTD {fmt_ntd(G)}</div>
      </div>
      <div style="flex:1;min-width:140px;padding:16px;background:#fff8e1;border-radius:10px;text-align:center">
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:4px">預期續約基準</div>
        <div style="font-size:22px;font-weight:800;color:#B8860B">NTD {fmt_ntd(te)}</div>
      </div>
    </div>

    <!-- A: Renewal forecast -->
    <h3 style="margin-top:0">A．現有廠商續約預測</h3>
    <p class="plain-desc">
      依歷史資料，將 2025 年的 {sum(v['n'] for v in agg.values())} 家廠商分為三類，
      各類適用不同的續約機率，估算 2026 年可保住的基本收入。
    </p>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr>
          <th>廠商類型</th><th class="right">家數</th><th class="right">2025 金額</th>
          <th class="right">續約機率</th><th class="right">預期保住</th><th class="right">風險流失</th>
        </tr></thead>
        <tbody>{seg_rows}</tbody>
      </table>
    </div>
    <div class="note" style="margin:12px 0 24px">
      ▸ 機率來源：忠實廠商參考歷史忠誠度估算（85%）；回頭廠商依 2023→2024 留存率（53%）；
      新廠商依首年存活率歷史平均（20%）。
      <br>▸ 預期續約基準 NTD {fmt_ntd(te)}，離 9.5M 目標還差 <strong>NTD {fmt_ntd(rg)}</strong>，
      需要 B／C／D 三個方向補足。
    </div>

    <!-- B: Win-back -->
    <h3>B．流失廠商挽回（2024 年流失，排除市集／飯店）</h3>
    <p class="plain-desc">
      以下為挽回清單優先分最高的 5 家廠商（排除僅參與一次者）。
      假設積極主動聯繫有 35% 的挽回成功率，預計可回收 <strong>NTD {fmt_ntd(wb)}</strong>。
    </p>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>廠商名稱</th><th>產業</th><th>最後類型</th>
          <th class="right">最後金額</th><th class="right">歷年參與</th></tr></thead>
        <tbody>{wb_rows}</tbody>
      </table>
    </div>
    <p class="plain-desc" style="margin-top:8px">
      ▸ 完整挽回清單請至「挽回清單」頁籤查看，共追蹤 57 家廠商。
    </p>

    <!-- C: Upsell -->
    <h3 style="margin-top:24px">C．現有廠商升級潛力（Upsell）</h3>
    <p class="plain-desc">
      2026 手冊升級價格：白金 100萬 ／ 黃金 70萬 ／ 鈦金 45萬 ／ 銀 22萬 ／ 銅 12萬。
      以下為忠實或回頭廠商中，升一個級別後潛在增加金額最大的名單。
      假設 40% 升級成功率，預計可增加 <strong>NTD {fmt_ntd(up)}</strong>。
    </p>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>廠商名稱</th><th>升級路徑</th>
          <th class="right">現行金額</th><th class="right">升級後定價</th>
          <th class="right">可增加</th></tr></thead>
        <tbody>{up_rows}</tbody>
      </table>
    </div>

    <!-- 2026 new items -->
    <h3 style="margin-top:24px">C+．2026 年全新品項（額外收入機會）</h3>
    <p class="plain-desc">
      2026 年企業參與手冊新增以下品項，可向現有及新廠商銷售。若全數售出，預計增加
      <strong>NTD {fmt_ntd(ni)}</strong>。
    </p>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>品項</th><th class="right">單價</th>
          <th class="right">目標數量</th><th class="right">小計</th><th>說明</th></tr></thead>
        <tbody>{ni_rows}</tbody>
      </table>
    </div>

    <!-- D: New prospects -->
    <h3 style="margin-top:24px">D．新廠商引入機會</h3>
    <p class="plain-desc">
      以下廠商目前未在我們的贊助名單中，但其母集團已在其他國家參與 Pride 相關贊助，
      具有較高的接洽成功率。另包含曾有贊助紀錄但已流失、且集團政策支持 DEI 的廠商。
    </p>

    <!-- Lapsed with global backing -->
    <p style="font-weight:700;margin-top:16px;margin-bottom:6px">▸ 曾有合作紀錄、集團支持 DEI（優先重啟）</p>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>廠商</th><th>最後參與</th><th>集團/母公司</th><th>集團 Pride 參與證據</th><th>建議切入點</th></tr></thead>
        <tbody>
          <tr><td><strong>諾和諾德</strong></td><td>2024</td><td>Novo Nordisk（丹麥）</td><td>贊助哥本哈根、紐約、倫敦 Pride；年報揭露 LGBTQ+ ERG</td><td>引用全球集團政策，以永續報告框架切入</td></tr>
          <tr><td><strong>羅氏</strong></td><td>2024</td><td>Roche（瑞士）</td><td>贊助舊金山、蘇黎世 Pride；PRIDE Network 員工群組</td><td>聯繫台灣 HR 或 DEI 負責人，以員工活動角度提案</td></tr>
          <tr><td><strong>GU</strong></td><td>2022</td><td>Fast Retailing（日本）</td><td>UT 系列聯名 ILGA；東京 Rainbow Pride 多年贊助</td><td>強調台灣遊行是東亞規模最大，對標東京 Pride</td></tr>
          <tr><td><strong>Diageo 台灣</strong></td><td>2023</td><td>Diageo（英國）</td><td>Johnnie Walker 彩虹版；贊助全球 30+ Pride 城市</td><td>Johnnie Walker 已在台參與，可提案擴大集團層級</td></tr>
          <tr><td><strong>雅詩蘭黛</strong></td><td>2023</td><td>Estée Lauder（美國）</td><td>MAC Viva Glam 捐款；LGBTQ+ 公益專案多年</td><td>強調台灣是亞洲 Pride 最受國際關注的場域</td></tr>
          <tr><td><strong>渣打銀行</strong></td><td>2022</td><td>Standard Chartered（英國）</td><td>贊助新加坡 Pink Dot；全球 Pride Month 活動</td><td>以金融業 ESG 評分框架切入，強調社會面揭露</td></tr>
          <tr><td><strong>必勝客</strong></td><td>2025 銀</td><td>Yum! Brands（美國）</td><td>Taco Bell 多年 Pride 合作；Yum! 全球 DEI 承諾</td><td>2025 已是銀級，洽談升鈦金或加購打卡牆</td></tr>
        </tbody>
      </table>
    </div>

    <!-- New prospects never participated -->
    <p style="font-weight:700;margin-top:20px;margin-bottom:6px">▸ 從未合作、集團已在海外贊助 Pride（潛在新客）</p>
    <div style="overflow-x:auto;">
      <table class="data-table">
        <thead><tr><th>廠商</th><th>產業</th><th>集團 Pride 參與</th><th>建議切入</th><th>優先級</th></tr></thead>
        <tbody>
          <tr><td><strong>微軟台灣</strong></td><td>科技</td><td>全球 Pride 活動、彩虹 LGBTQ+ ERG、官方聲明</td><td>強調 ESG S 指標、人才吸引</td><td><span style="color:#D93025;font-weight:700">最高</span></td></tr>
          <tr><td><strong>蘋果台灣</strong></td><td>科技</td><td>舊金山 Pride 遊行領頭企業；全球員工 Pride 活動</td><td>台灣是蘋果亞太重點市場</td><td><span style="color:#D93025;font-weight:700">最高</span></td></tr>
          <tr><td><strong>IKEA 台灣</strong></td><td>零售</td><td>IKEA 全球每年推出彩虹聯名商品；贊助歐洲 Pride</td><td>聯名商品授權合作切入</td><td><span style="color:#D93025;font-weight:700">最高</span></td></tr>
          <tr><td><strong>萬事達卡</strong></td><td>金融</td><td>全球 Pride 主要贊助商；彩虹卡設計</td><td>以品牌曝光與 ESG 評分雙角度提案</td><td><span style="color:#F6B93B;font-weight:700">高</span></td></tr>
          <tr><td><strong>Gap 台灣</strong></td><td>服飾</td><td>Gap Inc. 全球 Pride 系列；舊金山 Pride 長期贊助商</td><td>GAP 品牌曾以花車參與，可提案升級至銀級</td><td><span style="color:#F6B93B;font-weight:700">高</span></td></tr>
          <tr><td><strong>漢堡王台灣</strong></td><td>餐飲</td><td>Burger King 美國 Pride Whopper；RBI 全球 DEI 承諾</td><td>餐飲品牌現場行銷角度切入</td><td><span style="color:#888">中</span></td></tr>
          <tr><td><strong>H&M 台灣</strong></td><td>服飾</td><td>H&M 全球彩虹系列；贊助斯德哥爾摩 Pride</td><td>聯名商品 + 現場品牌曝光</td><td><span style="color:#888">中</span></td></tr>
        </tbody>
      </table>
    </div>

    <!-- Gap fill summary -->
    <h3 style="margin-top:28px">缺口填補總覽</h3>
    <div style="overflow-x:auto;margin-bottom:12px;">
      <table class="data-table">
        <thead><tr><th>來源</th><th class="right">預估可增加</th><th>說明</th></tr></thead>
        <tbody>
          <tr><td>A. 續約基準</td><td class="right" style="color:#1B7A3E;font-weight:700">NTD {fmt_ntd(te)}</td><td>歷史留存率估算</td></tr>
          <tr><td>B. 流失廠商挽回（前 5 名 × 35%）</td><td class="right" style="color:#1B7A3E;font-weight:700">+NTD {fmt_ntd(wb)}</td><td>主動外展，可調整挽回家數</td></tr>
          <tr><td>C. 現有廠商升級（前 6 名 × 40%）</td><td class="right" style="color:#1B7A3E;font-weight:700">+NTD {fmt_ntd(up)}</td><td>提案升一個級別</td></tr>
          <tr><td>C+. 新品項銷售</td><td class="right" style="color:#1B7A3E;font-weight:700">+NTD {fmt_ntd(ni)}</td><td>打卡牆、看板、手冊等新品項</td></tr>
          <tr><td>D. 新廠商引入（2 家 銀級估算）</td><td class="right" style="color:#1B7A3E;font-weight:700">+NTD {fmt_ntd(np_)}</td><td>全新合作廠商</td></tr>
          <tr style="font-weight:700;border-top:2px solid #ddd">
            <td>合計預測</td>
            <td class="right" style="color:{'#1B7A3E' if tp >= T else '#D93025'};font-weight:800">NTD {fmt_ntd(tp)}</td>
            <td>{'已達標 ✓' if tp >= T else f'距目標 {fmt_ntd(short)}'}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="plain-desc">{short_note}</p>

    <div class="action-box">
      <span class="act-icon">🎯</span>
      <div><strong>行動建議：</strong>
      優先確保 21 家忠實廠商全數續約（保住 3.2M 基礎），
      再集中火力聯繫前 5 名流失廠商（預計回收 {fmt_ntd(wb)}）；
      同步向有升級空間的廠商提出鈦金／銀級方案，
      並積極行銷打卡牆等 2026 新品項。
      若全部達成，加上引入 2 家新廠商，可達到 <strong>NTD {fmt_ntd(tp)}</strong>。
      </div>
    </div>
  </div>
"""
    return html, ''


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
    rE = analyze_E(dp, id_to_name, ext)
    print("F — Concentration Risk...")
    rF = analyze_F(dp, id_to_name, ext, cys, d)
    print("Gap / Opportunities...")
    rO = analyze_opportunities(dp, id_to_name, ext, rD, rB)

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
    ed = {r['cohort']: r['rate'] for r in rE[0]}
    print(f"[E] 2022: {ed.get('2022')}%  2023: {ed.get('2023')}%  2024: {ed.get('2024')}%")
    for t in rE[1]:
        print(f"[E] tier {t['tier']}: {t['new']} new, {t['survived']} survived, {t['rate']}%")

    print(f"[O] Projected 2026: NTD {rO['total_proj']:,}  (gap={rO['renewal_gap']:,} after renewals)")

    print("\nGenerating HTML sections...")
    sections = [
        section_D(rD),
        section_A(rA),
        section_B(rB),
        section_C(rC),
        section_E(rE),
        section_F(rF),
        section_opportunities(rO),
    ]
    panel_ids = ['analysis-d','analysis-a','analysis-b','analysis-c','analysis-e','analysis-f','opportunities']

    ok = inject(BASE / 'index.html', sections, panel_ids)
    if ok:
        print("index.html updated — 7 sections injected.")
    else:
        print("No changes made.")

if __name__ == '__main__':
    main()
