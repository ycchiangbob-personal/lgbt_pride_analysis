'use client'

import { useEffect, useState } from 'react'
import { BASE } from '@/lib/basePath'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'

type NewEntry = { name: string; cat: string; label: string; amount: number }
type ReturnEntry = {
  name: string; prev_yr: number; prev_cat: string; prev_label: string
  curr_cat: string; curr_label: string; curr_amount: number; change_type: string
}
type Cohort = { new_2025: NewEntry[]; returning_2025: ReturnEntry[] }

const CAT_CHIP: Record<string, { bg: string; color: string; border: string }> = {
  TIER:   { bg: '#f3e8ff', color: '#7c3aed', border: '#e9d5ff' },
  SINGLE: { bg: '#e0f2fe', color: '#0284c7', border: '#bae6fd' },
  MARKET: { bg: '#dcfce7', color: '#059669', border: '#a7f3d0' },
  OTHER:  { bg: '#f1f5f9', color: '#64748b', border: '#e2e8f0' },
}

function Chip({ cat, label }: { cat: string; label: string }) {
  const s = CAT_CHIP[cat] ?? CAT_CHIP.OTHER
  return (
    <span className="inline-block px-2 py-0.5 rounded-full text-xs border" style={{ background: s.bg, color: s.color, borderColor: s.border }}>
      {label}
    </span>
  )
}

function changeBadge(ct: string) {
  const map: Record<string, { label: string; bg: string; color: string }> = {
    same:      { label: '維持',    bg: '#f0f0f0', color: '#666' },
    upgrade:   { label: '↑ 升購', bg: '#f3e8ff', color: '#7c3aed' },
    downgrade: { label: '↓ 降購', bg: '#fff0f6', color: '#e8005a' },
    other:     { label: '轉換',    bg: '#fff9e6', color: '#a06020' },
  }
  const s = map[ct] ?? map.other
  return (
    <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold" style={{ background: s.bg, color: s.color }}>
      {s.label}
    </span>
  )
}

const SURVIVAL_CHART = [
  { year: '2018→2019', rate: 14.3, isRef: true },
  { year: '2019→2020', rate: 25.0, isRef: true },
  { year: '2020→2021', rate: 33.3, isRef: true },
  { year: '2021→2022', rate: 50.0, isRef: true },
  { year: '2022→2023', rate: 33.3, isRef: false },
  { year: '2023→2024', rate: 36.8, isRef: false },
  { year: '2024→2025', rate: 33.3, isRef: false },
]

const SURVIVAL_TABLE = [
  { yr: '2016–2017',     isRef: true,  newCnt: 0,  kept: 0, rate: 'N/A',   rateColor: '#94a3b8' },
  { yr: '2018 年新廠商', isRef: true,  newCnt: 14, kept: 2, rate: '14.3%', rateColor: '#D93025' },
  { yr: '2019 年新廠商', isRef: true,  newCnt: 8,  kept: 2, rate: '25.0%', rateColor: '#D93025' },
  { yr: '2020 年新廠商', isRef: true,  newCnt: 9,  kept: 3, rate: '33.3%', rateColor: '#d97706' },
  { yr: '2021 年新廠商', isRef: true,  newCnt: 4,  kept: 2, rate: '50.0%', rateColor: '#059669' },
  { yr: '2022 年新廠商', isRef: false, newCnt: 18, kept: 6, rate: '33.3%', rateColor: '#d97706' },
  { yr: '2023 年新廠商', isRef: false, newCnt: 19, kept: 7, rate: '36.8%', rateColor: '#d97706' },
  { yr: '2024 年新廠商', isRef: false, newCnt: 21, kept: 7, rate: '33.3%', rateColor: '#d97706' },
]

const TYPE_TABLE = [
  { type: 'T1/T2 白金/黃金', cnt: 2,  kept: 1, rate: '50.0%', rateColor: '#059669' },
  { type: 'T3 鈦金/白銀',   cnt: 5,  kept: 3, rate: '60.0%', rateColor: '#059669' },
  { type: 'T4 銀',           cnt: 24, kept: 8, rate: '33.3%', rateColor: '#d97706' },
  { type: 'T5 銅',           cnt: 8,  kept: 3, rate: '37.5%', rateColor: '#d97706' },
  { type: '花車/單買 (&gt;50k)', cnt: 19, kept: 5, rate: '26.3%', rateColor: '#D93025' },
]

type PriorityEntry = {
  name: string; type: string; typeStyle: { bg: string; color: string }
  amount: number; priority: '★★★' | '★★' | '★'; priColor: string
}

const FOLLOW_UP_2025: PriorityEntry[] = [
  { name: 'JINS',                   type: 'T3 鈦金', typeStyle: { bg: '#4472C420', color: '#4472C4' }, amount: 500000, priority: '★★★', priColor: '#1B7A3E' },
  { name: 'Johnnie Walker',         type: 'T4 銀',   typeStyle: { bg: '#70AD4720', color: '#70AD47' }, amount: 220000, priority: '★★★', priColor: '#1B7A3E' },
  { name: 'TFC 臺北婦產科診所',     type: 'T5 銅',   typeStyle: { bg: '#ED7D3120', color: '#ED7D31' }, amount: 120000, priority: '★★',  priColor: '#d97706' },
  { name: 'IM Adult',               type: '花車',    typeStyle: { bg: '#5BC0EB20', color: '#5BC0EB' }, amount: 120000, priority: '★★',  priColor: '#d97706' },
  { name: 'TSMC',                   type: '花車',    typeStyle: { bg: '#5BC0EB20', color: '#5BC0EB' }, amount: 120000, priority: '★★',  priColor: '#d97706' },
  { name: 'FNF',                    type: '花車',    typeStyle: { bg: '#5BC0EB20', color: '#5BC0EB' }, amount: 120000, priority: '★★',  priColor: '#d97706' },
  { name: 'hyve solutions',         type: 'T5 銅',   typeStyle: { bg: '#ED7D3120', color: '#ED7D31' }, amount: 108000, priority: '★★',  priColor: '#d97706' },
]

export function NewBrandPanel() {
  const [cohort, setCohort] = useState<Cohort | null>(null)

  useEffect(() => {
    fetch(`${BASE}/data/cohort_2025.json`)
      .then((r) => r.json())
      .then(setCohort)
  }, [])

  const returning_2025 = cohort?.returning_2025 ?? []
  // 只保留跳過 2024 年後再度回歸的廠商（prev_yr < 2024）
  const skip_year_2025 = returning_2025.filter((r) => r.prev_yr !== 2024)
  const upgrade   = skip_year_2025.filter((r) => r.change_type === 'upgrade')
  const same      = skip_year_2025.filter((r) => r.change_type === 'same')
  const downgrade = skip_year_2025.filter((r) => r.change_type === 'downgrade')
  const other     = skip_year_2025.filter((r) => r.change_type === 'other')
  const sorted = [...upgrade, ...same, ...downgrade, ...other]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">新品牌續約率</h1>
        <p className="text-sm text-text-muted mt-1">首次簽訂級別或花車合約的廠商，隔年還會回來嗎？（僅計算級別贊助 ＋ 單購 &gt;50k）</p>
      </div>

      {/* Intro text */}
      <div className="text-sm text-foreground leading-relaxed">
        每年首次加入（級別或單購 &gt;50k）的廠商，隔年續約率在 2022–2024 均維持在 33–37%。灰色柱子（2018–2021）因資料品質較低，僅供參考；2016–2017 無級別資料，不納入。
      </div>

      {/* Survival bar chart */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-3">新廠商首年加入後隔年續約率（級別 ＋ 單購 &gt;50k，2018–2024）</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={SURVIVAL_CHART} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="year" tick={{ fontSize: 10, fill: '#94a3b8' }} />
            <YAxis domain={[0, 80]} tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v) => `${v}%`} />
            <Tooltip
              formatter={(val) => [`${val}%`, '續約率']}
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
            />
            <Bar dataKey="rate" radius={[4, 4, 0, 0]}>
              {SURVIVAL_CHART.map((entry) => (
                <Cell key={entry.year} fill={entry.isRef ? '#cccccc' : '#4472C4'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Survival KPIs */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-sm font-semibold text-foreground mb-4">新進廠商次年留存率</h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: '2022 新進 → 2023 留存', rate: 33 },
            { label: '2023 新進 → 2024 留存', rate: 37 },
            { label: '2024 新進 → 2025 留存', rate: 33 },
          ].map(({ label, rate }) => (
            <div key={label} className="text-center">
              <p className="text-2xl font-bold" style={{ color: rate < 20 ? '#e8005a' : rate < 30 ? '#d97706' : '#059669' }}>
                {rate}%
              </p>
              <p className="text-xs text-text-muted mt-1">{label}</p>
            </div>
          ))}
        </div>
        <p className="text-xs text-text-muted mt-4">
          ▸ 2022–2024 新進廠商次年續約率維持 33–37%，趨勢穩定。重點應放在升級而非一次性合約。
        </p>
      </div>

      {/* Secondary view: tier/single-only vs blended survival */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-sm font-semibold text-foreground mb-1">留存率拆解：市集 ／ 飯店稀釋了整體數字</h2>
          <p className="text-sm text-text-muted mb-3">
            現行 33–37% 為「所有首次贊助廠商（含市集、飯店、其他）」的整體數字。若單獨計算<strong>首次簽訂級別或單購合約</strong>的廠商，留存率明顯更高。
          </p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">計算範圍</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">2022新→2023</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">2023新→2024</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">2024新→2025</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-border/50">
                <td className="px-4 py-2 text-text-secondary">全類型新廠商（含市集 ／ 飯店）</td>
                <td className="px-3 py-2 text-right font-bold" style={{ color: '#d97706' }}>33%</td>
                <td className="px-3 py-2 text-right font-bold" style={{ color: '#d97706' }}>37%</td>
                <td className="px-3 py-2 text-right font-bold" style={{ color: '#d97706' }}>33%</td>
              </tr>
              <tr>
                <td className="px-4 py-2 text-text-secondary">首次簽訂級別 ／ 單購廠商</td>
                <td className="px-3 py-2 text-right font-bold" style={{ color: '#059669' }}>76%</td>
                <td className="px-3 py-2 text-right font-bold" style={{ color: '#059669' }}>86%</td>
                <td className="px-3 py-2 text-right font-bold" style={{ color: '#059669' }}>100%</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-text-muted px-5 py-3 border-t border-border">
          ▸ 2024 年首次簽訂級別 ／ 單購的 6 家廠商（LifeWonders、Tapestry、犀牛盾、渣打銀行、愛群婦產科、疾管署）<strong>全數留存至 2025</strong>。<br />
          ▸ 2025 年首次簽訂級別 ／ 單購的廠商為 <strong>0 家</strong>，是 2016 年有紀錄以來首次，代表 2026 的成長動能完全依賴挽回與升級，缺乏新血。
        </p>
      </div>

      {/* Survival table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">新廠商加入年度</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">新廠商數</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">隔年續約</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">續約率</th>
              </tr>
            </thead>
            <tbody>
              {SURVIVAL_TABLE.map((r, i) => (
                <tr key={r.yr} className={`border-b border-border/50 ${r.isRef ? 'opacity-65' : ''} ${i % 2 === 1 ? 'bg-bg2/40' : ''}`}>
                  <td className="px-4 py-2 text-foreground">
                    {r.yr}
                    {r.isRef && <span className="ml-2 text-xs text-text-muted italic">（參考）</span>}
                  </td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.newCnt}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.kept}</td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: r.rateColor }}>{r.rate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Type breakdown table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-1">首年購買類型 vs 隔年續約率（2022–2024，級別 ＋ 單購 &gt;50k）</h2>
          <p className="text-sm text-text-muted mb-3">同樣是第一次合作的廠商，簽了哪種合約，決定了他們隔年回來的機率。</p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">首年購買類型</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">新廠商數</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">隔年續約</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">續約率</th>
              </tr>
            </thead>
            <tbody>
              {TYPE_TABLE.map((r, i) => (
                <tr key={r.type} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/40' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground">{r.type}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.cnt}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.kept}</td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: r.rateColor }}>{r.rate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-text-muted px-5 py-3 border-t border-border">
          ▸ 綠色 ≥ 40%　橘色 25–39%　紅色 &lt; 25%  ·  市集 / 飯店 / 其他類型不納入計算
        </p>
      </div>

      {/* Action box 1 */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        🌱 <strong>行動建議：</strong>新廠商開發時，優先引導簽訂級別合約（T4 銀以上），而非花車或單次活動，因為級別廠商的隔年續約率明顯更高。
      </div>

      {/* 2025 follow-up table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-1">2025 年首次合作廠商 — 2026 跟進清單（7 家，級別 ＋ 單購 &gt;50k）</h2>
          <p className="text-sm text-text-muted mb-3">
            以下廠商為 2025 年首次簽訂級別或單購 &gt;50k 合約，尚無隔年數據。依歷史首年存活率（33–37%），約有 2–3 家會自然續約；其餘需主動跟進。三步節奏：①活動後一個月發感謝函　②三個月電話回訪　③六個月前發出 2026 邀請。
          </p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商名稱</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">購買類型</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">2025 金額</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">跟進優先</th>
              </tr>
            </thead>
            <tbody>
              {FOLLOW_UP_2025.map((r, i) => (
                <tr key={r.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/40' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground">{r.name}</td>
                  <td className="px-3 py-2">
                    <span className="inline-block px-2 py-0.5 rounded text-xs font-medium" style={r.typeStyle}>
                      {r.type}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right text-text-secondary">NTD {r.amount.toLocaleString()}</td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: r.priColor }}>{r.priority}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-text-muted px-5 py-3 border-t border-border">
          ▸ 優先級：★★★ = 鈦金/銀（≥ NTD 200k）　★★ = 銅/花車（≥ NTD 100k）　★ = 其他/飯店（&lt; NTD 100k）<br />
          ▸ JINS 與 Johnnie Walker 為高價值新廠商，建議主管層級親自接觸。
        </p>
      </div>

      {/* Blind spot warning */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        📋 <strong>盲點提醒：</strong>2025 首次廠商不會出現在「忠實廠商」（需 3 年以上）、「挽回清單」（追蹤已流失者）或「留存率」（尚無隔年數據）等分析中，此清單是唯一能看見他們的地方。曾參與後跳過 2024、於 2025 再度返場的廠商，已列於上方「2025 返場品牌」清單中。
      </div>

      {/* Returning table */}
      {cohort && (
        <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <div className="px-5 pt-4 pb-3 border-b border-border flex items-center gap-3 flex-wrap">
            <h2 className="text-base font-semibold text-foreground">
              2025 返場品牌（{skip_year_2025.length} 家）
            </h2>
            <div className="flex gap-2 ml-auto flex-wrap">
              {[
                { label: `↑ 升購 ${upgrade.length}`, bg: '#f3e8ff', color: '#7c3aed' },
                { label: `維持 ${same.length}`, bg: '#f0f0f0', color: '#666' },
                { label: `↓ 降購 ${downgrade.length}`, bg: '#fff0f6', color: '#e8005a' },
              ].map(({ label, bg, color }) => (
                <span key={label} className="px-3 py-1 rounded-full text-xs font-semibold" style={{ background: bg, color }}>
                  {label}
                </span>
              ))}
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-bg2">
                  <th className="text-left px-4 py-2 text-text-muted font-medium">廠商</th>
                  <th className="text-center px-3 py-2 text-text-muted font-medium">前次年份</th>
                  <th className="text-left px-3 py-2 text-text-muted font-medium">前次採購</th>
                  <th className="text-left px-3 py-2 text-text-muted font-medium">2025 採購</th>
                  <th className="text-right px-4 py-2 text-text-muted font-medium">2025 金額</th>
                  <th className="text-center px-3 py-2 text-text-muted font-medium">變化</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((r, i) => (
                  <tr key={r.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                    <td className="px-4 py-2 font-medium text-foreground">{r.name}</td>
                    <td className="px-3 py-2 text-center text-text-muted text-xs">{r.prev_yr}</td>
                    <td className="px-3 py-2"><Chip cat={r.prev_cat} label={r.prev_label} /></td>
                    <td className="px-3 py-2"><Chip cat={r.curr_cat} label={r.curr_label} /></td>
                    <td className="px-4 py-2 text-right text-text-secondary text-xs">
                      {r.curr_amount ? `NT$${r.curr_amount.toLocaleString()}` : '—'}
                    </td>
                    <td className="px-3 py-2 text-center">{changeBadge(r.change_type)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
