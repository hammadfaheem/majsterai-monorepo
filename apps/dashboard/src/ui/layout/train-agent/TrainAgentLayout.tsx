import { Outlet } from 'react-router-dom'
import { TrainAgentSider } from './TrainAgentSider'

export function TrainAgentLayout() {
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
    </div>
  )
}
