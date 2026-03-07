import { Outlet } from 'react-router-dom'

/** Simple layout for onboarding pages - shared branding and container. */
export function OnboardingLayout() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">
      <header className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
        <h1
          className="font-bold text-2xl tracking-tight text-slate-900 dark:text-slate-100"
          style={{ fontFamily: 'Poppins, sans-serif' }}
        >
          Majster<span className="text-accent">AI</span>
        </h1>
      </header>
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
