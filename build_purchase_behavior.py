#!/usr/bin/env python3
"""Build purchase_behavior.json from 2019/2020 classified JSONs + all_extracted_v2.json"""
import json

TIER_VALS   = {'白金級', '黃金級', '白銀級', '鈦金級', '銀級', '銅級'}
SINGLE_VALS = {'花車', '單買', '車', '車（頭車）', '車（普通）'}

def categorize(tier_orig):
    if not tier_orig:
        return 'OTHER'
    t = tier_orig.strip()
    if t == '友善飯店':
        return 'HOTEL'
    if t in TIER_VALS:
        return 'TIER'
    if t in SINGLE_VALS or '車' in t or '花車' in t or '單買' in t:
        return 'SINGLE'
    if '市集' in t:
        return 'MARKET'
    return 'OTHER'

def short_tier(tier_orig, master_tier):
    """Return a short display label."""
    if tier_orig in {'白金級'}:           return 'T1 白金'
    if tier_orig in {'黃金級'}:           return 'T2 黃金'
    if tier_orig in {'白銀級'}:           return 'T3 白銀'
    if tier_orig in {'鈦金級'}:           return 'T3 鈦金'
    if tier_orig in {'銀級'}:             return 'T4 銀'
    if tier_orig in {'銅級'}:             return 'T5 銅'
    if master_tier in {'T1'}:            return 'T1'
    if master_tier in {'T2'}:            return 'T2'
    if master_tier in {'T3'}:            return 'T3'
    if master_tier in {'T4'}:            return 'T4'
    if master_tier in {'T5'}:            return 'T5'
    return ''

# Build name → donor_id lookup from id_state.json
with open('id_state.json', encoding='utf-8') as f:
    id_state = json.load(f)
name_to_id = {name: did for name, did in id_state['all_donors'].items()}

data = {}  # canonical_name → {donor_id, name, years: {yr: {cat, label, amount}}}

def add_record(name, donor_id, year, tier_orig, master_tier, amount):
    cat = categorize(tier_orig)
    if cat == 'HOTEL':
        return  # exclude hotel donors entirely
    if name not in data:
        did = donor_id or name_to_id.get(name)
        data[name] = {'donor_id': did, 'name': name, 'years': {}}
    single_label = (tier_orig or '').strip()
    # Normalize verbose vehicle names
    if single_label == '車（頭車）': single_label = '頭車'
    elif single_label in ('車（普通）', '車'): single_label = '花車'
    label = short_tier(tier_orig, master_tier) if cat == 'TIER' else (
            single_label or '單購' if cat == 'SINGLE' else
            '市集' if cat == 'MARKET' else '其他')
    data[name]['years'][str(year)] = {
        'cat': cat,
        'label': label,
        'amount': int(amount) if amount else 0,
    }

# ── 2019 ─────────────────────────────────────────────────────────────────────
with open('2019_classified.json', encoding='utf-8') as f:
    d19 = json.load(f)
for r in d19['records']:
    name = r.get('sponsor_canonical') or ''
    if not name:
        continue
    add_record(
        name,
        r.get('donor_id'),
        2019,
        r.get('tier_orig') or r.get('original_tier'),
        r.get('master_tier'),
        r.get('amount') or 0,
    )

# ── 2020 ─────────────────────────────────────────────────────────────────────
with open('2020_classified.json', encoding='utf-8') as f:
    d20 = json.load(f)
for r in d20['records']:
    name = r.get('sponsor_canonical') or ''
    if not name:
        continue
    add_record(
        name,
        r.get('donor_id'),
        2020,
        r.get('tier_orig'),
        r.get('master_tier'),
        r.get('amount') or 0,
    )

# ── 2022–2025 ────────────────────────────────────────────────────────────────
with open('all_extracted_v2.json', encoding='utf-8') as f:
    d_all = json.load(f)
for yr_str, recs in d_all.items():
    yr = int(yr_str)
    for r in recs:
        name = r.get('name_canonical') or ''
        if not name:
            continue
        add_record(
            name,
            r.get('donor_id'),
            yr,
            r.get('tier_orig'),
            r.get('master_tier'),
            r.get('amount') or 0,
        )

# ── Post-process: remove hotel-named donors (by name pattern) ────────────────
HOTEL_KEYWORDS = ['飯店', '酒店', '旅館', '旅店', 'hotel', 'Hotel', 'inn', 'Inn']
to_delete = []
for name, rec in data.items():
    if any(kw in name for kw in HOTEL_KEYWORDS):
        to_delete.append(name)
for name in to_delete:
    del data[name]
print(f'Removed {len(to_delete)} hotel-named donors: {to_delete}')

# ── Remove market-only donors ─────────────────────────────────────────────────
to_delete = []
for name, rec in data.items():
    cats = {v['cat'] for v in rec['years'].values()}
    if cats <= {'MARKET', 'OTHER'}:  # never had TIER or SINGLE
        to_delete.append(name)
for name in to_delete:
    del data[name]
print(f'Removed {len(to_delete)} market/other-only donors: {to_delete}')

# ── Remove donors with only 1 year of data ────────────────────────────────────
to_delete = [name for name, rec in data.items() if len(rec['years']) < 2]
for name in to_delete:
    del data[name]
print(f'Removed {len(to_delete)} single-year donors')

# ── Sort by total years desc, then name ──────────────────────────────────────
sorted_data = dict(sorted(data.items(), key=lambda x: (-len(x[1]['years']), x[0])))

# ── Write output ──────────────────────────────────────────────────────────────
with open('purchase_behavior.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

# ── Print summary ─────────────────────────────────────────────────────────────
tier_only  = [n for n, r in sorted_data.items() if all(v['cat']=='TIER'   for v in r['years'].values())]
single_only= [n for n, r in sorted_data.items() if all(v['cat']=='SINGLE' for v in r['years'].values())]
switchers  = [n for n, r in sorted_data.items() if
              any(v['cat']=='TIER' for v in r['years'].values()) and
              any(v['cat']=='SINGLE' for v in r['years'].values())]

print(f'\nTotal donors: {len(sorted_data)}')
print(f'  TIER-only:   {len(tier_only)}')
print(f'  SINGLE-only: {len(single_only)}')
print(f'  Switchers:   {len(switchers)} — {switchers}')
print(f'\nWrote purchase_behavior.json')
