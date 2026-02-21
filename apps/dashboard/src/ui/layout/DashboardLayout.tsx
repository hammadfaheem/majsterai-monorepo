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
          'min-h-screen transition-all duration-300',
          'ml-0',
          sidebarOpen ? 'md:ml-64' : 'md:ml-20'
        )}
      >
        <Header />

        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
