'use client'

import Image from 'next/image'
import Link from 'next/link'
import { BASE } from '@/lib/basePath'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Star,
  TrendingUp,
  RotateCcw,
  ShoppingCart,
  Sparkles,
  Target,
  BookOpen,
  Flag,
} from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

const NAV_ITEMS = [
  { label: '總覽',       href: '/',            icon: LayoutDashboard, color: '#E53E3E' },
  { label: '忠實贊助商', href: '/loyalist',    icon: Star,            color: '#ED8936' },
  { label: '留存率',     href: '/retention',   icon: TrendingUp,      color: '#D69E2E' },
  { label: '挽回清單',   href: '/winback',     icon: RotateCcw,       color: '#38A169' },
  { label: '採購行為',   href: '/purchase',    icon: ShoppingCart,    color: '#319795' },
  { label: '新品牌續約率', href: '/new-brand', icon: Sparkles,        color: '#3182CE' },
  { label: '機會識別',   href: '/opportunity', icon: Target,          color: '#5A67D8' },
  { label: '贊助商名錄', href: '/directory',   icon: BookOpen,        color: '#805AD5' },
  { label: '遊行隊伍',   href: '/parade',      icon: Flag,            color: '#D53F8C' },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-border px-4 py-4">
        <div className="flex flex-col gap-1">
          <Image
            src={`${BASE}/logo-light.png`}
            alt="臺灣同志遊行"
            width={160}
            height={60}
            className="object-contain"
            priority
          />
          <p className="text-xs text-text-muted mt-1">商業贊助分析報告</p>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV_ITEMS.map((item) => {
                const isActive =
                  item.href === '/'
                    ? pathname === '/'
                    : pathname.startsWith(item.href)
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton asChild isActive={isActive}>
                      <Link
                        href={item.href}
                        className="group flex items-center gap-2"
                        style={{ '--item-color': item.color } as React.CSSProperties}
                      >
                        <item.icon className="h-4 w-4 shrink-0 transition-colors duration-150 group-hover:text-[var(--item-color)]" />
                        <span>{item.label}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-border px-4 py-3">
        <p className="text-xs text-text-muted">
          2016–2025 · 第 14–23 屆
        </p>
      </SidebarFooter>
    </Sidebar>
  )
}
