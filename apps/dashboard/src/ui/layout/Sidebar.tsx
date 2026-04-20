import { useEffect, useMemo } from 'react'
import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/store/ui.store'
import {
  LayoutDashboard,
  Settings,
  Phone,
  UserPlus,
  Calendar,
  FileText,
  CheckSquare,
  GraduationCap,
} from 'lucide-react'

const baseNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Leads', href: '/leads', icon: UserPlus },
  { name: 'Calls', href: '/calls', icon: Phone },
  { name: 'Appointments', href: '/appointments', icon: Calendar },
  { name: 'Invoices', href: '/invoices', icon: FileText },
  { name: 'Train Agent', href: '/train-agent', icon: GraduationCap },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const MOBILE_BREAKPOINT = 768

export function Sidebar() {
  const { sidebarOpen, setSidebarOpen } = useUIStore()
  const navigation = useMemo(() => [...baseNavigation], [])

  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth >= MOBILE_BREAKPOINT) return
      setSidebarOpen(false)
    }
    onResize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [setSidebarOpen])

  return (
    <>
      {/* Backdrop on mobile when sidebar open */}
      <div
        aria-hidden
        className={cn(
          'fixed inset-0 z-30 bg-black/50 transition-opacity md:hidden',
          sidebarOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        )}
        onClick={() => setSidebarOpen(false)}
      />
      <aside
        className={cn(
          'fixed left-0 top-0 z-40 flex h-screen flex-col transition-all duration-300',
          'bg-[#142236] border-r border-[#0e1724] text-white',
          'w-64 min-w-64',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
          'md:w-64 md:min-w-64'
        )}
      >
      <div className="flex h-16 flex-shrink-0 items-center justify-center border-b border-[#0e1724]">
        <h1 className={cn('font-bold text-xl text-white', !sidebarOpen && 'text-sm')}>
          {sidebarOpen ? (
            <>
              Majster<span className="text-primary">AI</span>
            </>
          ) : (
            'M'
          )}
        </h1>
      </div>

      {/* {sidebarOpen && (
        <div className="flex-shrink-0 p-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-1">
            Welcome to MajsterAI  
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            Voice AI Agent Platform - Build, test, and deploy intelligent voice assistants.
          </p>
        </div>
      )} */}

      <nav className="flex-1 min-h-0 overflow-y-auto flex flex-col gap-1 p-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                'hover:bg-white/10',
                isActive
                  ? 'bg-white/10 text-white border-l-2 border-l-primary'
                  : 'text-white/80'
              )
            }
          >
            <item.icon className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span>{item.name}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
    </>
  )
}
