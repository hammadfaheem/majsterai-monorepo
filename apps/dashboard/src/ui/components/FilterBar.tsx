/** FilterBar component for filtering lists. */

import { Input } from './Input'
import { Select } from './Select'
import { cn } from '@/lib/utils'

interface FilterOption {
  value: string
  label: string
}

interface FilterBarProps {
  searchValue?: string
  onSearchChange?: (value: string) => void
  searchPlaceholder?: string
  filterOptions?: {
    label: string
    value: string
    options: FilterOption[]
    onChange?: (value: string) => void
  }[]
  className?: string
}

export function FilterBar({
  searchValue,
  onSearchChange,
  searchPlaceholder = 'Search...',
  filterOptions,
  className,
}: FilterBarProps) {
  return (
    <div className={cn('flex gap-4 items-center', className)}>
      {onSearchChange && (
        <Input
          type="text"
          placeholder={searchPlaceholder}
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          className="max-w-sm"
        />
      )}
      {filterOptions?.map((filter) => (
        <Select
          key={filter.label}
          value={filter.value}
          onChange={(e) => filter.onChange?.(e.target.value)}
        >
          <option value="">All {filter.label}</option>
          {filter.options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      ))}
    </div>
  )
}
