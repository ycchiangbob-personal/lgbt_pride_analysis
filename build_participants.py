"""
Build parade participants dataset by parsing the MD file and cross-referencing donor registry.
Outputs a JSON file: parade_participants.json
"""
import json
import re
from collections import defaultdict

BASE = '/Users/yanchenchiang/Documents/Claude/Projects/lgbt pride 2026'

with open(f'{BASE}/id_state.json') as f:
    id_state = json.load(f)
with open(f'{BASE}/donor_presence.json') as f:
    donor_presence = json.load(f)
with open(f'{BASE}/all_extracted_v2.json') as f:
    all_extracted = json.load(f)

donor_registry = id_state['all_donors']  # name -> donor_id

# Reverse map: donor_id -> list of canonical names (first one is primary)
id_to_names = defaultdict(list)
for name, did in donor_registry.items():
    id_to_names[did].append(name)

# Industry lookup: donor_id -> industry (from all_extracted_v2 records)
industry_lookup = {}
for year, records in all_extracted.items():
    for r in records:
        canonical = r.get('name_canonical', '')
        industry = r.get('industry', '')
        if canonical and industry:
            did = donor_registry.get(canonical)
            if did and did not in industry_lookup:
                industry_lookup[did] = industry

# Tier lookup: donor_id -> {year: tier}
tier_lookup = defaultdict(dict)
for year, records in all_extracted.items():
    for r in records:
        canonical = r.get('name_canonical', '')
        tier = r.get('tier_orig', '')
        if canonical and tier:
            did = donor_registry.get(canonical)
            if did:
                tier_lookup[did][year] = tier

# Parse MD file for parade participants
with open(f'{BASE}/taiwan-pride-parade-teams-2019-2025.md') as f:
    md_content = f.read()

# Manual alias map to connect MD names -> donor_id
# Format: raw_md_name -> donor_id
MANUAL_MAP = {
    # 商業車 commercial float sponsors
    '吉立亞醫藥': 'D0028',
    'Gilead 吉立亞醫藥': 'D0028',
    'Gilead': 'D0028',
    '渣打銀行': 'D0156',
    'Lespark': 'D0006',
    'LesPark': 'D0006',
    '拉拉公園': 'D0006',
    'AstraZeneca（AZ）': 'D0085',
    'AstraZeneca': 'D0085',
    '臺灣阿斯特捷利康': 'D0085',
    '臺灣阿斯特捷利康（AstraZeneca）': 'D0085',
    '阿斯特捷利康藥廠（AstraZeneca, AZ）': 'D0085',
    '臺虎精釀': 'D0062',
    '聯合利華': 'D0058',
    'GSK': 'D0052',
    'GSK Taiwan': 'D0052',
    'gsk': 'D0052',
    'Google': 'D0037',
    'Pride at Google Taiwan': 'D0037',
    'Pride@Google': 'D0037',
    'GAP': 'D0020',
    'GAP Taiwan': 'D0020',
    '台灣蓋璞': 'D0020',
    'NIKE': 'D0097',
    'Nike': 'D0097',
    'Uber': 'D0017',
    'Uber｜Uber Eats': 'D0017',
    'Tapestry': 'D0144',
    'Pride@tsmc': 'D0195',
    'VERVE': 'D0117',
    'Gstar': 'D0032',
    'G*star': 'D0032',
    'G*Star': 'D0032',
    'GSTAR': 'D0032',
    '諾億保經': 'D0190',
    '諾億財富管理顧問': 'D0116',
    '弗里德里希諾曼自由基金會': None,  # NGO, no donor ID
    'Pizza Hut': 'D0128',
    '必勝客': 'D0128',
    '諾億保險經紀人': 'D0190',
    '羅氏大藥廠與羅氏醫療診斷設備': 'D0115',
    '荷瑞紐澳 驕傲同行（Proud Together AU NL NZ SE）': None,
    '彩虹酷兒': 'D0022',
    '彩虹酷兒健康文化中心': 'D0022',
    '犀牛盾 RHINOSHIELD': 'D0163',
    'RHINOSHIELD': 'D0163',
    'JLR Taiwan 台灣捷豹路虎': 'D0148',
    'Zenyum': 'D0160',
    '歐肯單一麥芽蘇格蘭威士忌': None,
    '金賓美國波本威士忌': None,
    '法國巴黎人壽': 'D0157',
    'GU': 'D0146',
    '高誠公關': 'D0092',
    '高誠公關 GOLIN Taipei': 'D0092',
    '高誠公關GOLIN': 'D0092',
    'Fusion 聚變': 'D0158',
    '愛無界 Love Beyond Boundaries': None,
    '50% FIFTY PERCENT': 'D0079',
    '磊山保經 諾億團隊': 'D0094',
    '磊山保經諾億團隊': 'D0094',
    '雙全國際股份有限公司': None,
    'lululemon Taiwan': 'D0082',
    'G*STAR': 'D0032',
    '臺北市觀光傳播局': 'D0088',
    'GagaOOLala LGBTQ+ & BL線上影音平台': 'D0025',
    'PANGU by Kenal X Durex': 'D0118',
    'GroupM': 'D0122',
    'La Crema': 'D0127',
    '台灣保時捷車業股份有限公司 \nPorsche Taiwan Motors Limited': 'D0126',
    'Porsche Taiwan Motors Limited': 'D0126',
    '台灣保時捷車業股份有限公司 Porsche Taiwan Motors Limited': 'D0126',
    '臺虎精釀': 'D0062',
    'VIETJET': 'D0129',
    '諾和諾德藥品股份有限公司（Novo Nordisk）': 'D0112',
    '台灣諾和諾德藥品股份有限公司（Novo Nordisk）': 'D0112',
    '美商百富門': 'D0120',
    'Flyingv': None,
    'Tinder': 'D0054',
    '磊山保經諾億團隊': 'D0094',
    '彩虹酷兒健康文化中心': 'D0022',
    'Unilever 聯合利華股份有限公司': 'D0058',
    'Unilever': 'D0058',
    'foodpanda': 'D0057',
    'Foodpanda': 'D0057',
    'Klook 客路': 'D0061',
    'KLOOK 客路': 'D0061',
    'Gilead Sciences 吉立亞醫藥': 'D0028',
    'Formosa Pride': None,
    'GagaOOLala 屬於你的故事': 'D0025',
    'Grindr': 'D0042',
    'LesPark 拉拉公園': 'D0006',
    'T-STUDIO x PAR.T': 'D0034',
    '彩虹酷兒健康文化中心': 'D0022',
    '哈利男孩 x G-BOT TAIWAN': 'D0043',
    '#最挺你的外送平台 Deliveroo': 'D0029',
    'Deliveroo': 'D0029',
    'SONY Pictures 索尼影業': 'D0065',
    'Sony Pictures 索尼影業': 'D0065',
    '獨角落': 'D0063',
    'Maryjane Pizza': 'D0064',
    '瑪莉珍比薩': 'D0064',
    'GOLIN': 'D0066',
    'Biogen 台灣百健': 'D0056',
    '台灣百健': 'D0056',
    'GAP（台灣蓋璞）': 'D0020',
    'Biogen台灣百健': 'D0056',
    'Gilead吉立亞醫藥': 'D0028',
    'Gilead 吉立亞醫藥': 'D0028',
    '雷醫國際股份有限公司': 'D0121',
    'Prism 三稜鏡學生聯盟': None,  # Student alliance, not a donor
    # Lespark variants
    'Lespark': 'D0006',
    # More variants found in MD
    '吉立亞醫藥（Gilead）': 'D0028',
    '臺灣阿斯特捷利康股份有限公司': 'D0085',
    '美國高通公司': 'D0091',
    '飛比 Feebee': 'D0113',
    '飛比 feebee': 'D0113',
    '台灣樂天集團': 'D0093',
    '磊山保經 諾億團隊': 'D0094',
    'ModelTV 影音串流平台': 'D0081',
    'G.star': 'D0032',
    '台灣酷蓋 / Lez\'s Meeting 女人國 / mojumojo': None,
    'Mx.Me 覓我 交友軟體 / DOUBLE 束胸': None,
    'We are GYEE': None,
    'playing Gayly': None,
    '霹靂嬌娃 Charlie\'s Angels': None,
    'Google Gaygler': 'D0037',
    'Monocorn 獨角獸': None,
    '雙全國際股份有限公司': None,
    'TPO': None,
    '無心戒酒互助會': 'D0108',
    '亞曼瑞國際舞蹈學校': None,
    '歐肯單一麥芽蘇格蘭威士忌': None,
    '金賓美國波本威士忌': None,
    '愛無界 Love Beyond Boundaries': None,
    '弗里德里希諾曼自由基金會': None,
    'Prism 三稜鏡學生聯盟': None,
    'Formosa Pride': None,
    '荷瑞紐澳 驕傲同行（Proud Together AU NL NZ SE）': None,
}

def normalize(name):
    """Basic normalization for matching."""
    return re.sub(r'\s+', '', name).lower()

# Build normalized lookup from donor_registry
norm_to_id = {normalize(k): v for k, v in donor_registry.items()}

def find_donor_id(raw_name):
    """Try to find donor_id for a raw MD name."""
    name = raw_name.strip()

    # 1. Manual map
    if name in MANUAL_MAP:
        return MANUAL_MAP[name]

    # 2. Direct registry lookup
    if name in donor_registry:
        return donor_registry[name]

    # 3. Normalized lookup
    norm = normalize(name)
    if norm in norm_to_id:
        return norm_to_id[norm]

    # 4. Try removing parenthetical content
    name_clean = re.sub(r'[（(].*?[）)]', '', name).strip()
    if name_clean in donor_registry:
        return donor_registry[name_clean]
    if normalize(name_clean) in norm_to_id:
        return norm_to_id[normalize(name_clean)]

    return None

# Parse MD by year
# Split into year blocks
year_pattern = re.compile(r'## (\d{4}) 年（第 \d+ 屆）')
splits = year_pattern.split(md_content)

# splits: ['intro', '2025', 'content_2025', '2024', 'content_2024', ...]
year_blocks = {}
for i in range(1, len(splits), 2):
    year = int(splits[i])
    content = splits[i+1]
    year_blocks[year] = content

# For each year, parse 商業車 sections (with team color context)
# Structure:
# parade_entries[year] = [
#   {'raw_name': ..., 'donor_id': ..., 'section': '商業車', 'team': '紅色大隊'}
# ]
parade_entries = defaultdict(list)

for year, content in sorted(year_blocks.items()):
    # Split by team color sections
    team_pattern = re.compile(r'###\s+(.*?大隊.*?)\n')
    team_splits = team_pattern.split(content)
    # [content_before_first_team, team1_name, team1_content, team2_name, ...]

    for j in range(1, len(team_splits), 2):
        team_name = team_splits[j].strip()
        team_content = team_splits[j+1] if j+1 < len(team_splits) else ''

        # Find 商業車 line
        commercial_match = re.search(r'\*\*商業車：\*\*\s*([^\n]+)', team_content)
        if commercial_match:
            line = commercial_match.group(1).strip()
            # Split by 、and comma
            sponsors = re.split(r'[、，,]', line)
            for sponsor in sponsors:
                sponsor = sponsor.strip()
                if not sponsor:
                    continue
                did = find_donor_id(sponsor)
                parade_entries[year].append({
                    'raw_name': sponsor,
                    'donor_id': did,
                    'section': '商業車',
                    'team': team_name
                })

        # Also parse 隊伍 for known donors
        team_match = re.search(r'\*\*隊伍：\*\*\s*([^\n]+)', team_content)
        if team_match:
            line = team_match.group(1).strip()
            # Split by 、
            groups = re.split(r'[、，,]', line)
            for group in groups:
                group = group.strip()
                if not group:
                    continue
                did = find_donor_id(group)
                if did:  # Only include if we can match to a donor
                    # Avoid duplicates with 商業車 section
                    already_added = any(
                        e['donor_id'] == did and e['year'] == year
                        for e in parade_entries[year]
                        if 'year' in e
                    )
                    # Check within year entries
                    existing_ids = [e['donor_id'] for e in parade_entries[year] if e['donor_id']]
                    if did not in existing_ids:
                        parade_entries[year].append({
                            'raw_name': group,
                            'donor_id': did,
                            'section': '隊伍',
                            'team': team_name
                        })

# Now build the unified participant dataset
# participant_map: donor_id -> participant record
participant_map = {}

# First, seed from all known donors in donor_presence
for did in donor_presence.keys():
    canonical = id_to_names[did][0] if id_to_names[did] else did
    donor_yrs = sorted([int(y) for y in donor_presence[did].keys()])
    participant_map[did] = {
        'donor_id': did,
        'name': canonical,
        'aliases': id_to_names[did][1:] if len(id_to_names[did]) > 1 else [],
        'industry': industry_lookup.get(did, ''),
        'first_donor_year': min(donor_yrs) if donor_yrs else None,
        'donor_years': donor_yrs,
        'first_parade_year': None,
        'parade_detail': {},  # year -> {raw_name, section, team}
    }

# Now fill in parade data from MD parsing
for year, entries in parade_entries.items():
    for entry in entries:
        did = entry['donor_id']
        if did and did in participant_map:
            p = participant_map[did]
            if year not in p['parade_detail']:
                p['parade_detail'][year] = {
                    'raw_name': entry['raw_name'],
                    'section': entry['section'],
                    'team': entry['team']
                }
            # Update first_parade_year
            if p['first_parade_year'] is None or year < p['first_parade_year']:
                p['first_parade_year'] = year
        elif did is None:
            # Unknown name from MD - skip for now (no donor ID)
            pass

# Also add entries from MD that have NO donor ID match (for completeness)
# These are commercial sponsors without a D-number yet
unmatched_parade = {}
for year, entries in parade_entries.items():
    for entry in entries:
        if entry['donor_id'] is None:
            raw = entry['raw_name']
            if raw not in unmatched_parade:
                unmatched_parade[raw] = {
                    'donor_id': None,
                    'name': raw,
                    'aliases': [],
                    'industry': '',
                    'first_donor_year': None,
                    'donor_years': [],
                    'first_parade_year': year,
                    'parade_detail': {}
                }
            p = unmatched_parade[raw]
            if year not in p['parade_detail']:
                p['parade_detail'][year] = {
                    'raw_name': raw,
                    'section': entry['section'],
                    'team': entry['team']
                }
            if p['first_parade_year'] is None or year < p['first_parade_year']:
                p['first_parade_year'] = year

# Combine all into final list
final_list = []

# Donors with some parade presence OR donor years
for did, p in participant_map.items():
    p['parade_years'] = sorted(p['parade_detail'].keys())
    final_list.append(p)

# Unmatched MD entries (no donor ID)
for raw, p in unmatched_parade.items():
    p['parade_years'] = sorted(p['parade_detail'].keys())
    final_list.append(p)

# Sort by donor_id (put None at end)
def sort_key(p):
    did = p['donor_id']
    if did is None:
        return ('Z', 9999)
    return ('A', int(did[1:]))

final_list.sort(key=sort_key)

# Print stats
donors_with_parade = sum(1 for p in final_list if p['donor_id'] and p['first_parade_year'])
donors_only = sum(1 for p in final_list if p['donor_id'] and not p['first_parade_year'])
parade_only = sum(1 for p in final_list if not p['donor_id'] and p['first_parade_year'])

print(f'Total records: {len(final_list)}')
print(f'Donors with parade record: {donors_with_parade}')
print(f'Donors without parade record: {donors_only}')
print(f'Parade-only (no donor ID): {parade_only}')
print()
print('Unmatched MD commercial sponsors:')
for raw in unmatched_parade:
    print(f'  "{raw}"')

# Collect unique industries
industries = sorted(set(p['industry'] for p in final_list if p['industry']))
print('\nIndustries:', industries)

# Save output
with open(f'{BASE}/parade_participants.json', 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)
print('\nSaved to parade_participants.json')
