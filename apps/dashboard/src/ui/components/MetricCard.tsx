/** MetricCard component for displaying metrics. */

import { Card, CardContent } from './Card'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: string | number
  description?: string
  trend?: {
    value: number
    isPositive: boolean
  }
  className?: string
}

export function MetricCard({
  title,
  value,
  description,
  trend,
  className,
}: MetricCardProps) {
  return (
    <Card className={cn('border-l-4 border-l-accent', className)}>
      <CardContent className="p-6">
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">{value}</p>
            {trend && (
              <span
                className={cn(
                  'text-sm font-medium',
                  trend.isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                )}
              >
                {trend.isPositive ? '+' : ''}
                {trend.value}%
              </span>
            )}
          </div>
          {description && (
            <p className="text-xs text-slate-500 dark:text-slate-400">{description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
