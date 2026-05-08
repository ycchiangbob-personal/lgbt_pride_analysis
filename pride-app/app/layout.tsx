import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import { AppSidebar } from '@/components/app-sidebar'
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: '臺灣同志遊行 商業贊助分析 2016–2025',
  description: '臺灣同志遊行商業贊助資料庫，2016–2025年度跨年度分析報告',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="zh-TW"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="h-full">
        <SidebarProvider>
          <AppSidebar />
          <SidebarInset className="flex flex-col min-h-screen">
            {/* Rainbow stripe header */}
            <header
              className="flex shrink-0 items-center gap-3 px-4 h-14 border-b border-border bg-surface"
              style={{
                background:
                  'var(--rainbow) top/100% 6px no-repeat, var(--surface)',
                paddingTop: '6px',
              }}
            >
              <SidebarTrigger className="text-text-secondary hover:text-foreground" />
              <div
                className="h-4 w-px bg-border"
                aria-hidden="true"
              />
              <span className="text-sm font-medium text-text-secondary">
                臺灣同志遊行 商業贊助分析
              </span>
            </header>

            <main className="flex-1 overflow-auto p-6">
              {children}
            </main>
          </SidebarInset>
        </SidebarProvider>
      </body>
    </html>
  )
}
