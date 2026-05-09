'use client'

import { useEffect, useMemo, useState } from 'react'
import { BASE } from '@/lib/basePath'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Legend, Cell, LabelList,
} from 'recharts'

type Sponsor = {
  name_canonical: string
  tier_orig: string
  industry: string
  amount: number
}
type AllData = Record<string, Sponsor[]>

const YEARS = ['2022', '2023', '2024', '2025']

// Tenure retention data — filtered analysis (TIER + SINGLE>50k, excl. 市集/飯店), churn_v2.py output
const TENURE_DATA = [
  { label: '首次贊助', rate: 44.0, nChurn: 42, nRetain: 33, color: '#e8445a' },
  { label: '第 2 年',  rate: 75.0, nChurn: 7,  nRetain: 21, color: '#f4a93a' },
  { label: '第 3 年',  rate: 86.7, nChurn: 2,  nRetain: 13, color: '#4caf50' },
]

// Donor-type proof examples — reclassified per updated framework
// Commercial = brand sells specifically TO LGBT community (their customers are at Pride)
// Value = brand shows external DEI support; LGBT not their primary/significant market
// retentionRate: pooled 2022-2025, 3 transitions
const DONOR_TYPES = [
  {
    category: '価值導向（外部支持／DEI 理念）',
    retentionRate: 52.9,
    color: '#2e7d32', borderColor: '#4caf50', bgHeader: '#f0fdf4',
    loyalist: { name: 'Google', detail: '科技・銀級・NTD 170–198k/年', years: [true, true, true, true] },
    churner:  { name: 'lululemon', detail: '運動服飾・白銀級・NTD 300k', years: [true, false, null, null] },
  },
  {
    category: '商業導向（顧客就在現場）',
    retentionRate: 75.0,
    color: '#1565c0', borderColor: '#4472C4', bgHeader: '#eff6ff',
    loyalist: { name: 'G-Star', detail: '時尚・銀級・NTD 150–198k/年', years: [true, true, true, true] },
    churner:  { name: 'GaGaoLaLa', detail: 'LGBTQ+ 影音平台・白銀級・NTD 400k', years: [null, true, false, null] },
  },
]

// 2019–2021 reference rows (incomplete data, static)
const STATIC_HISTORY = [
  { label: '2019→2020', rate: 57.1, isRef: true },
  { label: '2020→2021', rate: 22.9, isRef: true },
  { label: '2021→2022', rate: 66.7, isRef: true },
]

const SINGLE_KEYWORDS = ['單買', '花車', '單購', '商業花車']

// Exclude: hotels, market booths, and single-purchase donors with amount ≤ NTD 50,000
const shouldExclude = (s: Sponsor) => {
  const tier = s.tier_orig ?? ''
  const ind  = s.industry  ?? ''
  if (tier.includes('飯店') || ind.includes('飯店') || ind.includes('旅館')) return true
  if (tier.includes('市集') || ind.includes('市集')) return true
  const isSingle = SINGLE_KEYWORDS.some((k) => tier.includes(k))
  if (isSingle && (s.amount ?? 0) <= 50000) return true
  return false
}

type RetentionRow = {
  label: string; from: string; to: string
  fromCount: number; retained: number; lost: number; rate: number
  churnTotalK: number; retainTotalK: number
  churnAvgK: number; retainAvgK: number
}

function computeRetention(data: AllData): RetentionRow[] {
  return [
    { from: '2022', to: '2023' },
    { from: '2023', to: '2024' },
    { from: '2024', to: '2025' },
  ].map(({ from, to }) => {
    const fromSponsors = (data[from] ?? []).filter((s) => !shouldExclude(s))
    const toNames     = new Set((data[to] ?? []).filter((s) => !shouldExclude(s)).map((s) => s.name_canonical))
    const fromNames   = fromSponsors.map((s) => s.name_canonical)
    const fromSet     = new Set(fromNames)
    const retained    = [...fromSet].filter((n) => toNames.has(n))
    const churned     = [...fromSet].filter((n) => !toNames.has(n))

    const sumAmt = (names: string[]) =>
      names.reduce((acc, n) => acc + (fromSponsors.find((s) => s.name_canonical === n)?.amount ?? 0), 0)

    const retainTotal = sumAmt(retained)
    const churnTotal  = sumAmt(churned)
    const rate = fromSet.size > 0 ? Math.round((retained.length / fromSet.size) * 100) : 0

    return {
      label: `${from}→${to}`, from, to,
      fromCount: fromSet.size,
      retained: retained.length,
      lost: churned.length,
      rate,
      churnTotalK:  Math.round(churnTotal  / 1000),
      retainTotalK: Math.round(retainTotal / 1000),
      churnAvgK:  churned.length  ? Math.round(churnTotal  / churned.length  / 1000) : 0,
      retainAvgK: retained.length ? Math.round(retainTotal / retained.length / 1000) : 0,
    }
  })
}

function KpiCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
      <p className="text-sm text-text-muted mb-1">{label}</p>
      <p className="text-2xl font-bold" style={{ color }}>{value}</p>
    </div>
  )
}

export function RetentionPanel() {
  const [data, setData] = useState<AllData | null>(null)

  useEffect(() => {
    fetch(`${BASE}/data/all_extracted_v2.json`)
      .then((r) => r.json())
      .then(setData)
  }, [])

  const retention = useMemo(() => (data ? computeRetention(data) : []), [data])

  // Bar chart 1 data: static 2019-2021 + computed 2022-2025
  const chart1Data = useMemo(() => [
    ...STATIC_HISTORY,
    ...retention.map((r) => ({ label: r.label, rate: r.rate, isRef: false })),
  ], [retention])

  // Bar chart 2 data: computed churn vs retain totals
  const chart2Data = useMemo(() =>
    retention.map((r) => ({ label: r.label, 流失: r.churnTotalK, 留存: r.retainTotalK })),
  [retention])

  // Detail table: static 2019-2021 + computed 2022-2025
  const tableRows = useMemo(() => [
    { yr: '2019→2020', isRef: true, prev: 7,  kept: 4,  lost: 3,  rate: '57.1%', churnAvg: null as string | null, retainAvg: null as string | null },
    { yr: '2020→2021', isRef: true, prev: 35, kept: 8,  lost: 27, rate: '22.9%', churnAvg: null, retainAvg: null },
    { yr: '2021→2022', isRef: true, prev: 12, kept: 8,  lost: 4,  rate: '66.7%', churnAvg: null, retainAvg: null },
    ...retention.map((r) => ({
      yr: r.label, isRef: false,
      prev: r.fromCount, kept: r.retained, lost: r.lost,
      rate: `${r.rate}%`,
      churnAvg:  r.churnAvgK  ? `NTD ${r.churnAvgK}k`  : null,
      retainAvg: r.retainAvgK ? `NTD ${r.retainAvgK}k` : null,
    })),
  ], [retention])

  const colorForRate = (r: number) =>
    r >= 50 ? '#059669' : r >= 40 ? '#d97706' : '#e8005a'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">留存率分析</h1>
      </div>

      {/* Scope disclaimer */}
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
        <strong>ℹ️ 計算範圍說明：</strong>本頁所有留存率數字僅涵蓋
        <strong>級別贊助廠商</strong>（白金／鈦金／黃金／銀／銅）與
        <strong>單購金額 &gt; NTD 50,000</strong> 的廠商。
        彩虹市集攤位與友善飯店已全數排除——此兩類廠商單次金額過低，
        且參與形式與商業贊助廠商不同，不列入商業合作留存分析。
      </div>

      {/* Bar chart 1 — retention rate history */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-2">每年有多少去年的廠商今年繼續贊助？（2019–2025）</h2>
        <p className="text-sm text-text-muted mb-4">
          留存率 = 去年有贊助的廠商中，今年繼續合作的比例。灰色柱子（2019–2021）因原始資料不完整，數字僅供參考。藍色柱子（2022–2025）依篩選後名單計算。
        </p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chart1Data} margin={{ top: 28, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v) => `${v}%`} />
            <Tooltip
              formatter={(val) => [`${val}%`, '留存率']}
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
            />
            <Bar dataKey="rate" radius={[4, 4, 0, 0]}>
              {chart1Data.map((entry) => (
                <Cell key={entry.label} fill={entry.isRef ? '#cccccc' : '#4472C4'} />
              ))}
              <LabelList
                dataKey="rate"
                position="top"
                style={{ fontSize: 11, fontWeight: 600, fill: '#475569' }}
                formatter={(v: unknown) => `${Number(v).toFixed(1)}%`}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Bar chart 2 — churn vs retain amounts */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-2">流失廠商 vs 留存廠商——上一年合計贊助金額（2022–2025）</h2>
        <p className="text-sm text-text-muted mb-4">
          紅柱 = 流失廠商在前一年的合計金額（該收入不再進來）；藍柱 = 留存廠商在前一年的合計金額（成功保住的收入）。數字已依篩選範圍計算，僅含級別廠商與單購 &gt; 50k。
        </p>
        <ResponsiveContainer width="100%" height={230}>
          <BarChart data={chart2Data} margin={{ top: 28, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v) => `${(v / 1000).toFixed(1)}M`} />
            <Tooltip
              formatter={(val) => [`NTD ${Number(val).toLocaleString()}k`, '']}
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
            />
            <Bar dataKey="流失" fill="#e53935" radius={[4, 4, 0, 0]}>
              <LabelList
                dataKey="流失"
                position="top"
                style={{ fontSize: 10, fontWeight: 600, fill: '#c62828' }}
                formatter={(v: unknown) => `${(Number(v) / 1000).toFixed(2)}M`}
              />
            </Bar>
            <Bar dataKey="留存" fill="#4472C4" radius={[4, 4, 0, 0]}>
              <LabelList
                dataKey="留存"
                position="top"
                style={{ fontSize: 10, fontWeight: 600, fill: '#1565c0' }}
                formatter={(v: unknown) => `${(Number(v) / 1000).toFixed(2)}M`}
              />
            </Bar>
            <Legend />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">年度</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">前年廠商數</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">續簽</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">流失</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">留存率</th>
                <th className="text-right px-3 py-2 font-medium" style={{ color: '#c62828' }}>流失廠商均額</th>
                <th className="text-right px-3 py-2 font-medium" style={{ color: '#2e7d32' }}>留存廠商均額</th>
              </tr>
            </thead>
            <tbody>
              {tableRows.map((r, i) => (
                <tr
                  key={r.yr}
                  className={`border-b border-border/50 ${r.isRef ? 'opacity-65' : ''} ${i % 2 === 1 ? 'bg-bg2/40' : ''}`}
                >
                  <td className="px-4 py-2 text-foreground">
                    {r.yr}
                    {r.isRef && <span className="ml-2 text-xs text-text-muted italic">（參考）</span>}
                  </td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.prev}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.kept}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.lost}</td>
                  <td className="px-3 py-2 text-right font-bold">{r.rate}</td>
                  {r.churnAvg ? (
                    <>
                      <td className="px-3 py-2 text-right" style={{ color: '#c62828' }}>{r.churnAvg}</td>
                      <td className="px-3 py-2 text-right" style={{ color: '#2e7d32' }}>{r.retainAvg}</td>
                    </>
                  ) : (
                    <td colSpan={2} className="px-3 py-2 text-right text-xs text-text-muted">資料不完整</td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action box */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        📉 <strong>行動建議：</strong>篩選後 2024→2025 流失 21 家，合計損失 NTD 3.39M，平均每家 162k——流失的是高單價客戶。行動重點：①<strong>第一年結束前</strong>主動啟動 renewal 溝通（56% 流失在此節點）；②引導廠商從銅／花車升至銀以上（銅級流失率 54.5% vs 銀級 40%）；③挽回流失廠商時設最低再入場門檻為銀級——重新進場的廠商若以低階再入，二次流失風險極高（見高誠公關、海峰電腦案例）。
      </div>

      {/* KPI cards (computed, hotel-excluded) */}
      {data && (
        <div className="grid grid-cols-3 gap-4">
          {retention.map((r) => (
            <KpiCard
              key={r.label}
              label={r.label}
              value={`${r.rate}%`}
              color={colorForRate(r.rate)}
            />
          ))}
        </div>
      )}

      {/* Tenure retention — Year 1 / 2 / 3 */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-1">出席年資 vs 留存率（2022–2025，篩選後）</h2>
        <p className="text-sm text-text-muted mb-4">三個轉換期合計（n=118 廠商次）。第 1 年留存率僅 44%，撐過後大幅躍升；進入第 3 年後留存率達 87%。</p>
        <ResponsiveContainer width="100%" height={130}>
          <BarChart layout="vertical" data={TENURE_DATA} margin={{ top: 4, right: 48, left: 8, bottom: 4 }}>
            <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <YAxis type="category" dataKey="label" width={58} tick={{ fontSize: 12, fill: '#475569' }} />
            <Tooltip formatter={(val) => [`${val}%`, '留存率']} contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
            <Bar dataKey="rate" radius={4}>
              {TENURE_DATA.map((d) => <Cell key={d.label} fill={d.color} />)}
              <LabelList dataKey="rate" position="right" style={{ fontSize: 12, fontWeight: 700 }} formatter={(v: unknown) => `${v}%`} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="overflow-x-auto mt-3">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-3 py-2 text-text-muted font-medium">出席年資</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">流失</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">留存</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">合計</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">留存率</th>
              </tr>
            </thead>
            <tbody>
              {TENURE_DATA.map((d, i) => (
                <tr key={d.label} className={i % 2 === 1 ? 'bg-bg2/40' : ''}>
                  <td className="px-3 py-2 font-medium">{d.label}</td>
                  <td className="px-3 py-2 text-right" style={{ color: '#c62828' }}>{d.nChurn}</td>
                  <td className="px-3 py-2 text-right" style={{ color: '#2e7d32' }}>{d.nRetain}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{d.nChurn + d.nRetain}</td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: d.color }}>{d.rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Donor-type proof — 2×2 comparison */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-1">商業導向廠商留存率更高——因為他們的顧客就在現場</h2>
        <p className="text-sm text-text-muted mb-4">
          商業導向廠商（75%）留存率高於價值導向廠商（53%）：前者的目標客群就在遊行現場，ROI 不需要解釋，自然持續回來。但兩類型內部同樣各有留存者與流失者——動機只是背景，<strong>年資與級別才是 BD 能操作的預測因子</strong>。
        </p>
        <div className="grid grid-cols-2 gap-4">
          {DONOR_TYPES.map((col) => (
            <div key={col.category}>
              <div className="pb-2 mb-3" style={{ borderBottom: `2px solid ${col.borderColor}` }}>
                <div className="text-sm font-bold" style={{ color: col.color }}>{col.category}</div>
                <div className="text-xs mt-0.5" style={{ color: '#888' }}>
                  2022–2025 平均留存率：<strong style={{ color: col.color }}>{col.retentionRate}%</strong>
                </div>
              </div>
              {[{ role: '留存', data: col.loyalist, bg: col.bgHeader, isChurner: false },
                { role: '流失', data: col.churner,  bg: '#fff8f8',    isChurner: true  }].map(({ role, data, bg, isChurner }) => (
                <div key={role} className="rounded-lg p-3 mb-2 text-sm" style={{ background: bg }}>
                  <div className="font-bold text-foreground">{data.name}</div>
                  <div className="text-xs mt-0.5 mb-2" style={{ color: '#666' }}>{data.detail}</div>
                  <div className="flex gap-1 flex-wrap">
                    {YEARS.map((yr, idx) => {
                      const v = data.years[idx]
                      return (
                        <span key={yr} className="text-xs font-mono px-1.5 py-0.5 rounded" style={{
                          background: v === true ? '#dcfce7' : v === false ? '#fee2e2' : '#f1f5f9',
                          color:      v === true ? '#166534' : v === false ? '#991b1b' : '#94a3b8',
                          fontWeight: v !== null ? 700 : 400,
                        }}>
                          {yr} {v === true ? '✓' : v === false ? '✗' : '—'}
                        </span>
                      )
                    })}
                  </div>
                  <div className="text-xs mt-1.5" style={{ color: isChurner ? '#e8445a' : '#2e7d32' }}>
                    → {isChurner ? '首年即流失' : '4 年連續留存'}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
        <p className="text-sm mt-4 pt-3 border-t border-border" style={{ color: '#555' }}>
          <strong>結論：</strong>Google 與 G-Star 動機截然不同，卻都連續贊助 4 年；lululemon 與 GaGaoLaLa 動機截然不同，卻都在首年離開。商業導向廠商整體更黏（75%），是因為顧客就在現場、ROI 可見——這是優勢，不是風險。對價值導向廠商，BD 應主動協助量化 DEI 影響力，降低預算被砍的風險。<strong>無論哪類，年資（第 1 年留存率僅 44%）與級別（銅／花車 &gt;50% 流失）都是首要管理標的。</strong>
        </p>
      </div>
    </div>
  )
}
