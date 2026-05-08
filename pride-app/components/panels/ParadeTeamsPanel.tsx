'use client'

import { useEffect, useMemo, useState } from 'react'

type GroupData = Record<string, { 社團車?: string[]; 商業車?: string[]; 隊伍?: string[] }>
type AllGroups = Record<string, GroupData>

const COLORS = ['紅色', '橙色', '黃色', '綠色', '藍色', '紫色']
const COLOR_STYLES: Record<string, { bg: string; color: string }> = {
  紅色: { bg: '#fff0f2', color: '#be185d' },
  橙色: { bg: '#fff7ed', color: '#c2410c' },
  黃色: { bg: '#fefce8', color: '#a16207' },
  綠色: { bg: '#f0fdf4', color: '#15803d' },
  藍色: { bg: '#eff6ff', color: '#1d4ed8' },
  紫色: { bg: '#faf5ff', color: '#7e22ce' },
}

export function ParadeTeamsPanel() {
  const [data, setData] = useState<AllGroups | null>(null)
  const [year, setYear] = useState('2023')
  const [type, setType] = useState<'all' | '商業車' | '社團車' | '隊伍'>('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetch('/data/parade_groups.json')
      .then((r) => r.json())
      .then(setData)
  }, [])

  const years = useMemo(() => (data ? Object.keys(data).sort() : []), [data])

  const groups = useMemo(() => {
    if (!data?.[year]) return []
    const yearData = data[year]
    return COLORS.filter((c) => yearData[c]).map((color) => {
      const grp = yearData[color]
      const entries: Array<{ name: string; type: '商業車' | '社團車' | '隊伍' }> = []
      if (type === 'all' || type === '商業車') grp?.['商業車']?.forEach((n) => entries.push({ name: n, type: '商業車' }))
      if (type === 'all' || type === '社團車') grp?.['社團車']?.forEach((n) => entries.push({ name: n, type: '社團車' }))
      if (type === 'all' || type === '隊伍')   grp?.['隊伍']?.forEach((n) => entries.push({ name: n, type: '隊伍' }))
      const filtered = search
        ? entries.filter((e) => e.name.toLowerCase().includes(search.toLowerCase()))
        : entries
      return { color, entries: filtered }
    }).filter((g) => g.entries.length > 0)
  }, [data, year, type, search])

  const typeChip = (t: string) => {
    const s = t === '商業車'
      ? { bg: '#e0f2fe', color: '#0284c7' }
      : t === '社團車'
      ? { bg: '#f3e8ff', color: '#7c3aed' }
      : { bg: '#f0fdf4', color: '#15803d' }
    return (
      <span className="inline-block px-1.5 py-0.5 rounded text-xs" style={{ background: s.bg, color: s.color }}>
        {t}
      </span>
    )
  }

  if (!data) {
    return <div className="flex items-center justify-center h-64 text-text-muted text-sm">載入中…</div>
  }

  const totalByCat = (cat: '商業車' | '社團車' | '隊伍') => {
    if (!data?.[year]) return 0
    return COLORS.reduce((s, c) => s + (data[year][c]?.[cat]?.length ?? 0), 0)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">遊行隊伍</h1>
        <p className="text-sm text-text-muted mt-1">共 228 筆紀錄。遊行年份欄依大隊顏色標示（紅/橙/黃/綠/藍/紫），深色格為商業贊助年份。資料來源：2019–2025 遊行參與團體名單 × 贊助商名錄。</p>
      </div>

      {/* Year selector */}
      <div className="flex gap-2 flex-wrap">
        {years.map((yr) => (
          <button
            key={yr}
            onClick={() => setYear(yr)}
            className="px-4 py-2 rounded-lg text-sm border transition-colors"
            style={{
              background: year === yr ? '#e8005a' : '#ffffff',
              color: year === yr ? '#ffffff' : '#475569',
              borderColor: year === yr ? '#e8005a' : '#e2e8f0',
            }}
          >
            {yr}
          </button>
        ))}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {(['商業車', '社團車', '隊伍'] as const).map((cat) => {
          const s = cat === '商業車'
            ? { color: '#0284c7', bg: '#e0f2fe' }
            : cat === '社團車'
            ? { color: '#7c3aed', bg: '#f3e8ff' }
            : { color: '#059669', bg: '#dcfce7' }
          return (
            <div key={cat} className="rounded-xl border border-border bg-surface p-4" style={{ boxShadow: 'var(--shadow-sm)' }}>
              <p className="text-xs text-text-muted mb-1">{cat}</p>
              <p className="text-2xl font-bold" style={{ color: s.color }}>{totalByCat(cat)}</p>
            </div>
          )
        })}
      </div>

      {/* Search */}
      <input
        type="text"
        placeholder="搜尋隊伍名稱…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="border border-border rounded-lg px-3 py-2 text-sm bg-surface focus:outline-none focus:ring-2 focus:ring-accent/30 w-52"
      />

      {/* Type filter */}
      <div className="flex gap-2">
        {(['all', '商業車', '社團車', '隊伍'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setType(t)}
            className="px-3 py-2 rounded-lg text-sm border transition-colors"
            style={{
              background: type === t ? '#475569' : '#ffffff',
              color: type === t ? '#ffffff' : '#475569',
              borderColor: type === t ? '#475569' : '#e2e8f0',
            }}
          >
            {t === 'all' ? '全部' : t}
          </button>
        ))}
      </div>

      {/* Groups by color */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {groups.map(({ color, entries }) => {
          const s = COLOR_STYLES[color] ?? { bg: '#f8fafc', color: '#475569' }
          return (
            <div key={color} className="rounded-xl border bg-surface p-4 overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)', borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-2 mb-3">
                <span className="inline-block w-3 h-3 rounded-full" style={{ background: s.color }} />
                <h3 className="font-semibold text-sm" style={{ color: s.color }}>{color}區</h3>
                <span className="ml-auto text-xs text-text-muted">{entries.length} 隊</span>
              </div>
              <div className="space-y-1 max-h-52 overflow-y-auto">
                {entries.map((e, i) => (
                  <div key={`${e.name}-${i}`} className="flex items-center justify-between gap-2 py-0.5">
                    <span className="text-xs text-foreground truncate">{e.name}</span>
                    {typeChip(e.type)}
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {groups.length === 0 && (
        <div className="text-center py-16 text-text-muted">無資料</div>
      )}
    </div>
  )
}
