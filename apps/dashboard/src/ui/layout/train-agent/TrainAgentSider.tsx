import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutGrid } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TRAIN_AGENT_KNOWLEDGE_BASE_ITEMS } from '@/lib/train-agent-config'
import { TrainAgentSidebarSection } from './TrainAgentSidebarSection'

export function TrainAgentSider() {
  const { pathname } = useLocation()
  const [knowledgeBaseCollapsed, setKnowledgeBaseCollapsed] = useState(false)

  const isOverviewActive = pathname === '/train-agent' || pathname === '/train-agent/'

  return (
    <div className="hidden lg:flex w-full h-full min-h-0 bg-gray-50 dark:bg-slate-800/50 text-gray-900 dark:text-slate-100 overflow-y-auto flex-col">
      <div className="p-6 pb-4 flex flex-col h-full">
        <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
          Train Agent
        </h3>

        <div className="mb-2">
          <Link
            to="/train-agent"
            className={cn(
              'flex items-center gap-2 py-2.5 px-3 rounded-lg text-sm transition-colors',
              isOverviewActive
                ? 'bg-primary/10 text-primary font-medium'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100'
            )}
          >
            <LayoutGrid className="size-4" />
            <span>Overview</span>
          </Link>
        </div>

        <div className="mt-4">
          <TrainAgentSidebarSection
            title="Knowledge Base"
            items={TRAIN_AGENT_KNOWLEDGE_BASE_ITEMS}
            isCollapsed={knowledgeBaseCollapsed}
            onToggle={() => setKnowledgeBaseCollapsed((v) => !v)}
          />
        </div>
      </div>
    </div>
  )
}
