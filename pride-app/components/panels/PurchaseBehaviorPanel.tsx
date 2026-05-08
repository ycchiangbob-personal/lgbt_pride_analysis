'use client'

import { useEffect, useMemo, useState } from 'react'

type YearEntry = { cat: string; label: string; amount: number }
type DonorRecord = { donor_id: string; name: string; years: Record<string, YearEntry> }
type PBData = Record<string, DonorRecord>
type PHData = Record<string, Record<string, string[]>>

const PB_YEARS = ['2019','2020','2022','2023','2024','2025']
type Filter = 'all' | 'tier' | 'single' | 'switch'

function chipStyle(cat: string): { bg: string; color: string; border: string } {
  if (cat === 'TIER')   return { bg: '#f3e8ff', color: '#7c3aed', border: '#e9d5ff' }
  if (cat === 'SINGLE') return { bg: '#e0f2fe', color: '#0284c7', border: '#bae6fd' }
  if (cat === 'MARKET') return { bg: '#dcfce7', color: '#059669', border: '#a7f3d0' }
  return { bg: '#f1f5f9', color: '#64748b', border: '#e2e8f0' }
}

export function PurchaseBehaviorPanel() {
  const [pbData, setPbData] = useState<PBData | null>(null)
  const [phData, setPhData] = useState<PHData | null>(null)
  const [filter, setFilter] = useState<Filter>('all')
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetch('/data/purchase_behavior.json').then((r) => r.json()),
      fetch('/data/product_history.json').then((r) => r.json()),
    ]).then(([pb, ph]) => { setPbData(pb); setPhData(ph) })
  }, [])

  const donors = useMemo(() => (pbData ? Object.values(pbData) : []), [pbData])

  const isTier   = (d: DonorRecord) => Object.values(d.years).some((v) => v.cat === 'TIER')
  const isSingle = (d: DonorRecord) => Object.values(d.years).some((v) => v.cat === 'SINGLE')
  const isSwitch = (d: DonorRecord) => isTier(d) && isSingle(d)

  const filtered = useMemo(() => {
    if (filter === 'tier')   return donors.filter(isTier)
    if (filter === 'single') return donors.filter(isSingle)
    if (filter === 'switch') return donors.filter(isSwitch)
    return donors
  }, [donors, filter])

  const tierCount   = donors.filter(isTier).length
  const singleCount = donors.filter(isSingle).length
  const swCount     = donors.filter(isSwitch).length

  if (!pbData) {
    return <div className="flex items-center justify-center h-64 text-text-muted text-sm">載入中…</div>
  }

  const PH_YEARS = ['2022','2023','2024','2025']

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">採購行為分析 2019–2025</h1>
        <p className="text-sm text-text-muted mt-1">
          各廠商在 2019–2025 年間實際採購品項（級別贊助 / 單購花車 / 彩虹市集）。可篩選特定族群，並觀察廠商是否有在「級別贊助」與「單購」之間切換。2021 年因 COVID-19 縮小辦理，無分類資料，故不納入。
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '顯示廠商數', value: filtered.length, color: '#0f172a' },
          { label: '有級別贊助', value: tierCount, color: '#7c3aed' },
          { label: '有單購紀錄', value: singleCount, color: '#0284c7' },
          { label: '曾切換行為', value: swCount, color: '#e8005a' },
        ].map(({ label, value, color }) => (
          <div key={label} className="rounded-xl border border-border bg-surface p-4" style={{ boxShadow: 'var(--shadow-sm)' }}>
            <p className="text-xs text-text-muted mb-1">{label}</p>
            <p className="text-2xl font-bold" style={{ color }}>{value}</p>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex gap-2 flex-wrap">
        {([['all', '全部'], ['tier', '級別贊助者'], ['single', '單購者'], ['switch', '曾切換行為']] as const).map(([f, label]) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className="px-3 py-2 rounded-lg text-sm border transition-colors"
            style={{
              background: filter === f ? '#7c3aed' : '#ffffff',
              color: filter === f ? '#ffffff' : '#475569',
              borderColor: filter === f ? '#7c3aed' : '#e2e8f0',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-3 text-text-muted font-medium">廠商</th>
                {PB_YEARS.map((yr) => (
                  <th key={yr} className="text-center px-3 py-3 text-text-muted font-medium">{yr}</th>
                ))}
                <th className="text-center px-3 py-3 text-text-muted font-medium">屆次</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => {
                const sw = isSwitch(d)
                const isExp = expanded === d.name
                const hist = phData?.[d.name]
                return [
                  <tr
                    key={d.name}
                    onClick={() => setExpanded(isExp ? null : d.name)}
                    className="border-b border-border/50 cursor-pointer hover:bg-bg2/60 transition-colors"
                    style={sw ? { background: 'rgba(139,92,246,.03)' } : {}}
                  >
                    <td className="px-4 py-3 font-medium text-foreground">
                      {d.name}
                      {hist && <span className="ml-2 text-xs text-text-muted">▸ 品項</span>}
                    </td>
                    {PB_YEARS.map((yr) => {
                      const entry = d.years[yr]
                      if (!entry) return <td key={yr} className="px-3 py-3 text-center text-border">—</td>
                      const { bg, color, border } = chipStyle(entry.cat)
                      return (
                        <td key={yr} className="px-3 py-3 text-center">
                          <span
                            className="inline-block px-2 py-0.5 rounded-full text-xs border"
                            style={{ background: bg, color, borderColor: border }}
                          >
                            {entry.label}
                          </span>
                        </td>
                      )
                    })}
                    <td className="px-3 py-3 text-center text-text-muted text-xs">{Object.keys(d.years).length}</td>
                  </tr>,
                  isExp && hist ? (
                    <tr key={`${d.name}-detail`}>
                      <td colSpan={PB_YEARS.length + 2} className="px-6 py-3 bg-bg2/60 border-b border-border">
                        <div className="flex flex-wrap gap-6">
                          {PH_YEARS.map((yr) => {
                            const items = hist[yr]
                            if (!items?.length) return null
                            return (
                              <div key={yr}>
                                <p className="text-xs font-semibold text-text-muted mb-1 uppercase">{yr}</p>
                                <div className="flex flex-wrap gap-1">
                                  {items.map((it: string) => (
                                    <span
                                      key={it}
                                      className="inline-block px-2 py-0.5 rounded text-xs"
                                      style={{ background: '#f0f4ff', color: '#3a5cb5', border: '1px solid #d0dcf5' }}
                                    >
                                      {it}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </td>
                    </tr>
                  ) : null,
                ]
              })}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-2 border-t border-border bg-bg2/40 text-xs text-text-muted">
          共 {filtered.length} 家廠商 · 點擊列展開品項明細
        </div>
      </div>

      {/* Switcher analysis */}
      {swCount > 0 && (
        <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
          <h2 className="text-base font-semibold text-foreground mb-4">切換行為統計（{swCount} 家切換廠商）</h2>
          <SwitcherAnalysis donors={donors.filter(isSwitch)} />
        </div>
      )}

      {/* 品項採購深度分析 */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-1">品項採購深度分析</h2>
          <p className="text-xs text-text-muted mb-3">
            品項黏著度 — 跨年保留率。連續兩年皆採購同一品項的比率。僅含實際可單購品項（排除級別含）。
          </p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">品項</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">保留率</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">採購者</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">定價</th>
              </tr>
            </thead>
            <tbody>
              {[
                { item: '活動看板',       ret: 83, adopters: 32, price: 35000  },
                { item: '手冊廣告版位',   ret: 72, adopters: 32, price: 25000  },
                { item: 'FB+IG 限時動態', ret: 68, adopters: 32, price: 10000  },
                { item: '轉播螢幕廣告',   ret: 72, adopters: 31, price: 18000  },
                { item: '市集獨立棚',     ret: 70, adopters: 25, price: 20000  },
                { item: 'IG 9/11月貼文', ret: 0,  adopters: 21, price: 30000  },
                { item: '商業花車',       ret: 92, adopters: 20, price: 120000 },
                { item: '官網廣告 B',     ret: 62, adopters: 18, price: 50000  },
                { item: 'IG 10月貼文',   ret: 83, adopters: 17, price: 45000  },
                { item: '官網廣告 C',     ret: 33, adopters: 17, price: 20000  },
                { item: 'FB+IG Reels',  ret: 0,  adopters: 16, price: 30000  },
                { item: 'FB 9/11月貼文', ret: 0,  adopters: 16, price: 30000  },
                { item: 'FB 10月貼文',  ret: 60, adopters: 15, price: 45000  },
                { item: 'IG 10月 Reels', ret: 33, adopters: 13, price: 45000  },
                { item: 'IG 9/11月 Reels', ret: 0, adopters: 11, price: 30000 },
                { item: 'IG 11月 Reels', ret: 0,  adopters: 9,  price: 30000  },
                { item: 'IG 11月貼文',   ret: 0,  adopters: 9,  price: 30000  },
                { item: '企業品牌空間 B', ret: 25, adopters: 7,  price: 150000 },
                { item: '官網廣告 A',     ret: 0,  adopters: 6,  price: 80000  },
                { item: '企業品牌空間 A', ret: 67, adopters: 4,  price: 250000 },
                { item: 'FB 11月貼文',   ret: 0,  adopters: 4,  price: 30000  },
              ].map((r, i) => (
                <tr key={r.item} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-2 text-foreground">{r.item}</td>
                  <td className="px-3 py-2 text-right">
                    <div className="inline-flex items-center gap-2 justify-end">
                      <div className="w-16 h-2 rounded bg-gray-100 overflow-hidden">
                        <div
                          className="h-full rounded"
                          style={{
                            width: `${r.ret}%`,
                            background: r.ret >= 70 ? '#059669' : r.ret >= 40 ? '#d97706' : r.ret > 0 ? '#94a3b8' : '#e2e8f0',
                          }}
                        />
                      </div>
                      <span className="text-xs font-medium" style={{ color: r.ret >= 70 ? '#059669' : r.ret >= 40 ? '#d97706' : '#94a3b8', minWidth: 28 }}>
                        {r.ret}%
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-2 text-right text-text-muted text-xs">{r.adopters}</td>
                  <td className="px-3 py-2 text-right text-text-muted text-xs">NT${r.price.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Insights */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-3">💡 定價與包裝設計的關鍵發現</h2>
        <ul className="space-y-3 text-sm text-foreground">
          <li className="flex gap-2">
            <span className="shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-current opacity-50 mt-2" />
            <span><strong>商業花車是最黏的單品（保留率 92%）</strong> — 但定價高於最低級別，導致花車買家每年多付 NT$12k 卻得到更少；這群人是 T5 最容易升購的對象。</span>
          </li>
          <li className="flex gap-2">
            <span className="shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-current opacity-50 mt-2" />
            <span><strong>可口可樂型廠商（只買品牌空間）是潛在 T3 客戶</strong> — 他們連續 3 年花 NT$250k，再加 NT$150k 就能到 T3，應設計「實體體驗限時升級方案」。</span>
          </li>
          <li className="flex gap-2">
            <span className="shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-current opacity-50 mt-2" />
            <span><strong>犀牛盾型廠商（自組高額單購）付了 T2 的錢卻沒有 T2 的名分</strong> — 他們要的是實體佈局（空間＋花車首位＋打卡牆），而非數位曝光；現有級別設計未能滿足此偏好。</span>
          </li>
          <li className="flex gap-2">
            <span className="shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-current opacity-50 mt-2" />
            <span><strong>社群類品項保留率普遍為 0%</strong> — 廠商每年重新拼湊，說明這類品項沒有粘性；考慮整合成「社群套包」固定銷售。</span>
          </li>
          <li className="flex gap-2">
            <span className="shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-current opacity-50 mt-2" />
            <span><strong>活動看板（83%）、轉播螢幕（72%）、手冊版位（72%）是最穩定的非花車品項</strong> — 這三項是跨類型廠商的共同偏好，建議納入所有級別包的基本配備。</span>
          </li>
        </ul>
      </div>

      {/* 2025 首次購買廠商 */}
      <div className="rounded-xl border border-border bg-surface p-5" style={{ boxShadow: 'var(--shadow-sm)' }}>
        <h2 className="text-base font-semibold text-foreground mb-4">2025 首次購買廠商（13 家）</h2>
        <div className="flex flex-wrap gap-8">
          {([
            { cat: '級別贊助', count: 3, color: '#0284c7', bg: '#e0f2fe',
              items: [
                { name: 'JINS', note: 'T3 鈦金 NT$500,000' },
                { name: 'Johnnie Walker', note: 'T4 銀 NT$220,000' },
                { name: 'TFC 臺北婦產科診所', note: 'T5 銅 NT$120,000' },
              ]},
            { cat: '單購花車', count: 5, color: '#059669', bg: '#dcfce7',
              items: [
                { name: 'IM Adult', note: '花車 NT$120,000' },
                { name: 'TSMC', note: '花車 NT$120,000' },
                { name: 'FNF', note: '花車 NT$120,000' },
                { name: '華納兄弟', note: '單買 NT$36,000' },
                { name: '新思科技', note: '單買 NT$10,000' },
              ]},
            { cat: '彩虹市集', count: 1, color: '#d97706', bg: '#fef9c3',
              items: [
                { name: 'TENGA', note: '市集' },
              ]},
            { cat: '其他', count: 4, color: '#64748b', bg: '#f1f5f9',
              items: [
                { name: '聯名商品', note: '其他 NT$160,000' },
                { name: '環球影城', note: '其他 NT$36,000' },
                { name: '一口純淨', note: '其他' },
                { name: 'Precision Biotics', note: '其他' },
              ]},
          ] as const).map(({ cat, count, color, bg, items }) => (
            <div key={cat}>
              <p className="text-xs font-semibold mb-2" style={{ color }}>{cat} ({count})</p>
              <div className="flex flex-wrap gap-1.5">
                {items.map(({ name, note }) => (
                  <span
                    key={name}
                    title={note}
                    className="inline-block px-2 py-0.5 rounded text-xs cursor-default"
                    style={{ background: bg, color }}
                  >
                    {name}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function SwitcherAnalysis({ donors }: { donors: DonorRecord[] }) {
  let t2s: string[] = [], s2t: string[] = [], t2out: string[] = [], s2out: string[] = []
  donors.forEach((d) => {
    const yrs = Object.keys(d.years).map(Number).sort((a, b) => a - b)
    for (let i = 0; i < yrs.length - 1; i++) {
      const a = String(yrs[i]), b = String(yrs[i + 1])
      const catA = d.years[a]?.cat, catB = d.years[b]?.cat
      if (catA === 'TIER'   && catB === 'SINGLE') t2s.push(d.name)
      if (catA === 'SINGLE' && catB === 'TIER')   s2t.push(d.name)
    }
    const lastYr = String(Math.max(...yrs))
    if (d.years[lastYr]?.cat === 'TIER'   && lastYr !== '2025') t2out.push(d.name)
    if (d.years[lastYr]?.cat === 'SINGLE' && lastYr !== '2025') s2out.push(d.name)
  })

  const items = [
    { label: '級別 → 單購（降購）', names: t2s, color: '#e8005a' },
    { label: '單購 → 級別（升購）', names: s2t, color: '#7c3aed' },
    { label: '末年為級別後流失', names: t2out, color: '#94a3b8' },
    { label: '末年為單購後流失', names: s2out, color: '#94a3b8' },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {items.map(({ label, names, color }) => (
        <div key={label} className="rounded-lg border border-border p-3">
          <p className="text-xs text-text-muted mb-1">{label}</p>
          <p className="text-xl font-bold mb-1" style={{ color }}>{names.length}</p>
          <p className="text-xs text-text-muted">
            {names.length ? names.slice(0, 3).join('、') + (names.length > 3 ? ` 等 ${names.length} 家` : '') : '—'}
          </p>
        </div>
      ))}
    </div>
  )
}
