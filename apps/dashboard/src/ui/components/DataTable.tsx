/** DataTable component for displaying tabular data. */

import { cn } from '@/lib/utils'

interface Column<T> {
  key: keyof T | string
  header: string
  render?: (value: unknown, row: T) => React.ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  className?: string
  onRowClick?: (row: T) => void
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  className,
  onRowClick,
}: DataTableProps<T>) {
  return (
    <div className={cn('overflow-x-auto -mx-4 sm:mx-0', className)}>
      <table className="min-w-[600px] w-full divide-y divide-slate-200 dark:divide-slate-700">
        <thead className="bg-slate-50 dark:bg-slate-800/50">
          <tr>
            {columns.map((column) => (
              <th
                key={String(column.key)}
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400 sm:px-6"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white dark:divide-slate-700 dark:bg-slate-800/30">
          {data.map((row, index) => (
            <tr
              key={index}
              onClick={() => onRowClick?.(row)}
              className={cn(
                'hover:bg-slate-50 dark:hover:bg-slate-700/50',
                onRowClick && 'cursor-pointer'
              )}
            >
              {columns.map((column) => {
                const value = column.key in row ? row[column.key] : null
                return (
                  <td
                    key={String(column.key)}
                    className="whitespace-nowrap px-4 py-4 text-sm text-slate-900 dark:text-slate-100 sm:px-6"
                  >
                    {column.render ? column.render(value, row) : String(value ?? '')}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length === 0 && (
        <div className="py-12 text-center text-sm text-slate-500 dark:text-slate-400">
          No data available
        </div>
      )}
    </div>
  )
}
