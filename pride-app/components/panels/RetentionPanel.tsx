'use client'

import { useEffect, useMemo, useState } from 'react'
import { BASE } from '@/lib/basePath'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend, Cell, LabelList,
} from 'recharts'

type Sponsor = {
  name_canonical: string
  tier_orig: string
  industry: string
  amount: number
}
type AllData = Record<string, Sponsor[]>

const YEARS = ['2022', '2023', '2024', '2025']

// 2019–2021 reference rows (incomplete data, static)
const STATIC_HISTORY = [
  { label: '2019→2020', rate: 57.1, isRef: true },
  { label: '2020→2021', rate: 22.9, isRef: true },
  { label: '2021→2022', rate: 66.7, isRef: true },
]

const isHotel = (s: Sponsor) =>
  s.tier_orig?.includes('飯店') || s.industry?.includes('飯店') || s.industry?.includes('旅館')

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
    const fromSponsors = (data[from] ?? []).filter((s) => !isHotel(s))
    const toNames     = new Set((data[to] ?? []).filter((s) => !isHotel(s)).map((s) => s.name_canonical))
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

  const matrix = useMemo(() => {
    if (!data) return []
    const clean = YEARS.reduce<AllData>((acc, yr) => {
      acc[yr] = (data[yr] ?? []).filter((s) => !isHotel(s))
      return acc
    }, {})
    const allNames = new Set<string>()
    YEARS.forEach((yr) => clean[yr]?.forEach((s) => allNames.add(s.name_canonical)))
    return [...allNames].sort().map((name) => ({
      name,
      years: YEARS.map((yr) => ({
        yr,
        present: !!clean[yr]?.find((s) => s.name_canonical === name),
        tier: clean[yr]?.find((s) => s.name_canonical === name)?.tier_orig ?? '',
      })),
    }))
  }, [data])

  const colorForRate = (r: number) =>
    r >= 50 ? '#059669' : r >= 40 ? '#d97706' : '#e8005a'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">年度留存率趨勢</h1>
        <p className="text-xs text-text-muted mt-1">友善飯店廠商已從計算中排除</p>
      </div>

      {/* Bar chart 1 — retention rate history */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-2">每年有多少去年的廠商今年繼續贊助？（2019–2025）</h2>
        <p className="text-sm text-text-muted mb-4">
          留存率 = 去年有贊助的廠商中，今年繼續合作的比例。灰色柱子（2019–2021）因原始資料不完整，數字僅供參考。<strong>2024→2025 的留存率為 39.7%，是近四年最低點。</strong>
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
          紅柱 = 流失廠商在前一年的合計金額（該收入不再進來）；藍柱 = 留存廠商在前一年的合計金額（成功保住的收入）。2024→2025 的流失均額雖低（每家 84k），但因流失了 47 家，<strong>合計仍達 NTD 3.97M</strong>——低均額是 2024 年大量引入低單價飯店廠商的組合效果，並非情況好轉。
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
        📉 <strong>行動建議：</strong>2024→2025 流失廠商均額雖最低（84k），但因流失數量達 47 家，合計損失 NTD 3.97M，為近三期次高。低均額是組合效果（2024 大量引入低單價飯店廠商），並非情況改善。行動重點：①批次跟進 2025 年友善飯店族群（9 家，詳見新品牌續約率頁）；②同步挽回高單價流失廠商（諾和諾德 220k、羅氏 220k 等，見挽回清單）；③所有現有廠商在合約到期前 3 個月主動啟動溝通。
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

      {/* Line chart trend */}
      {data && (
        <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <h2 className="text-base font-semibold text-foreground mb-4">留存率趨勢（2022–2025，資料完整期）</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart
              data={retention.map((r) => ({ label: r.label, 留存率: r.rate }))}
              margin={{ top: 8, right: 20, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                formatter={(val) => [`${val}%`, '留存率']}
                contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
              />
              <Line type="monotone" dataKey="留存率" stroke="#7c3aed" strokeWidth={2} dot={{ r: 5, fill: '#7c3aed' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Sponsor presence matrix (hotel-excluded) */}
      {data && (
        <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <h2 className="text-base font-semibold text-foreground px-5 pt-4 pb-3 border-b border-border">
            留存詳情（{retention.map((r) => `${r.label}: ${r.retained}/${r.fromCount}`).join('  ·  ')}）
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-bg2">
                  <th className="text-left px-4 py-2 text-text-muted font-medium">廠商</th>
                  {YEARS.map((yr) => (
                    <th key={yr} className="text-center px-3 py-2 text-text-muted font-medium">{yr}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.map((row, i) => (
                  <tr key={row.name} className={i % 2 === 0 ? '' : 'bg-bg2/40'}>
                    <td className="px-4 py-2 text-foreground font-medium">{row.name}</td>
                    {row.years.map(({ yr, present, tier }) => (
                      <td key={yr} className="px-3 py-2 text-center">
                        {present ? (
                          <span
                            className="inline-block px-2 py-0.5 rounded text-xs font-medium"
                            style={{ background: '#f3e8ff', color: '#7c3aed' }}
                          >
                            {tier ? tier.replace('級', '') : '✓'}
                          </span>
                        ) : (
                          <span className="text-border">—</span>
                        )}
                      </td>
                    ))}
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
