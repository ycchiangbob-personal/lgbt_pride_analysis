# 臺灣同志遊行 商業贊助資料庫 — Project Context

## Project Overview
Building a 2016–2025 Taiwan LGBT Pride commercial sponsorship database for growth analysis toward 2026.

## Data Location
All state files live in the project root (same folder as this CLAUDE.md).

## Key State Files
- `cross_year_summary.json` — master aggregate (9 years × 4 categories)
- `id_state.json` — donor registry D0001–D0229, next = D0230
- `donor_presence.json` — donor × year presence matrix (212 donors)
- `all_extracted_v2.json` — per-sponsor detail for 2022–2025
- `2021_final.json` — 2021 confirmed sponsor list (29 sponsors)
- `pending_issues.json` — remaining L-grade classification issues
- `2019_classified.json` / `2020_classified.json` — earlier year details
- `2016_classified_v2.json` / `2017_classified.json` / `2018_classified_v2.json`

## Classification Rules (finalized, do not change without explicit instruction)

### Four Categories
| Code | Name | Includes |
|---|---|---|
| 級別贊助 | Tier sponsorship | 白金/黃金/白銀/鈦金/銀/銅級 |
| 單購 | Single purchase | 單買、花車 |
| 市集 | Market booth | 彩虹市集（獨立棚 20k/頂、合併棚 10k/頂）|
| 其他 | Other | 友善飯店、未分級、聯盟/協會型、跨界合作 |

### Amount Rules
- Use contract/quoted price, not received amount
- Unpaid unless explicitly cancelled = include
- Government subsidies = exclude
- 0-amount sponsors = include in count, mark as in-kind
- 友善飯店 = 其他 (not 單購)
- NGO booths = not counted as revenue

### Market Booth Pricing (2024/2025)
- 獨立棚: NTD 20,000/頂
- 合併棚: NTD 10,000/頂
- NGO棚: 不計入

### Tier Deduplication
If a tier sponsor also has a market booth (included in tier package), do NOT double-count the booth fee.

### Donor ID Rules
- Format: D0001–D0229 (D0230 is next available)
- Known merges: DES→D0004, 茶鋪→D0001, lifewonders→D0076, D0218 released
- Canonical name is source of truth for matching

## Year Metadata
| Year | Edition | Theme |
|---|---|---|
| 2016 | 14 | 一起FUN出來—打破假友善，你我撐自在 |
| 2017 | 15 | 澀澀性平打開開，多元教慾跟上來 |
| 2018 | 16 | 性平攻略由你說，人人18投彩虹 |
| 2019 | 17 | 同志好厝邊 |
| 2020 | 18 | 成人之美 |
| 2021 | 19 | 友善日常（COVID-19 線上形式） |
| 2022 | 20 | 無限性 |
| 2023 | 21 | 與多元同行 STAND WITH DIVERSITY |
| 2024 | 22 | 邁向共榮 交織共生 |
| 2025 | 23 | 超·連結 |
| 2027 | 25 | （主題未定） |

## Cross-Year Summary (final numbers)
| Year | Total | 級別贊助 | 單購 | 市集 | 其他 |
|---|---:|---:|---:|---:|---:|
| 2016 | 808,000 | 0 | 0 | 63,000 | 745,000 |
| 2017 | 1,447,500 | 0 | 0 | 60,000 | 1,387,500 |
| 2018 | 1,565,000 | 0 | 0 | 0 | 1,565,000 |
| 2019 | 3,948,642 | 1,875,000 | 100,000 | 528,000 | 1,445,642 |
| 2020 | 4,270,000 | 2,355,000 | 773,000 | 549,500 | 592,500 |
| 2021 | ≥2,120,000 | 2,120,000 | 0 | 0 | 0 (20家金額不明) |
| 2022 | 9,060,650 | 6,779,000 | 1,900,500 | 239,150 | 142,000 |
| 2023 | 9,100,990 | 6,958,000 | 1,250,000 | 892,990 | 0 |
| 2024 | 10,803,504 | 6,486,219 | 2,938,000 | 930,000 | 449,285 |
| 2025 | 8,274,000 | 4,915,000 | 1,819,000 | 1,000,000 | 540,000 |

## Next Work: 2026 Growth Analysis
Six analyses planned, in priority order:

### B. Win-back List (highest priority)
47 donors in 2024 but not 2025. Priority score formula pending approval:
`score = amount_2024 × years_attended × tier_weight`
tier_weight: T1-T3=1.0, T4-T5=0.7, 單購=0.5

### A. Retention Rate Trend
Year-over-year: 2022→2023: 46%, 2023→2024: 53%, 2024→2025: 41%

### D. Loyalist Profile
27 sponsors with 3+ consecutive years in 2022–2025.
Core: 美光, 波士頓, 可口可樂, GILEAD, 拉拉公園, AZ, Google

### C. Tier Movement (2024→2025)
3 upgraded, 24 stayed, 5 downgraded.

### E. New Entrant Survival
New in 2022→survived 2023: 27%
New in 2023→survived 2024: 29%
New in 2024→survived 2025: 14% ← critical drop

### F. Revenue Concentration Risk
Top sponsors as % of total, Herfindahl index trend, what-if scenarios.

## Output Files Produced
- `跨年度全景_2016-2025_v7.xlsx` — master cross-year Excel
- `待釐清歸類疑義_2016-2025.xlsx` — remaining L-grade issues
- `臺灣同志遊行_商業贊助全景_2016-2025.html` — shareable interactive report (now index.html on GitHub Pages)
- Individual year Excel files: `2016_資料擷取結果.xlsx` through `2025_資料擷取結果.xlsx`

## Language
- All analysis code: Python
- All output labels: Traditional Chinese (繁體中文)
- Communication with user: Traditional Chinese
- User preference: short, precise, no decoration
