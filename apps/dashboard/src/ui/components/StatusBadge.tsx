/** StatusBadge component for displaying status indicators. */

import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  status: string
  className?: string
}

const statusColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800',
  contacted: 'bg-yellow-100 text-yellow-800',
  qualified: 'bg-purple-100 text-purple-800',
  converted: 'bg-green-100 text-green-800',
  lost: 'bg-red-100 text-red-800',
  pending: 'bg-gray-100 text-gray-800',
  active: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  ready: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const colorClass = statusColors[status.toLowerCase()] || statusColors.pending

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        colorClass,
        className
      )}
    >
      {status}
    </span>
  )
}
