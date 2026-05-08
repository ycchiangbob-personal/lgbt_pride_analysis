'use client'

import { useEffect, useMemo, useState } from 'react'
import { BASE } from '@/lib/basePath'

type ProductItem = { bg?: string; price?: number; unit?: string }
type RetentionItem = { item: string; adopters: number; retention_pct: number; consec: number; total: number; price: number }
type ValueGapItem = { sponsor: string; year: string; actual: number; items: string[]; item_list_cost: number; tier_label: string; tier_price: number; gap: number }
type LoyaltyItem = {
  sponsor: string
  years_count: number
  core_items: string[]
  total_unique: number
  loyalty_score: number
  cat: string[]
}
type ProductAnalysis = {
  prices: Record<string, ProductItem>
  retention: RetentionItem[]
  value_gaps: ValueGapItem[]
  loyalty: LoyaltyItem[]
}

function TierChip({ tier, noSpan }: { tier: string; noSpan?: boolean }) {
  const map: Record<string, [string, string]> = {
    T1: ['#B8860B20', '#B8860B'], T2: ['#E8A60020', '#E8A600'],
    T3: ['#4472C420', '#4472C4'], T4: ['#70AD4720', '#70AD47'],
    T5: ['#ED7D3120', '#ED7D31'],
  }
  const [bg, color] = map[tier] ?? ['#f1f5f920', '#64748b']
  return (
    <span className="inline-block px-2 py-0.5 rounded text-xs font-medium" style={{ background: bg, color }}>
      {tier}
    </span>
  )
}

function SectionCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-surface overflow-hidden" style={{ boxShadow: 'var(--shadow-sm)' }}>
      {children}
    </div>
  )
}

function ActionBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      {children}
    </div>
  )
}

const NEW_PROSPECTS = [
  { name: 'Fubon Financial', category: '金融', appeared: '隊伍 (2019–2024)', priority: 'A' },
  { name: '台灣銀行', category: '金融', appeared: '隊伍', priority: 'A' },
  { name: 'HSBC', category: '金融', appeared: '隊伍 (2020–2025)', priority: 'A' },
  { name: 'BNP Paribas', category: '金融', appeared: '隊伍 (2020–2024)', priority: 'A' },
  { name: 'EY', category: '顧問', appeared: '隊伍 (2019–2022)', priority: 'B' },
  { name: 'Marriott', category: '飯店', appeared: '隊伍 (2022–2024)', priority: 'B' },
  { name: 'P&G', category: '消費品', appeared: '隊伍 (2019–2025)', priority: 'A' },
  { name: 'BMS', category: '醫藥', appeared: '隊伍 (2020–2024)', priority: 'A' },
  { name: 'Mastercard', category: '金融科技', appeared: '全球 Pride', priority: 'B' },
  { name: 'Starbucks', category: '餐飲', appeared: '全球 Pride', priority: 'B' },
]

export function OpportunityPanel() {
  const [analysis, setAnalysis] = useState<ProductAnalysis | null>(null)

  useEffect(() => {
    fetch(`${BASE}/data/product_analysis.json`)
      .then((r) => r.json())
      .then(setAnalysis)
      .catch(() => {})
  }, [])

  const topRetention = useMemo(() => {
    if (!analysis) return []
    return [...(analysis.retention ?? [])]
      .filter((r) => r.adopters >= 3)
      .sort((a, b) => b.retention_pct - a.retention_pct)
      .slice(0, 20)
  }, [analysis])

  const topGaps = useMemo(() => {
    if (!analysis) return []
    return [...(analysis.value_gaps ?? [])]
      .sort((a, b) => b.gap - a.gap)
      .slice(0, 20)
  }, [analysis])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">機會識別與缺口分析</h1>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-xl p-4 text-center" style={{ background: '#f8f5f0' }}>
          <p className="text-xs text-text-muted mb-1">2025 年實際收入</p>
          <p className="text-xl font-extrabold text-foreground">NTD 8.27M</p>
        </div>
        <div className="rounded-xl p-4 text-center" style={{ background: '#e8f5e9' }}>
          <p className="text-xs text-text-muted mb-1">2026 年目標</p>
          <p className="text-xl font-extrabold" style={{ color: '#1B7A3E' }}>NTD 9.50M</p>
        </div>
        <div className="rounded-xl p-4 text-center" style={{ background: '#fdecea' }}>
          <p className="text-xs text-text-muted mb-1">需新增收入</p>
          <p className="text-xl font-extrabold" style={{ color: '#D93025' }}>+NTD 1.23M</p>
        </div>
        <div className="rounded-xl p-4 text-center" style={{ background: '#fff8e1' }}>
          <p className="text-xs text-text-muted mb-1">預期續約基準</p>
          <p className="text-xl font-extrabold" style={{ color: '#B8860B' }}>NTD 4.23M</p>
        </div>
      </div>

      {/* Section A */}
      <SectionCard>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-2">A．現有廠商續約預測</h2>
          <p className="text-sm text-text-muted mb-3">
            依歷史資料，將 2025 年的 59 家廠商分為三類，各類適用不同的續約機率，估算 2026 年可保住的基本收入。
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商類型</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">家數</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">2025 金額</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">續約機率</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">預期保住</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">風險流失</th>
              </tr>
            </thead>
            <tbody>
              {[
                { type: '忠實廠商（連續 3 年以上）', cnt: 21, amt: 'NTD 3.77M', prob: '85%', keep: 'NTD 3.20M', lose: '−NTD 565k（15%）' },
                { type: '回頭廠商（2024 及 2025 皆有）', cnt: 10, amt: 'NTD 995k', prob: '53%', keep: 'NTD 527k', lose: '−NTD 468k（47%）' },
                { type: '新廠商（2025 年首次）', cnt: 28, amt: 'NTD 2.51M', prob: '20%', keep: 'NTD 503k', lose: '−NTD 2.01M（80%）' },
              ].map((r) => (
                <tr key={r.type} className="border-b border-border/50">
                  <td className="px-4 py-2 text-foreground">{r.type}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.cnt}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.amt}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.prob}</td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: '#1B7A3E' }}>{r.keep}</td>
                  <td className="px-3 py-2 text-right" style={{ color: '#D93025' }}>{r.lose}</td>
                </tr>
              ))}
              <tr className="border-t-2 border-border font-bold">
                <td className="px-4 py-2 text-foreground">合計</td>
                <td className="px-3 py-2 text-right">59</td>
                <td className="px-3 py-2 text-right">NTD 7.27M</td>
                <td className="px-3 py-2 text-right">—</td>
                <td className="px-3 py-2 text-right" style={{ color: '#1B7A3E' }}>NTD 4.23M</td>
                <td className="px-3 py-2 text-right" style={{ color: '#D93025' }}>−NTD 3.04M</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-text-muted px-5 py-3 border-t border-border">
          機率來源：忠實廠商參考歷史忠誠度估算（85%）；回頭廠商依 2023→2024 留存率（53%）；新廠商依首年存活率歷史平均（20%）。<br />
          ▸ 預期續約基準 NTD 4.23M，離 9.5M 目標還差 <strong>NTD 5.27M</strong>，需要 B／C／D 三個方向補足。
        </p>
      </SectionCard>

      {/* Section B */}
      <SectionCard>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-2">B．流失廠商挽回（2024 年流失，排除市集／飯店）</h2>
          <p className="text-sm text-text-muted mb-3">
            以下為挽回清單優先分最高的 5 家廠商（排除僅參與一次者）。假設積極主動聯繫有 35% 的挽回成功率，預計可回收 <strong>NTD 335k</strong>。
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商名稱</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">產業</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">最後類型</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">最後金額</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">歷年參與</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: '諾和諾德', ind: '醫藥', tier: 'T4', amt: 'NTD 220,000', yrs: '2 年' },
                { name: '羅氏', ind: '醫藥', tier: 'T4', amt: 'NTD 220,000', yrs: '2 年' },
                { name: '高通', ind: '半導體', tier: 'T4', amt: 'NTD 198,000', yrs: '3 年' },
                { name: '樂天', ind: '電商', tier: 'T4', amt: 'NTD 197,985', yrs: '2 年' },
                { name: '海峰電腦', ind: '電腦', tier: 'T5', amt: 'NTD 120,000', yrs: '2 年' },
              ].map((r, i) => (
                <tr key={r.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground">{r.name}</td>
                  <td className="px-3 py-2 text-xs text-text-muted">{r.ind}</td>
                  <td className="px-3 py-2"><TierChip tier={r.tier} /></td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.amt}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.yrs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-text-muted px-5 py-3 border-t border-border">
          ▸ 完整挽回清單請至「挽回清單」頁籤查看，共追蹤 57 家廠商。
        </p>
      </SectionCard>

      {/* Section C */}
      <SectionCard>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-2">C．現有廠商升級潛力</h2>
          <p className="text-sm text-text-muted mb-3">
            2026 手冊升級價格：白金 100萬 ／ 黃金 70萬 ／ 鈦金 45萬 ／ 銀 22萬 ／ 銅 12萬。以下為忠實或回頭廠商中，升一個級別後潛在增加金額最大的名單。假設 40% 升級成功率，預計可增加 <strong>NTD 639k</strong>。
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商名稱</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">升級路徑</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">現行金額</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">升級後定價</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">可增加</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: '波士頓', from: 'T3', to: 'T2', cur: 'NTD 405,000', next: 'NTD 700,000', add: '+NTD 295,000' },
                { name: '美光', from: 'T3', to: 'T2', cur: 'NTD 405,000', next: 'NTD 700,000', add: '+NTD 295,000' },
                { name: 'Google', from: 'T4', to: 'T3', cur: 'NTD 198,000', next: 'NTD 450,000', add: '+NTD 252,000' },
                { name: 'G-Star', from: 'T4', to: 'T3', cur: 'NTD 198,000', next: 'NTD 450,000', add: '+NTD 252,000' },
                { name: 'Unilever', from: 'T4', to: 'T3', cur: 'NTD 198,000', next: 'NTD 450,000', add: '+NTD 252,000' },
                { name: '台虎', from: 'T4', to: 'T3', cur: 'NTD 198,000', next: 'NTD 450,000', add: '+NTD 252,000' },
              ].map((r, i) => (
                <tr key={r.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground">{r.name}</td>
                  <td className="px-3 py-2">
                    <TierChip tier={r.from} /> → <TierChip tier={r.to} />
                  </td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.cur}</td>
                  <td className="px-3 py-2 text-right text-text-secondary">{r.next}</td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: '#1B7A3E' }}>{r.add}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>

      {/* Section D */}
      <SectionCard>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-2">D．新廠商引入機會</h2>
          <p className="text-sm text-text-muted mb-4">
            以下廠商目前未在我們的贊助名單中，但其母集團已在其他國家參與 Pride 相關贊助，具有較高的接洽成功率。另包含曾有贊助紀錄但已流失、且集團政策支持 DEI 的廠商。
          </p>

          {/* D1 */}
          <p className="font-bold text-sm mb-2">▸ 曾有合作紀錄、集團支持 DEI（優先重啟）</p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">最後參與</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">遊行參與紀錄</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">集團/母公司</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">集團 Pride 參與證據</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">建議切入點</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: '諾和諾德', last: '2024', parade: '3 次', paradeNote: '2022 隊伍 → 2023–2024 花車', group: 'Novo Nordisk（丹麥）', evidence: '贊助哥本哈根、紐約、倫敦同志遊行；年報揭露 LGBT+ 員工資源群組', tip: '引用全球集團政策，以永續報告框架切入' },
                { name: '羅氏', last: '2024', parade: '4 次', paradeNote: '2022 隊伍 → 2023 花車+隊伍 → 2024 花車', group: 'Roche（瑞士）', evidence: '贊助舊金山、蘇黎世同志遊行；設有彩虹員工網絡', tip: '聯繫台灣人資或多元共融負責人，以員工活動角度提案' },
                { name: 'GU', last: '2022', parade: '1 次', paradeNote: '2024 花車', group: '迅銷集團（日本）', evidence: 'UT 系列聯名國際 LGBT+ 聯盟；多年贊助東京同志遊行', tip: '強調台灣遊行是東亞規模最大，對標東京同志遊行' },
                { name: 'Diageo 台灣', last: '2023', parade: '無紀錄', paradeNote: '', group: 'Diageo（英國）', evidence: 'Johnnie Walker 彩虹版；贊助全球 30+ Pride 城市', tip: 'Johnnie Walker 已在台參與，可提案擴大集團層級' },
                { name: '雅詩蘭黛', last: '2023', parade: '1 次', paradeNote: '旗下 M.A.C 台灣 2019 隊伍', group: 'Estée Lauder（美國）', evidence: 'MAC Viva Glam 公益捐款；多年 LGBT+ 平權專案', tip: '強調台灣是亞洲同志遊行最受國際關注的場域' },
                { name: '渣打銀行', last: '2022', parade: '1 次', paradeNote: '2024 花車', group: 'Standard Chartered（英國）', evidence: '贊助新加坡粉點（Pink Dot）；全球驕傲月品牌活動', tip: '以金融業永續評分框架切入，強調社會面揭露' },
                { name: '必勝客', last: '2025 銀', parade: '3 次', paradeNote: '2023 花車 → 2025 花車+隊伍', group: 'Yum! Brands（美國）', evidence: 'Taco Bell 多年 Pride 合作；Yum! 全球 DEI 承諾', tip: '2025 已是銀級，洽談升鈦金' },
              ].map((r, i) => (
                <tr key={r.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground whitespace-nowrap">{r.name}</td>
                  <td className="px-3 py-2 text-text-secondary whitespace-nowrap">{r.last}</td>
                  <td className="px-3 py-2 text-xs">
                    <span style={{ color: r.parade === '無紀錄' ? '#94a3b8' : r.parade === '1 次' ? '#888' : '#1B7A3E', fontWeight: 600 }}>{r.parade}</span>
                    {r.paradeNote && <><br /><span className="text-text-muted">{r.paradeNote}</span></>}
                  </td>
                  <td className="px-3 py-2 text-xs text-text-secondary">{r.group}</td>
                  <td className="px-3 py-2 text-xs text-text-muted">{r.evidence}</td>
                  <td className="px-3 py-2 text-xs text-text-muted">{r.tip}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* D2 */}
        <div className="px-5 pt-4 pb-2">
          <p className="font-bold text-sm mb-2">▸ 從未合作、集團已在海外贊助 Pride（潛在新客）</p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">產業</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">遊行參與紀錄</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">集團 Pride 參與</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">建議切入</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">優先級</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: '微軟台灣', ind: '科技', parade: '6 次', paradeNote: '2019–2025 隊伍（每年）', evidence: '全球同志遊行活動、LGBT+ 員工資源群組、官方聲明', tip: '強調 ESG S 指標、人才吸引', pri: '最高', priColor: '#D93025' },
                { name: '蘋果台灣', ind: '科技', parade: '無紀錄', paradeNote: '', evidence: '舊金山 Pride 遊行領頭企業；全球員工 Pride 活動', tip: '台灣是蘋果亞太重點市場', pri: '最高', priColor: '#D93025' },
                { name: 'IKEA 台灣', ind: '零售', parade: '無紀錄', paradeNote: '', evidence: 'IKEA 全球每年推出彩虹聯名商品；贊助歐洲 Pride', tip: '聯名商品授權合作切入', pri: '最高', priColor: '#D93025' },
                { name: '萬事達卡', ind: '金融', parade: '無紀錄', paradeNote: '', evidence: '全球 Pride 主要贊助商；彩虹卡設計', tip: '以品牌曝光與 ESG 評分雙角度提案', pri: '高', priColor: '#F6B93B' },
                { name: 'Gap 台灣', ind: '服飾', parade: '5 次', paradeNote: '2019–2025 花車；2019、2025 兼參隊伍', evidence: 'Gap Inc. 全球 Pride 系列；舊金山 Pride 長期贊助商', tip: '曾多次購買花車，可提案升級至銀級', pri: '高', priColor: '#F6B93B' },
                { name: '漢堡王台灣', ind: '餐飲', parade: '無紀錄', paradeNote: '', evidence: '漢堡王彩虹堡活動；百勝餐飲全球多元共融承諾', tip: '餐飲品牌現場行銷角度切入', pri: '中', priColor: '#888' },
                { name: 'H&M 台灣', ind: '服飾', parade: '無紀錄', paradeNote: '', evidence: 'H&M 全球彩虹系列；贊助斯德哥爾摩 Pride', tip: '聯名商品 + 現場品牌曝光', pri: '中', priColor: '#888' },
                { name: '摩根大通 JPMorgan', ind: '金融', parade: '1 次', paradeNote: '2019 隊伍', evidence: '紐約 Pride 主贊助商多年；全球 PRIDE Network 員工群組；年度 LGBT+ 平等指數滿分', tip: '以美系金融機構台灣市場旗艦地位切入；2019 參與後未再出現，可提案重返並升級為正式贊助商', pri: '高', priColor: '#F6B93B' },
                { name: 'Visa', ind: '金融科技', parade: '無紀錄', paradeNote: '', evidence: 'Visa 為全球 Pride 官方金融合作夥伴；WorldPride 主要贊助商；彩虹限定卡面設計', tip: '以數位支付品牌 + 遊行現場無現金支付體驗合作切入；台灣電支市場成長快，符合品牌在地布局目標', pri: '高', priColor: '#F6B93B' },
                { name: 'Salesforce', ind: '科技/SaaS', parade: '無紀錄', paradeNote: '', evidence: 'Salesforce 設有 Equality ERG；主辦 Dreamforce Pride 大型活動；全球 DEI 報告公開承諾', tip: '台灣 Salesforce 企業客戶社群成長中，以企業客戶活動切入附帶品牌曝光；強調平等文化是 Salesforce 核心價值', pri: '高', priColor: '#F6B93B' },
                { name: 'KPMG 安侯建業', ind: '顧問/審計', parade: '無紀錄', paradeNote: '', evidence: 'KPMG 全球 OUT Network 員工群組；贊助 WorldPride Sydney 2023、澳洲 Mardi Gras', tip: '四大中唯一尚未現身台灣遊行者，可對比 EY/Deloitte 已多次出現作說服素材；以 ESG 顧問定位切入', pri: '高', priColor: '#F6B93B' },
                { name: "Levi's 台灣", ind: '服飾', parade: '無紀錄', paradeNote: '', evidence: "Levi's 為舊金山 Pride 多年官方合作夥伴；全球彩虹限定系列；品牌歷史上長期支持 LGBTQ+ 平權", tip: '服飾品牌在遊行現場極具品牌能見度；提案聯名限定款 + 商業花車，切入年輕消費族群', pri: '中', priColor: '#888' },
                { name: 'Booking.com 台灣', ind: '旅遊科技', parade: '無紀錄', paradeNote: '', evidence: 'Booking.com 設有同志友善住宿認可標章；贊助阿姆斯特丹 Pride；全球 LGBTQ+ 旅遊市場布局', tip: '以「台灣是亞洲 LGBTQ+ 友善旅遊首選目的地」主題合作切入；提案遊行周邊住宿推薦廣宣聯名', pri: '中', priColor: '#888' },
              ].map((r, i) => (
                <tr key={r.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground whitespace-nowrap">{r.name}</td>
                  <td className="px-3 py-2 text-xs text-text-secondary whitespace-nowrap">{r.ind}</td>
                  <td className="px-3 py-2 text-xs">
                    <span style={{ color: r.parade === '無紀錄' ? '#94a3b8' : r.parade.includes('6') || r.parade.includes('5') ? '#1B7A3E' : '#F6B93B', fontWeight: 600 }}>{r.parade}</span>
                    {r.paradeNote && <><br /><span className="text-text-muted">{r.paradeNote}</span></>}
                  </td>
                  <td className="px-3 py-2 text-xs text-text-muted">{r.evidence}</td>
                  <td className="px-3 py-2 text-xs text-text-muted">{r.tip}</td>
                  <td className="px-3 py-2 text-xs font-bold whitespace-nowrap" style={{ color: r.priColor }}>{r.pri}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* D3 */}
        <div className="px-5 pt-4 pb-2">
          <p className="font-bold text-sm mb-1">▸ 遊行常客、尚無贊助紀錄（高轉換潛力）</p>
          <p className="text-sm text-text-muted mb-2">以下廠商每年以隊伍身份參與遊行，但從未在贊助名單中。遊行歷史顯示品牌已對活動有高度認同，為最直接的開發切入點。</p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">廠商</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">產業</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">遊行參與紀錄</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">集團 Pride 背景</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">建議切入</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">優先級</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Goldman Sachs', ind: '金融', parade: '5 次', note: '2019、2022–2025 隊伍', bg: '全球設有 LGBTQ+ Alliance 員工資源群組；贊助紐約 Pride', tip: '以 ESG 社會面指標、雇主品牌切入，強調 S 評分加分效益', pri: '最高', pc: '#D93025' },
                { name: 'Dell Technologies', ind: '科技', parade: '5 次', note: '2019、2022–2025 隊伍', bg: 'Dell Pride ERG 全球活躍；贊助多個國際 Pride', tip: '以員工 ERG 轉化為對外贊助，強調品牌在台灣科技人才市場的能見度', pri: '最高', pc: '#D93025' },
                { name: '台灣華特迪士尼', ind: '娛樂', parade: '3 次', note: '2022、2024–2025 隊伍', bg: 'Disney 全球 Pride 商品系列；各地主題樂園驕傲月活動', tip: '以 IP 聯名、現場品牌曝光切入；強調台灣遊行媒體能見度', pri: '高', pc: '#F6B93B' },
                { name: 'Activision Blizzard', ind: '遊戲', parade: '3 次', note: '2023–2025 隊伍（連三年）', bg: '已為 Microsoft 旗下；Overwatch、暗黑系列設有 Pride 特別活動', tip: '透過 Microsoft 台灣聯繫，可跨品牌合作或由 ABK 獨立提案', pri: '高', pc: '#F6B93B' },
                { name: 'Tesla Taiwan', ind: '科技', parade: '4 次', note: '2019–2023 隊伍（近二年未出現）', bg: 'ERG 仍積極；企業整體立場近年趨於保守', tip: '以 ERG 員工活動角度切入，避免品牌層級提案；評估內部支持度', pri: '中', pc: '#888' },
                { name: 'BMS 必治妥施貴寶', ind: '製藥', parade: '5 次', note: '2020–2024 隊伍（連五年）', bg: '全球設有 OUT & Allies 員工資源群組；贊助費城 Pride、紐約 Pride；多年 HIV/LGBTQ+ 公益投入', tip: '製藥業 Pride 贊助已是產業標配；以 ESG 社會面評分、台灣醫療人才招募切入，強調在地 DEI 宣示', pri: '最高', pc: '#D93025' },
                { name: '寶僑家品 P&G', ind: '消費品', parade: '6 次', note: '2019、2020、2022–2025 隊伍', bg: 'P&G 為舊金山 Pride 、WorldPride 主贊助商；旗下品牌（Pantene、Always）長年推出 Pride 限定廣告', tip: '台灣市場曝光轉化：從遊行隊伍升級為活動贊助商；可提案花車首位或銀級，擴大在地品牌影響力', pri: '最高', pc: '#D93025' },
                { name: 'HSBC 匯豐銀行', ind: '金融', parade: '5 次', note: '2020、2022–2025 隊伍', bg: '贊助香港 Pink Dot（2024 前）、倫敦 Pride；全球 Rainbow Network 員工群組；永續金融框架公開承諾', tip: '以銀行業永續金融 ESG 評分切入，強調台灣金融市場 S 評分加分；可比照渣打銀行已購花車的路徑提案', pri: '最高', pc: '#D93025' },
                { name: 'EY 安永', ind: '顧問/審計', parade: '4 次', note: '2019、2023–2025 隊伍', bg: 'EY Global 設有 Unity 員工網絡；贊助英國 Pride in London；全球 DEI 年度報告公開承諾', tip: '四大中台灣遊行出現最頻繁者，以 ESG 顧問業務定位、雇主品牌雙角度提案；可與 Deloitte 競爭策略比較作說服素材', pri: '高', pc: '#F6B93B' },
                { name: 'BNP Paribas 法巴', ind: '金融', parade: '4 次', note: '2019、2020、2022、2023 隊伍', bg: 'BNP 贊助巴黎 Pride、倫敦 Pride；全球 Prism 員工網絡；與法國工商會聯合參與遊行多次', tip: '以 ESG 社會面揭露、對外品牌宣示切入，訴諸高端金融客群；透過法國工商會台灣分會建立接觸管道', pri: '高', pc: '#F6B93B' },
                { name: '勤業眾信 Deloitte', ind: '顧問/審計', parade: '3 次', note: '2019、2021、2024 隊伍', bg: 'Deloitte 全球 GLOBE 員工網絡；贊助美國、澳洲多個 Pride 活動；DEI 年報公開揭露', tip: '四大之一，以 ESG 顧問業務、雇主品牌雙角度提案；2021 COVID 年仍出現，顯示內部支持穩固', pri: '高', pc: '#F6B93B' },
                { name: '施羅德 Schroders', ind: '金融', parade: '3 次', note: '2022、2023、2025 隊伍', bg: 'Schroders 贊助倫敦 Pride；設有 Pride at Schroders 員工網絡；ESG 投資策略公開承諾', tip: '資產管理業者，以 ESG 投資承諾、對內外雙重品牌效益切入；可強調台灣責任投資市場的能見度', pri: '高', pc: '#F6B93B' },
                { name: '羅技 Logitech', ind: '科技', parade: '3 次', note: '2022–2024 隊伍（連三年）', bg: 'Logitech 發行彩虹版週邊產品（鍵盤、滑鼠）；全球 Pride 月品牌活動；台灣總部設在新北', tip: '以遊行現場品牌展示（彩虹限定產品試用站）作為低門檻切入，搭配花車或攤位合作提案', pri: '高', pc: '#F6B93B' },
                { name: 'LVMH 集團', ind: '精品零售', parade: '3 次', note: '2022–2024 隊伍', bg: 'LVMH/Louis Vuitton 贊助巴黎 Pride；集團 DEI 承諾報告；旗下品牌多有 Pride 限定系列', tip: '精品客群與 LGBTQ+ 社群高度重疊；強調台灣遊行媒體能見度及品牌形象投資；可由集團台灣代理洽談', pri: '中', pc: '#888' },
                { name: 'Expedia Group', ind: '旅遊科技', parade: '3 次', note: '2019、2020、2023 隊伍', bg: 'Expedia 設有 PRIDE 員工群組；贊助多個城市 Pride；推出同志友善旅遊專頁', tip: '以「同志友善旅遊」定位切入，提案遊行現場品牌曝光與官網聯名廣宣；強調台灣是 LGBTQ+ 旅遊熱門目的地', pri: '中', pc: '#888' },
                { name: '台灣萊雅 L\'Oréal', ind: '美妝消費品', parade: '2 次', note: '2023、2025 隊伍', bg: 'L\'Oréal Paris 全球 Stand Up 反霸凌活動；贊助巴黎 Pride；旗下品牌 NYX、Lancôme 有 Pride 聯名', tip: '美妝品牌與 LGBTQ+ 社群高親和力；提案聯名限定商品 + 遊行現場彩妝體驗站，低門檻高曝光', pri: '高', pc: '#F6B93B' },
                { name: 'Morgan Stanley 台灣', ind: '金融', parade: '2 次', note: '2023、2024 隊伍', bg: 'Morgan Stanley 設有 LGBTQ+ Diversity Network；贊助紐約 Pride；全球 ERG 積極', tip: '以投資銀行業雇主品牌、ESG 社會評分加分切入；可比照同業 Goldman Sachs 已多年參與卻未贊助的模式提案', pri: '高', pc: '#F6B93B' },
                { name: '台灣英特爾 Intel', ind: '半導體', parade: '2 次', note: '2023、2025 隊伍', bg: 'Intel 設有 GAAD（Gay, Allies & Allies for Diversity）員工群組；贊助多個美國 Pride；全球 DEI 報告揭露', tip: '半導體業在台曝光，以供應鏈多元共融承諾、台灣 STEM 人才吸引作為主軸；可搭配花車合作提案', pri: '中', pc: '#888' },
                { name: 'VF Taiwan 台灣威富', ind: '服飾戶外', parade: '2 次', note: '2024、2025 隊伍', bg: 'The North Face 全球 Pride 聯名系列；Timberland Pride 企業承諾；VF Corp DEI 年報公開', tip: '以戶外品牌愛護台灣 LGBTQ+ 社群、永續環境雙主軸切入；可提案 TNF 或 Timberland 旗下品牌聯名', pri: '中', pc: '#888' },
                { name: 'Amazon 台灣', ind: '科技/電商', parade: '2 次', note: '2023、2024 隊伍', bg: 'Amazon 設有 Glamazon LGBTQ+ ERG；贊助西雅圖 Pride；AWS 及 Prime Video 均有 Pride 月活動', tip: '以 AWS 台灣業務、雇主品牌切入；可從 AWS 企業客戶活動切入附帶品牌曝光，強調台灣雲端市場布局', pri: '高', pc: '#F6B93B' },
                { name: '保樂力加 Pernod Ricard', ind: '酒類飲料', parade: '2 次', note: '2023、2025 隊伍', bg: '旗下 Absolut Vodka 為全球最長期 Pride 贊助商之一（40+ 年）；Chivas、Ballantine\'s 全球 Pride 活動', tip: 'Absolut Pride 品牌基因極強，台灣酒類廣宣限制下以遊行現場品牌曝光（非廣播）切入；花車提案最適合', pri: '高', pc: '#F6B93B' },
              ].map((r, i) => (
                <tr key={r.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-2 font-medium text-foreground whitespace-nowrap">{r.name}</td>
                  <td className="px-3 py-2 text-xs text-text-secondary whitespace-nowrap">{r.ind}</td>
                  <td className="px-3 py-2 text-xs">
                    <span style={{ color: r.parade.includes('6') || r.parade.includes('5') ? '#1B7A3E' : '#F6B93B', fontWeight: 600 }}>{r.parade}</span>
                    <br /><span className="text-text-muted">{r.note}</span>
                  </td>
                  <td className="px-3 py-2 text-xs text-text-muted">{r.bg}</td>
                  <td className="px-3 py-2 text-xs text-text-muted">{r.tip}</td>
                  <td className="px-3 py-2 text-xs font-bold whitespace-nowrap" style={{ color: r.pc }}>{r.pri}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>

      {/* Gap summary */}
      <SectionCard>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-3">缺口填補總覽</h2>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-2 text-text-muted font-medium">來源</th>
                <th className="text-right px-3 py-2 text-text-muted font-medium">預估可增加</th>
                <th className="text-left px-3 py-2 text-text-muted font-medium">說明</th>
              </tr>
            </thead>
            <tbody>
              {[
                { src: 'A. 續約基準', amt: 'NTD 4.23M', note: '歷史留存率估算', bold: false },
                { src: 'B. 流失廠商挽回（前 5 名 × 35%）', amt: '+NTD 335k', note: '主動外展，可調整挽回家數', bold: false },
                { src: 'C. 現有廠商升級（前 6 名 × 40%）', amt: '+NTD 639k', note: '提案升一個級別', bold: false },
                { src: 'D. 新廠商引入（2 家 銀級估算）', amt: '+NTD 440k', note: '全新合作廠商', bold: false },
              ].map((r, i) => (
                <tr key={r.src} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-2 text-foreground">{r.src}</td>
                  <td className="px-3 py-2 text-right font-bold" style={{ color: '#1B7A3E' }}>{r.amt}</td>
                  <td className="px-3 py-2 text-text-muted text-xs">{r.note}</td>
                </tr>
              ))}
              <tr className="border-t-2 border-border font-bold">
                <td className="px-4 py-2 text-foreground">合計預測</td>
                <td className="px-3 py-2 text-right font-extrabold" style={{ color: '#D93025' }}>NTD 5.64M</td>
                <td className="px-3 py-2 text-text-muted text-xs">距目標 3.86M</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-text-muted px-5 py-3 border-t border-border">
          距目標仍差 NTD 3.86M，須透過更多新廠商或更積極的挽回補足。
        </p>
      </SectionCard>

      {/* Action box */}
      <ActionBox>
        🎯 <strong>行動建議：</strong>優先確保 21 家忠實廠商全數續約（保住 3.2M 基礎），再集中火力聯繫前 5 名流失廠商（預計回收 335k）；同步向有升級空間的廠商提出鈦金／銀級方案。若全部達成，加上引入 2 家新廠商，可達到 <strong>NTD 5.64M</strong>。
      </ActionBox>

      {/* E. 新潛力廠商 */}
      <SectionCard>
        <div className="px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold text-foreground mb-1">E．新潛力廠商（遊行隊伍轉化）</h2>
          <p className="text-sm text-text-muted mb-3">
            以下廠商曾以「隊伍」或「全球 Pride」形式參與，尚無商業贊助紀錄，為 2026 年 BD 開發優先目標。
          </p>
        </div>
        <div className="overflow-x-auto border-t border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-bg2 border-b border-border">
                <th className="text-left px-4 py-3 text-text-muted font-medium">廠商</th>
                <th className="text-left px-4 py-3 text-text-muted font-medium">產業</th>
                <th className="text-left px-4 py-3 text-text-muted font-medium">曾出現方式</th>
                <th className="text-center px-4 py-3 text-text-muted font-medium">優先</th>
              </tr>
            </thead>
            <tbody>
              {NEW_PROSPECTS.map((p, i) => (
                <tr key={p.name} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                  <td className="px-4 py-3 font-medium text-foreground">{p.name}</td>
                  <td className="px-4 py-3 text-text-secondary text-xs">{p.category}</td>
                  <td className="px-4 py-3 text-text-muted text-xs">{p.appeared}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className="inline-flex w-6 h-6 rounded-full text-xs font-bold items-center justify-center"
                      style={p.priority === 'A'
                        ? { background: '#fff0f6', color: '#e8005a' }
                        : { background: '#f1f5f9', color: '#64748b' }}
                    >
                      {p.priority}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>

      {/* F. 品項留存率 */}
      {!analysis ? (
        <div className="flex items-center justify-center h-24 text-text-muted text-sm">載入中…</div>
      ) : (
        <>
          <SectionCard>
            <div className="px-5 pt-4 pb-2">
              <h2 className="text-base font-semibold text-foreground mb-1">F．品項留存率分析</h2>
              <p className="text-sm text-text-muted mb-2">品項採用數 ≥ 3 家，依留存率排序（共 {topRetention.length} 個品項）</p>
            </div>
            <div className="overflow-x-auto border-t border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-bg2">
                    <th className="text-left px-4 py-2 text-text-muted font-medium">品項</th>
                    <th className="text-right px-4 py-2 text-text-muted font-medium">採用廠商</th>
                    <th className="text-right px-4 py-2 text-text-muted font-medium">留存率</th>
                    <th className="text-right px-4 py-2 text-text-muted font-medium">連續採用</th>
                    <th className="text-right px-4 py-2 text-text-muted font-medium">定價</th>
                  </tr>
                </thead>
                <tbody>
                  {topRetention.map((r, i) => (
                    <tr key={r.item} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                      <td className="px-4 py-2 text-foreground">{r.item}</td>
                      <td className="px-4 py-2 text-right text-text-secondary">{r.adopters}</td>
                      <td className="px-4 py-2 text-right font-medium" style={{ color: r.retention_pct >= 50 ? '#059669' : r.retention_pct >= 30 ? '#d97706' : '#e8005a' }}>
                        {r.retention_pct}%
                      </td>
                      <td className="px-4 py-2 text-right text-text-secondary">{r.consec}</td>
                      <td className="px-4 py-2 text-right text-text-muted text-xs">
                        {r.price ? `NT$${r.price.toLocaleString()}` : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>

          {/* G. 價值落差 */}
          <SectionCard>
            <div className="px-5 pt-4 pb-2">
              <h2 className="text-base font-semibold text-foreground mb-1">G．贊助金額 vs 品項定價落差</h2>
              <p className="text-sm text-text-muted mb-2">廠商實際付款 vs 品項清單總價差（正數 = 付超過品項定價合計）</p>
            </div>
            <div className="overflow-x-auto border-t border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-bg2">
                    <th className="text-left px-4 py-2 text-text-muted font-medium">廠商</th>
                    <th className="text-center px-3 py-2 text-text-muted font-medium">年份</th>
                    <th className="text-left px-3 py-2 text-text-muted font-medium">級別</th>
                    <th className="text-right px-4 py-2 text-text-muted font-medium">實付</th>
                    <th className="text-right px-4 py-2 text-text-muted font-medium">品項合計</th>
                    <th className="text-right px-4 py-2 text-text-muted font-medium">差額</th>
                  </tr>
                </thead>
                <tbody>
                  {topGaps.map((r, i) => (
                    <tr key={`${r.sponsor}-${r.year}`} className={`border-b border-border/50 ${i % 2 === 1 ? 'bg-bg2/30' : ''}`}>
                      <td className="px-4 py-2 text-foreground font-medium">{r.sponsor}</td>
                      <td className="px-3 py-2 text-center text-text-muted text-xs">{r.year}</td>
                      <td className="px-3 py-2 text-xs text-text-secondary">{r.tier_label}</td>
                      <td className="px-4 py-2 text-right text-text-secondary">NT${r.actual.toLocaleString()}</td>
                      <td className="px-4 py-2 text-right text-text-secondary">NT${r.item_list_cost.toLocaleString()}</td>
                      <td className="px-4 py-2 text-right font-semibold" style={{ color: r.gap > 0 ? '#059669' : '#e8005a' }}>
                        {r.gap > 0 ? '+' : ''}NT${r.gap.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>

          {/* H. 廠商忠誠度 */}
          <SectionCard>
            <div className="px-5 pt-4 pb-3 border-b border-border">
              <h2 className="text-base font-semibold text-foreground mb-1">H．廠商忠誠度分析</h2>
              <p className="text-sm text-text-muted">依忠誠度分數排序的前 20 家廠商，列出他們長期穩定採用的核心品項。</p>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(analysis.loyalty ?? []).slice(0, 20).map((item) => (
                  <div key={item.sponsor} className="rounded-lg border border-border p-3" style={{ background: '#fafafa' }}>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-medium text-foreground text-sm">{item.sponsor}</p>
                        <p className="text-xs text-text-muted mt-0.5">{item.years_count} 年連續 · 忠誠度 {item.loyalty_score}</p>
                      </div>
                      <span className="text-xs text-text-muted whitespace-nowrap">{item.core_items?.length ?? 0} 項核心品項</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {(item.core_items ?? []).map((it) => (
                        <span key={it} className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#f3e8ff', color: '#7c3aed', border: '1px solid #e9d5ff' }}>
                          {it}
                        </span>
                      ))}
                      {(!item.core_items || item.core_items.length === 0) && (
                        <span className="text-xs text-text-muted">尚無穩定核心品項</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </SectionCard>
        </>
      )}
    </div>
  )
}
