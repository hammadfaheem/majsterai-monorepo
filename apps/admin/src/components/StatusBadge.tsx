import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  status: string
  className?: string
}

const statusColors: Record<string, string> = {
  // Platform roles
  superadmin: 'bg-purple-100 text-purple-800',
  staff: 'bg-blue-100 text-blue-800',
  customer: 'bg-slate-100 text-slate-800',
  // Generic statuses
  active: 'bg-green-100 text-green-800',
  completed: 'bg-green-100 text-green-800',
  pending: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const colorClass = statusColors[status.toLowerCase()] ?? statusColors['pending']
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        colorClass,
        className,
      )}
    >
      {status}
    </span>
  )
}
