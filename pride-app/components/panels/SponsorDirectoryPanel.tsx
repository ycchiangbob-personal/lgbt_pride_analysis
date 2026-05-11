'use client'

import { useEffect, useMemo, useState } from 'react'
import { BASE } from '@/lib/basePath'

type Sponsor = {
  col: number; name_orig: string; name_canonical: string
  tier_orig: string; industry: string; lead: string; contact: string
  amount: number; amount_source: string
}
type AllData = Record<string, Sponsor[]>

const YEARS = ['2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016']

// A/B/C are 友善飯店 pricing tier codes, not industry names; Ｖ is a stray data artifact
function normalizeIndustry(ind: string): string {
  if (ind === 'A' || ind === 'B' || ind === 'C') return '飯店'
  if (ind === 'Ｖ') return ''
  return ind
}

function tierChip(tier: string) {
  if (!tier) return null
  const map: Record<string, { bg: string; color: string; border: string }> = {
    '白金級': { bg: '#f3e8ff', color: '#7c3aed', border: '#e9d5ff' },
    '黃金級': { bg: '#fff0f6', color: '#e8005a', border: '#fbb6c8' },
    '鈦金級': { bg: '#e0f2fe', color: '#0284c7', border: '#bae6fd' },
    '白銀級': { bg: '#e0f2fe', color: '#0284c7', border: '#bae6fd' },
    '銀級':   { bg: '#dcfce7', color: '#059669', border: '#a7f3d0' },
    '銅級':   { bg: '#fef9c3', color: '#d97706', border: '#fde68a' },
    '花車':   { bg: '#e0f2fe', color: '#0284c7', border: '#bae6fd' },
    '單買':   { bg: '#e0f2fe', color: '#0284c7', border: '#bae6fd' },
    '頭車':   { bg: '#e0f2fe', color: '#0284c7', border: '#bae6fd' },
  }
  const s = map[tier] ?? { bg: '#f1f5f9', color: '#64748b', border: '#e2e8f0' }
  return (
    <span className="inline-block px-2 py-0.5 rounded-full text-xs border" style={{ background: s.bg, color: s.color, borderColor: s.border }}>
      {tier}
    </span>
  )
}

export function SponsorDirectoryPanel() {
  const [data, setData] = useState<AllData | null>(null)
  const [search, setSearch] = useState('')
  const [yearFilter, setYearFilter] = useState('all')
  const [industryFilter, setIndustryFilter] = useState('all')

  useEffect(() => {
    fetch(`${BASE}/data/directory_all.json`)
      .then((r) => r.json())
      .then(setData)
  }, [])

  const allSponsors = useMemo(() => {
    if (!data) return []
    const map = new Map<string, { name: string; industry: string; years: Record<string, Sponsor>; aliases?: string[]; donor_id?: string }>()
    YEARS.forEach((yr) => {
      data[yr]?.forEach((s) => {
        if (!map.has(s.name_canonical)) {
          const ind = normalizeIndustry(s.industry || '')
          map.set(s.name_canonical, { name: s.name_canonical, industry: ind || '—', years: {} })
        }
        map.get(s.name_canonical)!.years[yr] = s
      })
    })
    return [...map.values()].sort((a, b) => a.name.localeCompare(b.name, 'zh-TW'))
  }, [data])

  const industries = useMemo(() => {
    const s = new Set<string>()
    allSponsors.forEach((sp) => { if (sp.industry !== '—') s.add(sp.industry) })
    return ['all', ...Array.from(s).sort()]
  }, [allSponsors])

  const filtered = useMemo(() => {
    const q = search.toLowerCase()
    return allSponsors.filter((sp) => {
      if (q && !sp.name.toLowerCase().includes(q) &&
          !sp.aliases?.some((a: string) => a.toLowerCase().includes(q)) &&
          !sp.donor_id?.toLowerCase().includes(q)) return false
      if (yearFilter !== 'all' && !sp.years[yearFilter]) return false
      if (industryFilter !== 'all' && sp.industry !== industryFilter) return false
      return true
    })
  }, [allSponsors, search, yearFilter, industryFilter])

  if (!data) {
    return <div className="flex items-center justify-center h-64 text-text-muted text-sm">載入中…</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">贊助商名錄</h1>
        <p className="text-sm text-text-muted mt-1">共 222 家廠商（2016–2025 年）。可使用下方篩選框快速查找，或直接按 Ctrl+F 搜尋頁面文字。</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="輸入廠商名稱、別名或 D 編號…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm bg-surface focus:outline-none focus:ring-2 focus:ring-accent/30 w-52"
        />
        <div className="flex gap-1">
          {['all', ...YEARS].map((yr) => (
            <button
              key={yr}
              onClick={() => setYearFilter(yr)}
              className="px-3 py-2 rounded-lg text-sm border transition-colors"
              style={{
                background: yearFilter === yr ? '#7c3aed' : '#ffffff',
                color: yearFilter === yr ? '#ffffff' : '#475569',
                borderColor: yearFilter === yr ? '#7c3aed' : '#e2e8f0',
              }}
            >
              {yr === 'all' ? '全部' : yr}
            </button>
          ))}
        </div>
        <select
          value={industryFilter}
          onChange={(e) => setIndustryFilter(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm bg-surface text-text-secondary focus:outline-none"
        >
          {industries.map((ind) => (
            <option key={ind} value={ind}>{ind === 'all' ? '所有產業' : ind}</option>
          ))}
        </select>
      </div>

      <p className="text-sm text-text-muted">共 {filtered.length} 家廠商</p>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {filtered.map((sp) => (
          <div key={sp.name} className="rounded-xl border border-border bg-surface p-4" style={{ boxShadow: 'var(--shadow-sm)' }}>
            <p className="font-semibold text-foreground text-sm mb-1">{sp.name}</p>
            <p className="text-xs text-text-muted mb-3">{sp.industry}</p>
            <div className="space-y-1">
              {YEARS.filter((yr) => sp.years[yr]).map((yr) => {
                const s = sp.years[yr]
                return (
                  <div key={yr} className="flex items-center justify-between gap-2">
                    <span className="text-xs text-text-muted w-10 shrink-0">{yr}</span>
                    <div className="flex items-center gap-1 flex-1 justify-between">
                      {tierChip(s.tier_orig)}
                      {s.amount ? (
                        <span className="text-xs text-text-muted">NT${(s.amount / 10000).toFixed(0)}萬</span>
                      ) : null}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 text-text-muted">無符合條件的廠商</div>
      )}
    </div>
  )
}
