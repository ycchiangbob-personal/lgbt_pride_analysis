'use client'

import Image from 'next/image'
import Link from 'next/link'
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
  { label: '總覽', href: '/',            icon: LayoutDashboard },
  { label: '忠實贊助商', href: '/loyalist',  icon: Star },
  { label: '留存率', href: '/retention', icon: TrendingUp },
  { label: '挽回清單', href: '/winback',   icon: RotateCcw },
  { label: '採購行為', href: '/purchase',  icon: ShoppingCart },
  { label: '新品牌續約率', href: '/new-brand', icon: Sparkles },
  { label: '機會識別', href: '/opportunity', icon: Target },
  { label: '贊助商名錄', href: '/directory', icon: BookOpen },
  { label: '遊行隊伍', href: '/parade',    icon: Flag },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-border px-4 py-4">
        <div className="flex flex-col gap-1">
          <Image
            src="/logo-light.png"
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
                      <Link href={item.href} className="flex items-center gap-2">
                        <item.icon className="h-4 w-4 shrink-0" />
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
