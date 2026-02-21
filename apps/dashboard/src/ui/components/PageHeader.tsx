import { cn } from '@/lib/utils'

interface PageHeaderProps {
  title: string
  description?: string
  className?: string
}

export function PageHeader({ title, description, className }: PageHeaderProps) {
  return (
    <div className={className}>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 sm:text-3xl">
        {title}
      </h1>
      {description && (
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{description}</p>
      )}
    </div>
  )
}
