#!/usr/bin/env python3
"""Build cohort_2025.json: 2025 new entrants + returning buyer year-over-year comparison"""
import json

HOTEL_KW  = ['飯店', '酒店', '旅館', '旅店', 'hotel', 'Hotel', 'HotelCom']
TIER_VALS  = {'白金級', '黃金級', '白銀級', '鈦金級', '銀級', '銅級'}
SINGLE_VALS = {'花車', '單買', '車', '車（頭車）', '車（普通）'}

def categorize(tier_orig):
    if not tier_orig: return 'OTHER'
    t = tier_orig.strip()
    if t == '友善飯店': return 'HOTEL'
    if t in TIER_VALS:  return 'TIER'
    if t in SINGLE_VALS or '車' in t: return 'SINGLE'
    if '市集' in t:     return 'MARKET'
    return 'OTHER'

def short_label(tier_orig):
    MAP = {'白金級':'T1 白金','黃金級':'T2 黃金','白銀級':'T3 白銀','鈦金級':'T3 鈦金',
           '銀級':'T4 銀','銅級':'T5 銅','花車':'花車','單買':'單買','車':'車'}
    return MAP.get((tier_orig or '').strip(), tier_orig or '其他')

def is_hotel(name):
    return any(kw in name for kw in HOTEL_KW)

# Load all data
with open('all_extracted_v2.json', encoding='utf-8') as f:
    d_all = json.load(f)
with open('2019_classified.json', encoding='utf-8') as f:
    d19 = json.load(f)
with open('2020_classified.json', encoding='utf-8') as f:
    d20 = json.load(f)

# Build full history: name -> {yr: {cat, tier_orig, label, amount}}
history = {}

def add(name, yr, tier_orig, amount):
    c = categorize(tier_orig)
    if c == 'HOTEL' or is_hotel(name): return
    history.setdefault(name, {})[yr] = {
        'cat': c, 'tier_orig': tier_orig or '',
        'label': short_label(tier_orig), 'amount': int(amount or 0)
    }

for r in d19['records']:
    n = r.get('sponsor_canonical', '')
    if n: add(n, 2019, r.get('tier_orig') or r.get('original_tier'), r.get('amount', 0))

for r in d20['records']:
    n = r.get('sponsor_canonical', '')
    if n: add(n, 2020, r.get('tier_orig'), r.get('amount', 0))

for yr_str, recs in d_all.items():
    for r in recs:
        n = r.get('name_canonical', '')
        if n: add(n, int(yr_str), r.get('tier_orig'), r.get('amount', 0))

# Identify 2025 new vs returning
new_2025 = []
returning_2025 = []

for name, yrs in history.items():
    if 2025 not in yrs: continue
    curr = yrs[2025]
    if curr['cat'] == 'HOTEL': continue
    prior_yrs = sorted([y for y in yrs if y != 2025])
    if not prior_yrs:
        new_2025.append({
            'name': name, 'cat': curr['cat'],
            'label': curr['label'], 'amount': curr['amount'],
        })
    else:
        last_yr  = prior_yrs[-1]
        prev     = yrs[last_yr]
        prev_cat = prev['cat']
        curr_cat = curr['cat']
        if prev_cat == 'HOTEL': continue
        if prev_cat == curr_cat:
            change_type = 'same'
        elif prev_cat == 'SINGLE' and curr_cat == 'TIER':
            change_type = 'upgrade'
        elif prev_cat == 'TIER' and curr_cat == 'SINGLE':
            change_type = 'downgrade'
        else:
            change_type = 'other'
        returning_2025.append({
            'name': name,
            'prev_yr': last_yr, 'prev_cat': prev_cat, 'prev_label': prev['label'],
            'curr_cat': curr_cat, 'curr_label': curr['label'], 'curr_amount': curr['amount'],
            'change_type': change_type,
        })

# Sort
new_2025.sort(key=lambda x: -x['amount'])
returning_2025.sort(key=lambda x: ['upgrade','same','other','downgrade'].index(x['change_type']) * 1000 - x['curr_amount'])

out = {'new_2025': new_2025, 'returning_2025': returning_2025}
with open('cohort_2025.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# Summary
same     = [r for r in returning_2025 if r['change_type'] == 'same']
upgrades = [r for r in returning_2025 if r['change_type'] == 'upgrade']
downgrades=[r for r in returning_2025 if r['change_type'] == 'downgrade']
others   = [r for r in returning_2025 if r['change_type'] == 'other']

print(f'2025 new entrants : {len(new_2025)}')
print(f'2025 returning    : {len(returning_2025)}')
print(f'  same product    : {len(same)}')
print(f'  upgraded (S→T)  : {len(upgrades)}  — {[r["name"] for r in upgrades]}')
print(f'  downgraded (T→S): {len(downgrades)} — {[r["name"] for r in downgrades]}')
print(f'  other change    : {len(others)}   — {[r["name"] for r in others]}')
print('\nWrote cohort_2025.json')
