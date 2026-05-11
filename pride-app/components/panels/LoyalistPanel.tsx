'use client'

import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList,
} from 'recharts'

const TIER_CHIP: Record<string, [string, string]> = {
  T1:   ['#B8860B20', '#B8860B'],
  T2:   ['#E8A60020', '#E8A600'],
  T3:   ['#4472C420', '#4472C4'],
  T4:   ['#70AD4720', '#70AD47'],
  T5:   ['#ED7D3120', '#ED7D31'],
  '花車': ['#5BC0EB20', '#5BC0EB'],
  '單買': ['#5BC0EB20', '#5BC0EB'],
  '其他': ['#aaa2', '#aaa'],
  '—':   ['#ddd2', '#bbb'],
}

function TierChip({ tier }: { tier: string }) {
  const key = Object.keys(TIER_CHIP).find((k) => tier.startsWith(k)) ?? '其他'
  const [bg, color] = TIER_CHIP[key]
  return (
    <span className="inline-block px-2 py-0.5 rounded text-xs font-medium" style={{ background: bg, color }}>
      {tier || '—'}
    </span>
  )
}

type Loyalist = {
  name: string; ind: string; maxRun: number; totalYears: number
  tiers: [string, string, string, string]
  amounts: [number, number, number, number]
  avgAmount: number; total: number
}

const DATA: Loyalist[] = [
  { name: 'GILEAD',         ind: '醫藥',   maxRun: 4, totalYears: 6,  tiers: ['T1','T2','T3','T4'],   amounts: [1000000,1000000,550000,230000], avgAmount: 695000,  total: 2780000 },
  { name: '美光',           ind: '科技',   maxRun: 4, totalYears: 4,  tiers: ['T3','T3','T3','T3'],   amounts: [300000,400000,405000,405000],   avgAmount: 377500,  total: 1510000 },
  { name: '波士頓',         ind: '醫材',   maxRun: 4, totalYears: 4,  tiers: ['單買','T3','T3','T3'],  amounts: [25000,400000,405000,405000],   avgAmount: 308750,  total: 1235000 },
  { name: '諾億保經',       ind: '金融',   maxRun: 4, totalYears: 6,  tiers: ['T4','T4','T4','T3'],   amounts: [150000,180000,198000,405000],   avgAmount: 233250,  total: 933000  },
  { name: '拉拉公園',       ind: '生活',   maxRun: 4, totalYears: 10, tiers: ['T3','T4','T4','T4'],   amounts: [300000,180000,198000,198000],   avgAmount: 219000,  total: 876000  },
  { name: 'UBer',           ind: '生活',   maxRun: 4, totalYears: 7,  tiers: ['單買','T4','花車','花車'], amounts: [310000,190000,250000,120000], avgAmount: 217500,  total: 870000  },
  { name: 'VERVE',          ind: '服飾',   maxRun: 3, totalYears: 3,  tiers: ['—','T4','T4','花車'],   amounts: [0,180000,240000,350000],       avgAmount: 256667,  total: 770000  },
  { name: '可口可樂',       ind: '生活',   maxRun: 3, totalYears: 3,  tiers: ['其他','單買','單買','單買'], amounts: [0,250000,250000,250000],   avgAmount: 250000,  total: 750000  },
  { name: 'Google',         ind: '科技',   maxRun: 4, totalYears: 5,  tiers: ['T4','T4','T4','T4'],   amounts: [170000,180000,198000,198000],   avgAmount: 186500,  total: 746000  },
  { name: '台虎',           ind: '生活',   maxRun: 4, totalYears: 6,  tiers: ['花車','T4','T4','T4'],  amounts: [249000,100000,198000,198000],   avgAmount: 186250,  total: 745000  },
  { name: 'AZ',             ind: '醫藥',   maxRun: 4, totalYears: 5,  tiers: ['T4','T4','T4','T4'],   amounts: [155000,180000,198000,198000],   avgAmount: 182750,  total: 731000  },
  { name: 'GSK',            ind: '醫藥',   maxRun: 4, totalYears: 6,  tiers: ['T4','T4','T4','T4'],   amounts: [150000,180000,198000,198000],   avgAmount: 181500,  total: 726000  },
  { name: 'G-Star',         ind: '夜店',   maxRun: 4, totalYears: 4,  tiers: ['T4','T4','T4','T4'],   amounts: [150000,180000,198000,198000],   avgAmount: 181500,  total: 726000  },
  { name: 'NIKE',           ind: '運動',   maxRun: 4, totalYears: 4,  tiers: ['單買','T4','花車','花車'], amounts: [250000,230000,120000,120000], avgAmount: 180000,  total: 720000  },
  { name: 'Unilever',       ind: 'FMCG',  maxRun: 4, totalYears: 6,  tiers: ['T4','T4','T5','T4'],   amounts: [170000,150000,120000,198000],   avgAmount: 159500,  total: 638000  },
  { name: '高通',           ind: '科技',   maxRun: 3, totalYears: 3,  tiers: ['T4','T4','T4','—'],    amounts: [150000,180000,198000,0],        avgAmount: 176000,  total: 528000  },
  { name: 'GAP',            ind: '服飾',   maxRun: 4, totalYears: 8,  tiers: ['單買','花車','花車','花車'], amounts: [100000,120000,120000,120000], avgAmount: 115000, total: 460000  },
  { name: '彩虹酷兒健康文化中心', ind: 'NGO', maxRun: 4, totalYears: 8, tiers: ['單買','花車','花車','花車'], amounts: [100000,120000,120000,120000], avgAmount: 115000, total: 460000 },
  { name: 'M.A.C',          ind: '彩妝',   maxRun: 3, totalYears: 4,  tiers: ['—','T4','T4','其他'],   amounts: [0,180000,198000,44000],         avgAmount: 140667, total: 422000  },
  { name: '默沙東',         ind: '醫藥',   maxRun: 3, totalYears: 3,  tiers: ['—','T4','T5','T5'],    amounts: [0,180000,120000,108000],        avgAmount: 136000,  total: 408000  },
  { name: 'Sagami',         ind: '生活',   maxRun: 4, totalYears: 4,  tiers: ['單買','單買','單買','單買'], amounts: [49000,30000,60000,63000],   avgAmount: 50500,   total: 202000  },
  { name: '台灣百健',       ind: '醫藥',   maxRun: 3, totalYears: 5,  tiers: ['—','單買','單買','單買'], amounts: [0,55000,25000,20000],          avgAmount: 33333,   total: 100000  },
  { name: '辻利茶舖',       ind: '食品',   maxRun: 4, totalYears: 10, tiers: ['單買','單買','單買','單買'], amounts: [15000,25000,25000,25000],  avgAmount: 22500,   total: 90000   },
]

const CHART_DATA = [...DATA].sort((a, b) => b.total - a.total).map((d) => ({
  name: d.name,
  total: d.total,
}))

const MAX_AMT = Math.max(...DATA.map((d) => Math.max(...d.amounts)))

function calcDelta(d: Loyalist) {
  const first = d.amounts.find((a) => a > 0) ?? 0
  const last = [...d.amounts].reverse().find((a) => a > 0) ?? 0
  const overall = last - first
  const latestPct = d.amounts[2] > 0 ? ((d.amounts[3] - d.amounts[2]) / d.amounts[2]) * 100 : null
  return { overall, latestPct }
}

const MAX_DELTA = Math.max(...DATA.map((d) => Math.abs(calcDelta(d).overall)))

function fmt(n: number) {
  if (n === 0) return '—'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`
  return `${(n / 1000).toFixed(0)}k`
}

function fmtDelta(n: number) {
  if (n === 0) return null
  const abs = Math.abs(n)
  const str = abs >= 1_000_000 ? `${(abs / 1_000_000).toFixed(2)}M` : `${(abs / 1000).toFixed(0)}k`
  return (n > 0 ? '+' : '−') + str
}

export function LoyalistPanel() {
  const [view, setView] = useState<'tier' | 'amount'>('tier')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">忠實贊助商輪廓</h1>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <p className="text-sm text-text-muted mb-1">4 屆全勤</p>
          <p className="text-2xl font-bold text-foreground">{DATA.filter((d) => d.maxRun === 4).length} 家</p>
        </div>
        <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <p className="text-sm text-text-muted mb-1">連續 3 年以上</p>
          <p className="text-2xl font-bold" style={{ color: '#7c3aed' }}>{DATA.length} 家</p>
        </div>
        <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <p className="text-sm text-text-muted mb-1">合計贊助金額</p>
          <p className="text-2xl font-bold" style={{ color: '#e8005a' }}>
            {(DATA.reduce((s, d) => s + d.total, 0) / 1_000_000).toFixed(2)}M
          </p>
        </div>
      </div>

      {/* Bar chart section */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-1">2022–2025 年連續贊助 3 年以上的廠商（共 23 家）</h2>
        <p className="text-sm text-text-muted mb-4">
          這 23 家廠商是最穩定的收入來源，連續贊助 3 年以上。圖表依「年均金額 × 連續年數」排序；表格可切換顯示各年度贊助類別或實際金額。
        </p>
        <ResponsiveContainer width="100%" height={700}>
          <BarChart data={CHART_DATA} layout="vertical" margin={{ top: 4, right: 90, left: 10, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v) => `${(v / 10000).toFixed(0)}萬`} />
            <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12, fill: '#334155' }} />
            <Tooltip
              formatter={(val) => [`NT$${Number(val).toLocaleString()}`, '贊助總金額']}
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
            />
            <Bar dataKey="total" fill="#4472C4" radius={[0, 4, 4, 0]}>
              <LabelList
                dataKey="total"
                position="right"
                style={{ fontSize: 11, fill: '#475569' }}
                formatter={(v: unknown) => `NT$${(Number(v) / 10000).toFixed(0)}萬`}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Toggle + detail table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="px-5 pt-4 pb-3 border-b border-border flex items-center gap-3 flex-wrap">
          <h2 className="text-base font-semibold text-foreground">忠實廠商詳情</h2>
          <div className="flex gap-2 ml-auto">
            {(['tier', 'amount'] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className="px-3 py-1.5 rounded-lg text-sm border transition-colors"
                style={{
                  background: view === v ? '#7c3aed' : '#ffffff',
                  color: view === v ? '#ffffff' : '#475569',
                  borderColor: view === v ? '#7c3aed' : '#e2e8f0',
                }}
              >
                {v === 'tier' ? '各年贊助類別' : '各年贊助金額'}
              </button>
            ))}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商名稱</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">產業</th>
                <th className="text-center px-2 py-2 text-text-muted font-medium whitespace-nowrap">連續/參與</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium">2022</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium">2023</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium">2024</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium">2025</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium whitespace-nowrap">整體趨勢</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium whitespace-nowrap">24→25</th>
                <th className="text-right px-4 py-2 text-text-muted font-medium">年均金額</th>
              </tr>
            </thead>
            <tbody>
              {DATA.map((d, i) => (
                <tr key={d.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/40' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground whitespace-nowrap">{d.name}</td>
                  <td className="px-3 py-2 text-xs text-text-muted">{d.ind}</td>
                  <td className="px-2 py-2 text-center text-xs text-text-secondary whitespace-nowrap">{d.maxRun}/{d.totalYears}</td>
                  {view === 'tier'
                    ? d.tiers.map((t, j) => (
                        <td key={j} className="px-3 py-2 text-center">
                          <TierChip tier={t} />
                        </td>
                      ))
                    : d.amounts.map((a, j) => (
                        <td key={j} className="px-3 py-2 text-center">
                          {a > 0 ? (
                            <div className="flex flex-col items-center gap-0.5">
                              <div className="h-1.5 rounded bg-blue-200 w-16 overflow-hidden">
                                <div
                                  className="h-full rounded"
                                  style={{ width: `${(a / MAX_AMT) * 100}%`, background: '#4472C4' }}
                                />
                              </div>
                              <span className="text-xs text-text-secondary">{fmt(a)}</span>
                            </div>
                          ) : (
                            <span className="text-border text-xs">—</span>
                          )}
                        </td>
                      ))}
                  {(() => {
                    const { overall, latestPct } = calcDelta(d)
                    const deltaLabel = fmtDelta(overall)
                    const barWidth = MAX_DELTA > 0 ? (Math.abs(overall) / MAX_DELTA) * 48 : 0
                    const deltaColor = overall > 0 ? '#059669' : overall < 0 ? '#e8005a' : '#94a3b8'
                    return (
                      <>
                        <td className="px-3 py-2 text-center">
                          {deltaLabel ? (
                            <div className="flex flex-col items-center gap-0.5">
                              <div className="h-1.5 rounded bg-slate-100 overflow-hidden" style={{ width: 48 }}>
                                <div className="h-full rounded" style={{ width: barWidth, background: deltaColor }} />
                              </div>
                              <span className="text-xs font-medium" style={{ color: deltaColor }}>{deltaLabel}</span>
                            </div>
                          ) : (
                            <span className="text-xs text-border">—</span>
                          )}
                        </td>
                        <td className="px-3 py-2 text-center">
                          {latestPct === null ? (
                            <span className="text-xs text-border">—</span>
                          ) : (
                            <span className="text-xs font-semibold" style={{ color: latestPct > 0 ? '#059669' : latestPct < 0 ? '#e8005a' : '#94a3b8' }}>
                              {latestPct > 0 ? '+' : ''}{latestPct.toFixed(1)}%
                            </span>
                          )}
                        </td>
                      </>
                    )
                  })()}
                  <td className="px-4 py-2 text-right text-xs font-medium text-foreground whitespace-nowrap">
                    NT${d.avgAmount.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action box */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        🎯 <strong>行動建議：</strong>這份名單是 2026 業務的第一優先拜訪清單。第一季前確認每一家是否延續合作，並詢問是否有升級意願。鞏固這 23 家，等同於保住收入基礎的主要部分。
      </div>
    </div>
  )
}
