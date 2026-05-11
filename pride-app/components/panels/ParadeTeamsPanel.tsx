'use client'

import { useEffect, useMemo, useState } from 'react'
import { BASE } from '@/lib/basePath'

type GroupData = Record<string, { 社團車?: string[]; 商業車?: string[]; 隊伍?: string[] }>
type AllGroups = Record<string, GroupData>

type ParadeDetailEntry = { raw_name: string; section: string; team: string }
type Participant = {
  donor_id: string
  name: string
  aliases: string[]
  industry: string
  parade_detail: Record<string, ParadeDetailEntry>
  parade_years: number[]
}

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
  const [participants, setParticipants] = useState<Participant[]>([])
  const [year, setYear] = useState('2023')
  const [type, setType] = useState<'all' | '商業車' | '社團車' | '隊伍'>('all')
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300)
    return () => clearTimeout(t)
  }, [search])

  useEffect(() => {
    fetch(`${BASE}/data/parade_groups.json`)
      .then((r) => r.json())
      .then(setData)
    fetch(`${BASE}/data/parade_participants.json`)
      .then((r) => r.json())
      .then(setParticipants)
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
      return { color, entries }
    }).filter((g) => g.entries.length > 0)
  }, [data, year, type])

  const searchResults = useMemo(() => {
    if (debouncedSearch.trim().length < 2) return []
    const term = debouncedSearch.toLowerCase()
    return participants.filter(
      (p) => p.name.toLowerCase().includes(term) ||
             p.aliases.some((a) => a.toLowerCase().includes(term)) ||
             Object.values(p.parade_detail).some((d) => d.raw_name.toLowerCase().includes(term))
    )
  }, [participants, debouncedSearch])

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

  const isSearching = debouncedSearch.trim().length >= 2

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

      {/* Search + type filter row */}
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="搜尋品牌查看歷年紀錄…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm bg-surface focus:outline-none focus:ring-2 focus:ring-accent/30 w-64"
        />
        {isSearching && (
          <span className="text-xs text-text-muted">共 {searchResults.length} 筆</span>
        )}
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

      {/* Search mode: cross-year brand cards */}
      {isSearching ? (
        <div className="space-y-4">
          {searchResults.length === 0 ? (
            <div className="text-center py-16 text-text-muted">找不到符合「{debouncedSearch}」的紀錄</div>
          ) : (
            searchResults.map((p) => {
              const filteredYears = p.parade_years
                .map(String)
                .filter((yr) => {
                  if (type === 'all') return true
                  return p.parade_detail[yr]?.section === type
                })
              return (
                <div key={p.donor_id} className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
                  {/* Card header */}
                  <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-bg2/40">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-foreground">{p.name}</span>
                      {p.industry && (
                        <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#f1f5f9', color: '#64748b' }}>
                          {p.industry}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-text-muted">
                      共 {p.parade_years.length} 次遊行
                    </span>
                  </div>

                  {/* Year rows */}
                  {p.parade_years.length === 0 ? (
                    <div className="px-4 py-3 text-sm text-text-muted">此廠商無遊行參與紀錄</div>
                  ) : filteredYears.length === 0 ? (
                    <div className="px-4 py-3 text-sm text-text-muted">此廠商在所選類型（{type}）無紀錄</div>
                  ) : (
                    <div className="divide-y divide-border/50">
                      {filteredYears.map((yr) => {
                        const detail = p.parade_detail[yr]
                        const colorKey = detail?.team?.split('大隊')[0] ?? ''
                        const colorStyle = COLOR_STYLES[colorKey]
                        return (
                          <div key={yr} className="flex items-center gap-4 px-4 py-2.5">
                            <span className="text-sm font-medium text-foreground w-10 shrink-0">{yr}</span>
                            <div className="flex items-center gap-1.5 min-w-0 flex-1">
                              {colorStyle && (
                                <span
                                  className="inline-block w-2.5 h-2.5 rounded-full shrink-0"
                                  style={{ background: colorStyle.color }}
                                />
                              )}
                              <span className="text-xs text-text-secondary truncate">
                                {detail?.team ?? '—'}
                              </span>
                            </div>
                            <div className="shrink-0">{typeChip(detail?.section ?? '—')}</div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>
      ) : (
        /* Normal mode: year-based color groups */
        <>
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
        </>
      )}
    </div>
  )
}
