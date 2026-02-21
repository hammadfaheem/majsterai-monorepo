import { useEffect, useMemo } from 'react'
import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/store/ui.store'
import { useAppSelector } from '@/store/hooks'
import { LayoutDashboard, Mic, Settings, Users, Phone, UserPlus, Calendar, Wrench, FileText, Bot, GitBranch, PhoneForwarded, CalendarClock, Building2, Tag, CheckSquare, ShieldCheck } from 'lucide-react'

const baseNavigation = [
  // { name: 'Home', href: '/', icon: LayoutDashboard },
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Leads', href: '/leads', icon: UserPlus },
  { name: 'Calls', href: '/calls', icon: Phone },
  { name: 'Appointments', href: '/appointments', icon: Calendar },
  { name: 'Team', href: '/team', icon: Users },
  { name: 'Services', href: '/services', icon: Wrench },
  { name: 'Invoices', href: '/invoices', icon: FileText },
  { name: 'Agent', href: '/agent', icon: Bot },
  { name: 'Scenarios', href: '/scenarios', icon: GitBranch },
  { name: 'Transfers', href: '/transfers', icon: PhoneForwarded },
  { name: 'Schedules', href: '/schedules', icon: CalendarClock },
  { name: 'Departments', href: '/departments', icon: Building2 },
  { name: 'Tags', href: '/tags', icon: Tag },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare },
  { name: 'Test Agent', href: '/test-agent', icon: Mic },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const MOBILE_BREAKPOINT = 768

export function Sidebar() {
  const { sidebarOpen, setSidebarOpen } = useUIStore()
  const user = useAppSelector((state) => state.auth.user)
  const navigation = useMemo(() => {
    const nav = [...baseNavigation]
    if (user?.role === 'SUPERADMIN') {
      nav.push({ name: 'Admin', href: '/admin', icon: ShieldCheck })
    }
    return nav
  }, [user?.role])

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
          'fixed left-0 top-0 z-40 flex h-screen flex-col transition-all duration-300 bg-white border-r border-slate-200 dark:bg-slate-900 dark:border-slate-800',
          'w-64 md:transition-[width]',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
          sidebarOpen ? 'md:w-64' : 'md:w-20'
        )}
      >
      <div className="flex h-16 flex-shrink-0 items-center justify-center border-b border-slate-200 dark:border-slate-800">
        <h1 className={cn('font-bold text-xl text-slate-900 dark:text-slate-100', !sidebarOpen && 'text-sm')}>
          {sidebarOpen ? (
            <>
              Majster<span className="text-accent">AI</span>
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
                'hover:bg-slate-100 dark:hover:bg-slate-800',
                isActive
                  ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white'
                  : 'text-slate-600 dark:text-slate-300'
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
