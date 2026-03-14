import { Link, useLocation } from 'react-router-dom'
import {
  Building2,
  ChevronDown,
  ChevronRight,
  FileText,
  GitBranch,
  HelpCircle,
  MessageCircle,
  PhoneForwarded,
  Wrench,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { TrainAgentNavItem } from '@/lib/train-agent-config'
import { Button } from '@/ui/components/Button'

const ICON_MAP: Record<TrainAgentNavItem['icon'], LucideIcon> = {
  'building2': Building2,
  'wrench': Wrench,
  'git-branch': GitBranch,
  'file-text': FileText,
  'help-circle': HelpCircle,
  'message-circle': MessageCircle,
  'phone-forwarded': PhoneForwarded,
}

interface TrainAgentSidebarSectionProps {
  title: string
  items: TrainAgentNavItem[]
  isCollapsed: boolean
  onToggle: () => void
}

export function TrainAgentSidebarSection({
  title,
  items,
  isCollapsed,
  onToggle,
}: TrainAgentSidebarSectionProps) {
  const { pathname } = useLocation()

  return (
    <div className="mb-2">
      <Button
        variant="ghost"
        className="w-full justify-start text-left h-8 px-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100"
        onClick={onToggle}
      >
        <div className="flex items-center gap-2">
          {isCollapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
          <span className="text-xs font-medium">{title}</span>
          <span className="ml-auto text-xs text-gray-500">{items.length}</span>
        </div>
      </Button>
      {!isCollapsed && (
        <div className="ml-4 mt-1 space-y-1">
          {items.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(`${item.href}/`)
            const Icon = ICON_MAP[item.icon]

            return (
              <Link
                key={item.id}
                to={item.href}
                className={cn(
                  'flex items-center gap-2 py-1 px-2 rounded text-xs transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <Icon className="h-3 w-3 flex-shrink-0" />
                <span className="flex-1 min-w-0">{item.title}</span>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
