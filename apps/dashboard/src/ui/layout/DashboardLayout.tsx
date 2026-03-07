import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { useUIStore } from '@/store/ui.store'
import { cn } from '@/lib/utils'

export function DashboardLayout() {
  const { sidebarOpen } = useUIStore()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div
        className={cn(
          'flex flex-col min-h-screen transition-all duration-300',
          'ml-0 md:ml-64'
        )}
      >
        <Header />

        <main className="flex-1 min-h-0 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
