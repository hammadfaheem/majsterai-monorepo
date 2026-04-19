import { Card, CardContent } from './Card'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: string | number
  description?: string
  className?: string
}

export function MetricCard({ title, value, description, className }: MetricCardProps) {
  return (
    <Card className={cn('border-l-4 border-l-accent', className)}>
      <CardContent className="p-6">
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <p className="text-3xl font-bold text-slate-900">{value}</p>
          {description && <p className="text-xs text-slate-500">{description}</p>}
        </div>
      </CardContent>
    </Card>
  )
}
