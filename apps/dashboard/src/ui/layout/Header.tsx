import { Menu, Bell, User, LogOut, ChevronDown, Sun, Moon } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logout } from '@/store/authSlice'
import { useUIStore } from '@/store/ui.store'
import { useOrganization } from '@/application/organization/organizationContext'
import { Button } from '@/ui/components/Button'
import { userService } from '@/application/user/userService'
import { cn } from '@/lib/utils'

export function Header() {
  const { toggleSidebar, theme, setTheme } = useUIStore()
  const { user } = useAppSelector((state) => state.auth)
  const { currentOrganization, organizations, setCurrentOrganization } = useOrganization()
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [orgDropdownOpen, setOrgDropdownOpen] = useState(false)

  async function handleLogout() {
    try {
      await userService.logout()
    } catch {
      // ignore
    }
    dispatch(logout())
    navigate('/login', { replace: true })
  }

  return (
    <header className="sticky top-0 z-20 flex h-14 min-h-14 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-900 md:h-16 md:px-6">
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="min-h-11 min-w-11 touch-manipulation md:h-10 md:w-10"
        >
          <Menu className="h-5 w-5" />
        </Button>

        {organizations.length > 1 && (
          <div className="relative">
            <button
              type="button"
              onClick={() => setOrgDropdownOpen((o) => !o)}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 min-h-11 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 md:min-h-10"
            >
              <span className="truncate max-w-32 sm:max-w-48">
                {currentOrganization?.name ?? 'Select org'}
              </span>
              <ChevronDown className={cn('h-4 w-4 flex-shrink-0', orgDropdownOpen && 'rotate-180')} />
            </button>
            {orgDropdownOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  aria-hidden
                  onClick={() => setOrgDropdownOpen(false)}
                />
                <div className="absolute left-0 top-full z-20 mt-1 w-56 rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-800">
                  {organizations.map((org) => (
                    <button
                      key={org.id}
                      type="button"
                      onClick={() => {
                        setCurrentOrganization(org)
                        setOrgDropdownOpen(false)
                      }}
                      className={cn(
                        'w-full px-3 py-2 text-left text-sm',
                        currentOrganization?.id === org.id
                          ? 'bg-slate-100 font-medium text-slate-900 dark:bg-slate-700 dark:text-slate-100'
                          : 'text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-700'
                      )}
                    >
                      {org.name}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          className="min-h-11 min-w-11 touch-manipulation md:h-10 md:w-10"
        >
          {theme === 'dark' ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="min-h-11 min-w-11 touch-manipulation md:h-10 md:w-10"
        >
          <Bell className="h-5 w-5" />
        </Button>

        <div className="flex items-center gap-2 pl-2 md:gap-3 md:pl-4 border-l border-slate-200 dark:border-slate-700">
          <div className="hidden flex-col items-end sm:flex">
            <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{user?.name ?? 'User'}</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 truncate max-w-32">{user?.email ?? ''}</span>
          </div>
          <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-700">
            <User className="h-5 w-5 text-slate-600 dark:text-slate-300" />
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleLogout}
            title="Sign out"
            className="min-h-9 gap-1.5 px-2 md:px-3 md:gap-2"
          >
            <LogOut className="h-4 w-4 md:h-4 md:w-4" />
            <span className="hidden sm:inline text-sm font-medium">Log out</span>
          </Button>
        </div>
      </div>
    </header>
  )
}
