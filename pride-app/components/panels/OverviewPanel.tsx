'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LabelList, ResponsiveContainer,
  LineChart, Line, ReferenceLine,
} from 'recharts'

type YearData = {
  '級別贊助': { count: number; amount: number }
  '單購':     { count: number; amount: number }
  '市集':     { count: number; amount: number }
  '其他':     { count: number; amount: number }
  total?: number
}
type Summary = Record<string, YearData>

const YEARS       = ['2016','2017','2018','2019','2020','2022','2023','2024','2025']
const TABLE_YEARS = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']

const YEAR_META: Record<string, { edition: number; theme: string }> = {
  '2016': { edition: 14, theme: '一起FUN出來—打破假友善，你我撐自在' },
  '2017': { edition: 15, theme: '澀澀性平打開開，多元教慾跟上來' },
  '2018': { edition: 16, theme: '性平攻略由你說，人人18投彩虹' },
  '2019': { edition: 17, theme: '同志好厝邊' },
  '2020': { edition: 18, theme: '成人之美' },
  '2021': { edition: 19, theme: '友善日常（COVID-19 線上形式）' },
  '2022': { edition: 20, theme: '無限性' },
  '2023': { edition: 21, theme: '與多元同行 STAND WITH DIVERSITY' },
  '2024': { edition: 22, theme: '邁向共榮 交織共生' },
  '2025': { edition: 23, theme: '超·連結' },
}

const CAT_COLORS: Record<string, string> = {
  '級別贊助': '#7c3aed',
  '單購':     '#0284c7',
  '市集':     '#059669',
  '其他':     '#94a3b8',
}
const LINE_KEYS  = ['合計', '級別贊助', '單購', '市集', '其他'] as const
const LINE_COLORS: Record<string, string> = {
  '合計':    '#0f172a',
  '級別贊助':'#7c3aed',
  '單購':    '#0284c7',
  '市集':    '#059669',
  '其他':    '#94a3b8',
}

function fmtNTD(n: number) {
  if (n >= 1_000_000) return `NT$${(n / 1_000_000).toFixed(2)}M`
  if (n >= 10_000)    return `NT$${(n / 10_000).toFixed(0)}萬`
  return `NT$${n.toLocaleString()}`
}

function fmtShort(n: number) {
  if (!n) return '—'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`
  if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}k`
  return `${n}`
}

function KpiCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
      <p className="text-sm text-text-muted mb-1">{label}</p>
      <p className="text-2xl font-bold text-foreground leading-tight">{value}</p>
      {sub && <p className="text-xs text-text-muted mt-1">{sub}</p>}
    </div>
  )
}

export function OverviewPanel() {
  const [summary, setSummary] = useState<Summary | null>(null)
  const [activeLine, setActiveLine] = useState<string | null>(null)
  const [barMode, setBarMode] = useState<'amount' | 'ratio' | 'count'>('amount')

  useEffect(() => {
    fetch('/data/cross_year_summary.json')
      .then((r) => r.json())
      .then(setSummary)
  }, [])

  const getTotal = (yr: string): number => {
    const d = summary?.[yr]
    if (!d) return 0
    if (typeof d.total === 'number') return d.total
    return Object.values(d).reduce<number>((s, v) => {
      if (typeof v === 'object' && v !== null && 'amount' in v) return s + ((v as { amount: number }).amount ?? 0)
      return s
    }, 0)
  }

  const tableRows = useMemo(() => {
    if (!summary) return []
    return TABLE_YEARS.map((yr) => {
      const d = summary[yr] ?? {}
      return {
        yr,
        tier:      d['級別贊助']?.amount ?? 0,
        tierCnt:   d['級別贊助']?.count  ?? 0,
        single:    d['單購']?.amount    ?? 0,
        singleCnt: d['單購']?.count     ?? 0,
        market:    d['市集']?.amount    ?? 0,
        marketCnt: d['市集']?.count     ?? 0,
        other:     d['其他']?.amount    ?? 0,
        otherCnt:  d['其他']?.count     ?? 0,
        total:     getTotal(yr),
      }
    })
  }, [summary])

  // Bar chart data — _total stored per row so LabelList can read it directly
  const barData = useMemo(() => {
    if (!summary) return []
    return YEARS.map((yr) => {
      const d = summary[yr] ?? {}
      if (barMode === 'count') {
        const tier   = d['級別贊助']?.count ?? 0
        const single = d['單購']?.count    ?? 0
        const market = d['市集']?.count    ?? 0
        const other  = d['其他']?.count    ?? 0
        return { yr, '級別贊助': tier, '單購': single, '市集': market, '其他': other,
                 _total: tier + single + market + other }
      }
      const tierAmt   = d['級別贊助']?.amount ?? 0
      const singleAmt = d['單購']?.amount    ?? 0
      const marketAmt = d['市集']?.amount    ?? 0
      const otherAmt  = d['其他']?.amount    ?? 0
      const totalAmt  = tierAmt + singleAmt + marketAmt + otherAmt
      if (barMode === 'ratio' && totalAmt > 0) {
        const tier   = Math.round((tierAmt   / totalAmt) * 100)
        const single = Math.round((singleAmt / totalAmt) * 100)
        const market = Math.round((marketAmt / totalAmt) * 100)
        const other  = Math.round((otherAmt  / totalAmt) * 100)
        return { yr, '級別贊助': tier, '單購': single, '市集': market, '其他': other, _total: 100 }
      }
      const tier   = Math.round(tierAmt   / 10000)
      const single = Math.round(singleAmt / 10000)
      const market = Math.round(marketAmt / 10000)
      const other  = Math.round(otherAmt  / 10000)
      return { yr, '級別贊助': tier, '單購': single, '市集': market, '其他': other,
               _total: tier + single + market + other }
    })
  }, [summary, barMode])

  // Line chart data
  const lineData = useMemo(() => {
    if (!summary) return []
    return YEARS.map((yr) => {
      const d = summary[yr] ?? {}
      const tier   = Math.round((d['級別贊助']?.amount ?? 0) / 10000)
      const single = Math.round((d['單購']?.amount    ?? 0) / 10000)
      const market = Math.round((d['市集']?.amount    ?? 0) / 10000)
      const other  = Math.round((d['其他']?.amount    ?? 0) / 10000)
      return { yr, '合計': tier + single + market + other, '級別贊助': tier, '單購': single, '市集': market, '其他': other }
    })
  }, [summary])

  // Y-axis domain zooms to the active line's range when one is selected
  const lineDomain = useMemo<[number, number] | ['auto', 'auto']>(() => {
    if (!activeLine || !lineData.length) return ['auto', 'auto']
    const vals = lineData.map((d) => (d as unknown as Record<string, number>)[activeLine]).filter((v) => typeof v === 'number' && v > 0)
    if (!vals.length) return [0, 100]
    const lo = Math.min(...vals), hi = Math.max(...vals)
    const pad = Math.max(20, Math.round((hi - lo) * 0.2))
    return [Math.max(0, lo - pad), hi + pad]
  }, [activeLine, lineData])

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleLegendClick = (entry: any) => {
    const key = String(entry.dataKey ?? entry.value ?? '')
    setActiveLine((prev) => (prev === key ? null : key))
  }

  if (!summary) {
    return <div className="flex items-center justify-center h-64 text-text-muted text-sm">載入中…</div>
  }

  const maxYr   = YEARS.reduce((best, yr) => getTotal(yr) > getTotal(best) ? yr : best, '2016')
  const count25 = Object.values(summary['2025'] ?? {})
    .filter((v): v is { count: number; amount: number } => typeof v === 'object')
    .reduce((s, v) => s + v.count, 0)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">商業贊助全景</h1>
        <p className="text-sm text-text-muted mt-1">2016–2025 年度跨年度分析（第 14–23 屆）</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="2025 年總收入"   value={fmtNTD(getTotal('2025'))} sub="第 23 屆" />
        <KpiCard label="歷史最高年份"    value={fmtNTD(getTotal(maxYr))}  sub={`${maxYr} 年`} />
        <KpiCard label="2025 活躍廠商數" value={`${count25} 家`}          sub="各類別加總" />
        <KpiCard label="資料涵蓋年份"    value="10 年"                    sub="2016–2025（不含 2021）" />
      </div>

      {/* ── Bar chart ──────────────────────────────────────────────────── */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-foreground">各年度收入結構</h2>
          <div className="flex gap-1">
            {([['amount', '贊助金額'], ['ratio', '金額比例'], ['count', '廠商數']] as const).map(([m, label]) => (
              <button
                key={m}
                onClick={() => setBarMode(m)}
                className="px-3 py-1.5 rounded-lg text-xs border transition-colors"
                style={{
                  background: barMode === m ? '#7c3aed' : '#ffffff',
                  color: barMode === m ? '#ffffff' : '#475569',
                  borderColor: barMode === m ? '#7c3aed' : '#e2e8f0',
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={barData} margin={{ top: 30, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="yr" tick={{ fontSize: 12, fill: '#94a3b8' }} />
            <YAxis
              tick={{ fontSize: 12, fill: '#94a3b8' }}
              tickFormatter={(v) => barMode === 'ratio' ? `${v}%` : barMode === 'count' ? `${v}` : `${v}萬`}
            />
            <Tooltip
              formatter={(val, name) => {
                if (barMode === 'ratio') return [`${val}%`, name]
                if (barMode === 'count') return [`${val} 家`, name]
                return [`NT$${(Number(val) * 10000).toLocaleString()}`, name]
              }}
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {Object.entries(CAT_COLORS).map(([name, color], idx, arr) => (
              <Bar key={name} dataKey={name} stackId="a" fill={color}>
                <LabelList
                  dataKey={name}
                  position="center"
                  style={{ fill: '#fff', fontSize: 9, fontWeight: 700 }}
                  formatter={(v: unknown) => {
                    const n = Number(v)
                    if (barMode === 'ratio') return n >= 10 ? `${n}%` : ''
                    if (barMode === 'count') return n >= 5 ? `${n}` : ''
                    return n >= 80 ? `${n}萬` : ''
                  }}
                />
                {idx === arr.length - 1 && (
                  <LabelList
                    dataKey="_total"
                    position="top"
                    style={{ fontSize: 10, fontWeight: 700, fill: '#475569' }}
                    formatter={(v: unknown) => {
                      const n = Number(v)
                      if (!n) return ''
                      if (barMode === 'ratio') return `${n}%`
                      if (barMode === 'count') return `${n}`
                      return `${n}萬`
                    }}
                  />
                )}
              </Bar>
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Line chart with click-to-zoom ────────────────────────────── */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-base font-semibold text-foreground">逐年趨勢（萬元）</h2>
          {activeLine && (
            <button
              onClick={() => setActiveLine(null)}
              className="text-xs px-3 py-1 rounded-full border border-border text-text-muted hover:text-foreground transition-colors"
            >
              顯示全部
            </button>
          )}
        </div>
        <p className="text-xs text-text-muted mb-4">
          點選圖例項目可單獨檢視該類別趨勢並標示金額，再次點選還原
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={lineData} margin={{ top: 8, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="yr" tick={{ fontSize: 12, fill: '#94a3b8' }} />
            <YAxis
              domain={lineDomain}
              tick={{ fontSize: 12, fill: '#94a3b8' }}
              tickFormatter={(v) => `${v}萬`}
            />
            <Tooltip
              formatter={(val, name) => [`NT$${(Number(val) * 10000).toLocaleString()}`, name]}
              contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
            />
            <Legend
              wrapperStyle={{ fontSize: 12, cursor: 'pointer' }}
              onClick={handleLegendClick}
            />
            {LINE_KEYS.map((key) => {
              const isActive  = activeLine === null || activeLine === key
              const isFocused = activeLine === key
              return (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={LINE_COLORS[key]}
                  strokeWidth={isFocused ? 3 : isActive ? 2 : 1}
                  strokeDasharray={key === '合計' ? '6 3' : undefined}
                  opacity={isActive ? 1 : 0.15}
                  dot={{
                    r: isFocused ? 6 : isActive ? 4 : 3,
                    fill: LINE_COLORS[key],
                    strokeWidth: 0,
                    cursor: 'pointer',
                  }}
                  activeDot={{ r: 7, strokeWidth: 0 }}
                  connectNulls
                />
              )
            })}
            {/* Vertical reference at 2021 gap */}
            <ReferenceLine x="2020" stroke="#e2e8f0" strokeDasharray="4 4" label={{ value: '2021 停辦', position: 'top', fontSize: 9, fill: '#94a3b8' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── 逐年明細 table ──────────────────────────────────────────────── */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground px-5 pt-4 pb-3 border-b border-border">逐年明細</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">年度</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium whitespace-nowrap">屆</th>
                <th className="text-center px-3 py-2 text-text-muted font-medium whitespace-nowrap">級別贊助廠商數</th>
                <th className="text-right px-4 py-2 text-text-muted font-medium whitespace-nowrap">總贊助金額</th>
                <th className="text-left px-5 py-2 text-text-muted font-medium">分類結構</th>
                <th className="text-left px-4 py-2 text-text-muted font-medium whitespace-nowrap">金額比例</th>
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, i) => {
                const meta = YEAR_META[row.yr]
                const cats = [
                  { label: '級別', amt: row.tier,   cnt: row.tierCnt,   unit: '家', bg: '#fff7ed', color: '#c2410c' },
                  { label: '單購', amt: row.single,  cnt: row.singleCnt, unit: '家', bg: '#e0f2fe', color: '#0284c7' },
                  { label: '市集', amt: row.market,  cnt: row.marketCnt, unit: '棚', bg: '#dcfce7', color: '#059669' },
                  { label: '其他', amt: row.other,   cnt: row.otherCnt,  unit: '家', bg: '#f1f5f9', color: '#64748b' },
                ].filter((c) => c.amt > 0)
                const pct = (n: number) => row.total > 0 ? Math.round((n / row.total) * 100) : 0
                return (
                  <tr key={row.yr} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/40' : ''} hover:bg-bg2/70 transition-colors`}>
                    {/* 年度 + 主題 */}
                    <td className="px-4 py-3 min-w-40">
                      <p className="font-bold text-foreground">{row.yr}</p>
                      {meta && <p className="text-xs text-text-muted mt-0.5 leading-snug">{meta.theme}</p>}
                    </td>
                    {/* 屆 */}
                    <td className="px-3 py-3 text-center">
                      {meta && (
                        <span className="inline-block px-2 py-1 rounded-lg text-xs font-semibold bg-bg2 text-text-secondary whitespace-nowrap">
                          第{meta.edition}屆
                        </span>
                      )}
                    </td>
                    {/* 級別贊助廠商數 */}
                    <td className="px-3 py-3 text-center font-medium text-foreground">
                      {row.tierCnt > 0 ? row.tierCnt : '—'}
                    </td>
                    {/* 總贊助金額 */}
                    <td className="px-4 py-3 text-right font-bold text-foreground whitespace-nowrap">
                      {row.yr === '2021' ? '≥' : ''}NTD {row.total.toLocaleString()}
                    </td>
                    {/* 分類結構 */}
                    <td className="px-5 py-3">
                      <div className="flex flex-wrap gap-2">
                        {cats.map(({ label, amt, cnt, unit, bg, color }) => (
                          <div key={label} className="rounded-lg px-2.5 py-1.5 text-xs leading-tight" style={{ background: bg, color }}>
                            <div className="font-semibold">{label}</div>
                            <div className="font-bold">{fmtShort(amt)}</div>
                            <div className="opacity-70">{cnt}{unit}</div>
                          </div>
                        ))}
                      </div>
                    </td>
                    {/* 金額比例 */}
                    <td className="px-4 py-3">
                      <div className="flex h-2 w-24 rounded overflow-hidden mb-1">
                        {[
                          { amt: row.tier,   color: '#c2410c' },
                          { amt: row.single, color: '#0284c7' },
                          { amt: row.market, color: '#059669' },
                          { amt: row.other,  color: '#94a3b8' },
                        ].map(({ amt, color }, j) =>
                          amt > 0 ? <div key={j} style={{ width: `${pct(amt)}%`, background: color }} /> : null
                        )}
                      </div>
                      <p className="text-xs text-text-muted whitespace-nowrap">
                        {pct(row.tier)}% / {pct(row.single)}% / {pct(row.market)}% / {pct(row.other)}%
                      </p>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 分類定義 */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground px-5 pt-4 pb-3 border-b border-border">分類定義</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">分類</th>
                <th className="text-left px-4 py-2 text-text-muted font-medium">涵蓋級別</th>
                <th className="text-left px-4 py-2 text-text-muted font-medium">說明</th>
              </tr>
            </thead>
            <tbody>
              {[
                {
                  cat: '級別贊助',
                  tiers: 'T1(≥800k), T2(500–799k), T3(300–499k), T4(150–299k), T5(40–149k)',
                  desc: '依固定牌價購買整套贊助方案。2019 年起正式設立。T1–T5 為統一代稱，歷年實際名稱有所調整（如白金、黃金、鈦金等），以 T1–T5 為準避免混淆。',
                },
                {
                  cat: '單購',
                  tiers: '單買、花車路權、友善飯店',
                  desc: '個別選購特定品項，不進入整套級別方案。2020 起有商業車分項，2023 起有友善飯店方案。',
                },
                {
                  cat: '市集',
                  tiers: '彩虹市集獨立棚（20k/頂）、合併棚（10k/頂）',
                  desc: '純市集攤位。NGO 棚不計入收入。若已為級別贊助商，不重複收市集費。',
                },
                {
                  cat: '其他',
                  tiers: '未分級合作、跨界合作、聯盟/協會型贊助',
                  desc: '2016–2018 因無級別制度，所有廠商歸此類。2019 後為客製化或非標準方案。',
                },
              ].map((r, i) => (
                <tr key={r.cat} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/40' : ''}`}>
                  <td className="px-4 py-3 font-semibold text-foreground whitespace-nowrap">{r.cat}</td>
                  <td className="px-4 py-3 text-xs text-text-secondary">{r.tiers}</td>
                  <td className="px-4 py-3 text-xs text-text-muted">{r.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
