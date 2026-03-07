import { Outlet } from 'react-router-dom'
import { Mic } from 'lucide-react'
import { Button } from '@/ui/components/Button'
import { TrainAgentSider } from './TrainAgentSider'
import { useTestAgentWidgetStore } from '@/store/testAgentWidget.store'

export function TrainAgentLayout() {
  const openWidget = useTestAgentWidgetStore((s) => s.open)
  const isWidgetOpen = useTestAgentWidgetStore((s) => s.isOpen)

  return (
    <div className="flex flex-col lg:flex-row min-h-[calc(100vh-4rem)] -m-6">
      <aside className="lg:w-72 lg:flex-shrink-0 lg:h-full border-r border-slate-200 dark:border-slate-800">
        <TrainAgentSider />
      </aside>
      <div className="flex-1 overflow-y-auto bg-white dark:bg-slate-900 min-w-0">
        <div className="p-6 md:p-6">
          <Outlet />
        </div>
      </div>
      {!isWidgetOpen && (
        <div className="fixed bottom-6 right-6 z-40 shadow-lg rounded-lg">
          <Button
            variant="accent"
            size="lg"
            className="gap-2"
            onClick={openWidget}
          >
            <Mic className="w-5 h-5" />
            Test Agent
          </Button>
        </div>
      )}
    </div>
  )
}
