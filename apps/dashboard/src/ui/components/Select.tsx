import * as React from 'react'
import { cn } from '@/lib/utils'

const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => {
  return (
    <select
      className={cn(
        'flex h-10 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        'dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:ring-offset-slate-900 dark:focus-visible:ring-slate-400',
        className
      )}
      ref={ref}
      {...props}
    >
      {children}
    </select>
  )
})
Select.displayName = 'Select'

const SelectTrigger = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, ...props }, ref) => (
  <Select ref={ref} className={className} {...props} />
))
SelectTrigger.displayName = 'SelectTrigger'

const SelectContent = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>
}

const SelectValue = ({ placeholder }: { placeholder?: string }) => {
  return <option value="">{placeholder}</option>
}

const SelectItem = React.forwardRef<
  HTMLOptionElement,
  React.OptionHTMLAttributes<HTMLOptionElement>
>(({ className, ...props }, ref) => (
  <option ref={ref} className={className} {...props} />
))
SelectItem.displayName = 'SelectItem'

export { Select, SelectTrigger, SelectContent, SelectValue, SelectItem }
