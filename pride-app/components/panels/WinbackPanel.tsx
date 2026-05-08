'use client'

import { useState } from 'react'

type Entry = {
  rank: number
  name: string
  industry: string
  tier: string
  amount: number
  yearsDisplay: string
  score: number
  dimmed: boolean
}

const CHIP: Record<string, [string, string]> = {
  T1: ['#B8860B20', '#B8860B'],
  T2: ['#E8A60020', '#E8A600'],
  T3: ['#4472C420', '#4472C4'],
  T4: ['#70AD4720', '#70AD47'],
  T5: ['#ED7D3120', '#ED7D31'],
  '花車': ['#5BC0EB20', '#5BC0EB'],
  '單買': ['#5BC0EB20', '#5BC0EB'],
}

function TierChip({ tier }: { tier: string }) {
  const [bg, color] = CHIP[tier] ?? ['#f1f5f920', '#64748b']
  return (
    <span className="inline-block px-2 py-0.5 rounded text-xs font-medium" style={{ background: bg, color }}>
      {tier}
    </span>
  )
}

const G2024: Entry[] = [
  { rank: 1,  name: '諾和諾德',       industry: '醫藥',     tier: 'T4',  amount: 220000,  yearsDisplay: '2 年',     score: 29.0, dimmed: false },
  { rank: 2,  name: '羅氏',           industry: '醫藥',     tier: 'T4',  amount: 220000,  yearsDisplay: '2 年',     score: 29.0, dimmed: false },
  { rank: 3,  name: '高通',           industry: '半導體',   tier: 'T4',  amount: 198000,  yearsDisplay: '3 年',     score: 28.5, dimmed: false },
  { rank: 4,  name: '樂天',           industry: '電商',     tier: 'T4',  amount: 197985,  yearsDisplay: '2 年',     score: 26.1, dimmed: false },
  { rank: 5,  name: '海峰電腦',       industry: '電腦',     tier: 'T5',  amount: 120000,  yearsDisplay: '2 年',     score: 13.2, dimmed: false },
  { rank: 6,  name: 'GU',             industry: '服飾',     tier: 'T4',  amount: 220000,  yearsDisplay: '僅1次 ↓', score: 13.2, dimmed: true },
  { rank: 7,  name: 'MYFEEL',         industry: '新創',     tier: 'T4',  amount: 219985,  yearsDisplay: '僅1次 ↓', score: 13.2, dimmed: true },
  { rank: 8,  name: '捷豹路虎',       industry: '車業',     tier: 'T4',  amount: 220000,  yearsDisplay: '僅1次 ↓', score: 13.2, dimmed: true },
  { rank: 9,  name: '高誠公關',       industry: '公關',     tier: '花車',amount: 120000,  yearsDisplay: '2 年',     score: 10.6, dimmed: false },
  { rank: 10, name: 'Suntory',        industry: '酒業',     tier: '花車',amount: 240000,  yearsDisplay: '僅1次 ↓', score: 9.6,  dimmed: true },
  { rank: 11, name: 'TaskUs',         industry: '軟體',     tier: 'T5',  amount: 120000,  yearsDisplay: '僅1次 ↓', score: 6.0,  dimmed: true },
  { rank: 12, name: 'Kenvue',         industry: 'FMCG',    tier: 'T5',  amount: 120000,  yearsDisplay: '僅1次 ↓', score: 6.0,  dimmed: true },
  { rank: 13, name: '台灣武田',       industry: '醫藥',     tier: 'T5',  amount: 120000,  yearsDisplay: '僅1次 ↓', score: 6.0,  dimmed: true },
  { rank: 14, name: 'SleekStrip',     industry: '生活',     tier: 'T5',  amount: 120000,  yearsDisplay: '僅1次 ↓', score: 6.0,  dimmed: true },
  { rank: 15, name: '宜蘊醫療',       industry: '醫藥',     tier: 'T5',  amount: 120000,  yearsDisplay: '僅1次 ↓', score: 6.0,  dimmed: true },
  { rank: 16, name: 'Zenyum',         industry: '生活',     tier: '花車',amount: 140000,  yearsDisplay: '僅1次 ↓', score: 5.6,  dimmed: true },
  { rank: 17, name: '法國巴黎人壽',   industry: '壽險',     tier: '花車',amount: 120000,  yearsDisplay: '僅1次 ↓', score: 4.8,  dimmed: true },
  { rank: 18, name: 'Fusion 聚變',    industry: '活動',     tier: '花車',amount: 120000,  yearsDisplay: '僅1次 ↓', score: 4.8,  dimmed: true },
  { rank: 19, name: '澳洲紐西蘭商會', industry: '商會',     tier: '花車',amount: 120000,  yearsDisplay: '僅1次 ↓', score: 4.8,  dimmed: true },
  { rank: 20, name: '佳葆視聽',       industry: '',         tier: '花車',amount: 120000,  yearsDisplay: '僅1次 ↓', score: 4.8,  dimmed: true },
  { rank: 21, name: 'EROLABS',        industry: '成人',     tier: '單買',amount: 50000,   yearsDisplay: '僅1次 ↓', score: 2.0,  dimmed: true },
  { rank: 22, name: '台灣不二',       industry: '生活',     tier: '單買',amount: 43000,   yearsDisplay: '僅1次 ↓', score: 1.7,  dimmed: true },
  { rank: 23, name: 'Sanofi',         industry: '醫療',     tier: '單買',amount: 25000,   yearsDisplay: '2 年',     score: 2.2,  dimmed: false },
]

const G2023: Entry[] = [
  { rank: 1,  name: 'GaGaoLaLa',                                                 industry: '影音',     tier: 'T3',  amount: 400000, yearsDisplay: '3 年',     score: 57.6, dimmed: false },
  { rank: 2,  name: 'PINKOI',                                                     industry: '電商',     tier: 'T4',  amount: 180000, yearsDisplay: '3 年',     score: 25.9, dimmed: false },
  { rank: 3,  name: 'Durex',                                                      industry: '生活',     tier: 'T4',  amount: 200000, yearsDisplay: '2 年',     score: 26.4, dimmed: false },
  { rank: 4,  name: '飛比',                                                       industry: '電商',     tier: 'T4',  amount: 180000, yearsDisplay: '僅1次 ↓', score: 10.8, dimmed: true },
  { rank: 5,  name: '世邦魏理仕',                                                 industry: '房地產',   tier: 'T4',  amount: 180000, yearsDisplay: '僅1次 ↓', score: 10.8, dimmed: true },
  { rank: 6,  name: 'LIFEWONDERS',                                                industry: '遊戲',     tier: 'T4',  amount: 180000, yearsDisplay: '僅1次 ↓', score: 10.8, dimmed: true },
  { rank: 7,  name: '美商百富門',                                                 industry: '酒商',     tier: 'T4',  amount: 180000, yearsDisplay: '僅1次 ↓', score: 10.8, dimmed: true },
  { rank: 8,  name: '雷醫國際股份有限公司',                                       industry: '醫美',     tier: 'T4',  amount: 180000, yearsDisplay: '僅1次 ↓', score: 10.8, dimmed: true },
  { rank: 9,  name: 'GroupM',                                                     industry: '廣告',     tier: 'T4',  amount: 180000, yearsDisplay: '僅1次 ↓', score: 10.8, dimmed: true },
  { rank: 10, name: 'VIETJET',                                                    industry: '航空',     tier: '花車',amount: 160000, yearsDisplay: '僅1次 ↓', score: 6.4,  dimmed: true },
  { rank: 11, name: 'La Crema',                                                   industry: '餐飲',     tier: '花車',amount: 140000, yearsDisplay: '僅1次 ↓', score: 5.6,  dimmed: true },
  { rank: 12, name: '台灣保時捷車業股份有限公司 Porsche Taiwan Motors Limited',   industry: '車商',     tier: '花車',amount: 120000, yearsDisplay: '僅1次 ↓', score: 4.8,  dimmed: true },
  { rank: 13, name: '樂桃航空',                                                   industry: '航空',     tier: 'T4',  amount: 68000,  yearsDisplay: '僅1次 ↓', score: 4.1,  dimmed: true },
  { rank: 14, name: '國際人權特赦組織(AI)',                                       industry: 'NGO',      tier: '單買',amount: 25000,  yearsDisplay: '4 年',     score: 2.6,  dimmed: false },
  { rank: 15, name: '紅犀牛',                                                     industry: '情趣用品', tier: '單買',amount: 15000,  yearsDisplay: '僅1次 ↓', score: 0.6,  dimmed: true },
  { rank: 16, name: '我們一起穩交吧',                                             industry: '交友',     tier: '單買',amount: 5000,   yearsDisplay: '僅1次 ↓', score: 0.2,  dimmed: true },
]

const G2022: Entry[] = [
  { rank: 1,  name: 'DIKE',         industry: '',     tier: 'T2',  amount: 700000,  yearsDisplay: '2 年',     score: 115.5, dimmed: false },
  { rank: 2,  name: 'FiftyPercent', industry: '服飾', tier: 'T1',  amount: 1000000, yearsDisplay: '僅1次 ↓', score: 75.0,  dimmed: true },
  { rank: 3,  name: 'Model TV',     industry: '',     tier: 'T2',  amount: 700000,  yearsDisplay: '僅1次 ↓', score: 52.5,  dimmed: true },
  { rank: 4,  name: 'YAHOO',        industry: '',     tier: 'T4',  amount: 170000,  yearsDisplay: '2 年',     score: 22.4,  dimmed: false },
  { rank: 5,  name: 'lululemon',    industry: '',     tier: 'T3',  amount: 300000,  yearsDisplay: '僅1次 ↓', score: 18.0,  dimmed: true },
  { rank: 6,  name: 'UT麗舍',       industry: '',     tier: 'T4',  amount: 254000,  yearsDisplay: '僅1次 ↓', score: 15.2,  dimmed: true },
  { rank: 7,  name: 'MAC',          industry: '',     tier: '單買',amount: 352000,  yearsDisplay: '僅1次 ↓', score: 14.1,  dimmed: true },
  { rank: 8,  name: '台北市觀傳局', industry: '',     tier: 'T4',  amount: 150000,  yearsDisplay: '僅1次 ↓', score: 9.0,   dimmed: true },
  { rank: 9,  name: '麥肯錫',       industry: '',     tier: '單買',amount: 100000,  yearsDisplay: '僅1次 ↓', score: 4.0,   dimmed: true },
  { rank: 10, name: '無心戒酒',     industry: '',     tier: '單買',amount: 100000,  yearsDisplay: '僅1次 ↓', score: 4.0,   dimmed: true },
  { rank: 11, name: '永準貿易',     industry: '',     tier: '單買',amount: 80000,   yearsDisplay: '僅1次 ↓', score: 3.2,   dimmed: true },
  { rank: 12, name: '澤豐',         industry: '',     tier: '單買',amount: 10000,   yearsDisplay: '2 年',     score: 0.9,   dimmed: false },
  { rank: 13, name: '七彩翼國際',   industry: '',     tier: '單買',amount: 10000,   yearsDisplay: '僅1次 ↓', score: 0.4,   dimmed: true },
]

function Table({ entries }: { entries: Entry[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-bg2">
            <th className="text-center px-2 py-2 text-text-muted font-medium w-8">#</th>
            <th className="text-left px-3 py-2 text-text-muted font-medium">廠商名稱</th>
            <th className="text-left px-3 py-2 text-text-muted font-medium hidden sm:table-cell">產業</th>
            <th className="text-center px-3 py-2 text-text-muted font-medium">類型</th>
            <th className="text-right px-3 py-2 text-text-muted font-medium">最後金額</th>
            <th className="text-right px-3 py-2 text-text-muted font-medium">歷年</th>
            <th className="text-right px-3 py-2 text-text-muted font-medium">優先分</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={`${e.rank}-${e.name}`} className="border-b border-border/40" style={{ opacity: e.dimmed ? 0.65 : 1 }}>
              <td className="text-center px-2 py-2 text-text-muted text-xs">{e.rank}</td>
              <td className="px-3 py-2 font-semibold text-foreground">{e.name}</td>
              <td className="px-3 py-2 text-xs text-text-muted hidden sm:table-cell">{e.industry}</td>
              <td className="px-3 py-2 text-center"><TierChip tier={e.tier} /></td>
              <td className="px-3 py-2 text-right text-foreground whitespace-nowrap">NTD {e.amount.toLocaleString()}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">
                {e.dimmed
                  ? <span className="text-xs" style={{ color: '#aaa' }}>{e.yearsDisplay}</span>
                  : <span className="text-foreground text-sm">{e.yearsDisplay}</span>}
              </td>
              <td className="px-3 py-2 text-right font-bold text-foreground">{e.score.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Group({ title, entries, defaultOpen }: { title: string; entries: Entry[]; defaultOpen: boolean }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
      <button
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-bg2/50 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <span className="font-semibold text-foreground text-sm">{title}</span>
        <span className="text-text-muted text-xs ml-4 shrink-0">{open ? '▲' : '▼'}</span>
      </button>
      {open && <Table entries={entries} />}
    </div>
  )
}

export function WinbackPanel() {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-text-muted mb-1">流失廠商挽回優先清單</p>
        <h1 className="text-2xl font-bold text-foreground">挽回清單</h1>
        <p className="text-sm text-text-muted mt-1">2022–2024 年曾贊助、但 2025 年未出現的廠商（市集／飯店類已排除）</p>
      </div>

      <p className="text-sm text-text-secondary">
        共追蹤 52 家廠商，上一年合計貢獻 NTD 9.63M。
        依最後活躍年度分組，優先聯繫 2024 年流失的廠商，再逐步往前追蹤。
        優先分數 = （金額 ÷ 10,000）×（出席加成）×（類型權重），數字越高越值得優先聯繫。
      </p>

      <div className="rounded-lg border border-border bg-bg2 px-4 py-3 text-sm text-foreground">
        <strong>優先分數：</strong>{' '}
        類型權重：鈦金=1.5、銀=1.2、銅=1.0、花車/單買=0.8；出席加成每年+10%，最高+50%；僅參與過一次者分數折半（×0.5），列表中以灰色標示
      </div>

      <Group title="▸ 2024 年流失（最高優先）（23 家，上一年合計 NTD 3.31M）" entries={G2024} defaultOpen={true} />
      <Group title="▸ 2023 年流失（中期目標）（16 家，上一年合計 NTD 2.39M）" entries={G2023} defaultOpen={false} />
      <Group title="▸ 2022 年流失（長期重啟）（13 家，上一年合計 NTD 3.93M）" entries={G2022} defaultOpen={false} />

      <div
        className="rounded-xl border border-border bg-surface p-5 flex gap-3"
        style={{ borderLeftWidth: 4, borderLeftColor: '#e8005a', boxShadow: 'var(--shadow-sm)' }}
      >
        <span className="text-2xl shrink-0">📞</span>
        <div className="text-sm text-foreground">
          <strong>行動建議：</strong>
          先集中火力挽回 2024 年流失廠商（最近一年），再逐年往前聯繫 2023 及 2022 年流失廠商。
          曾在多年前流失的廠商若重新接洽，建議以新合作形式（升級或特別方案）重新吸引。
        </div>
      </div>
    </div>
  )
}
