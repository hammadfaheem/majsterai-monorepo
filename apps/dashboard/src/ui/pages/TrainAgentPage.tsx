/** Train Agent – hub for configuring voice AI. */

import { Link } from 'react-router-dom'
import {
  Bot,
  RefreshCw,
  Sparkles,
  BookOpen,
  Wrench,
  GitBranch,
  Users,
  Building2,
  PhoneForwarded,
  ChevronRight,
  Tag,
  CalendarClock,
  Star,
  Mic,
  type LucideIcon,
} from 'lucide-react'
import { Card, CardContent } from '@/ui/components/Card'
import { Button } from '@/ui/components/Button'
import { useSetupProgress } from '@/lib/hooks/useSetupProgress'
import { cn } from '@/lib/utils'

const REQUIRED_STEPS_CARDS: {
  id: string
  icon: LucideIcon
  title: string
  description: string
  href: string
}[] = [
  {
    id: 'agent',
    icon: Bot,
    title: 'Agent',
    description: 'Name, prompt, and variables',
    href: '/agent',
  },
  {
    id: 'services',
    icon: Wrench,
    title: 'Services',
    description: 'Core services offered',
    href: '/services',
  },
  {
    id: 'scenarios',
    icon: GitBranch,
    title: 'Scenarios',
    description: 'Conversation flows and restrictions',
    href: '/scenarios',
  },
  {
    id: 'team',
    icon: Users,
    title: 'Team',
    description: 'Team members and contacts',
    href: '/team',
  },
  {
    id: 'departments',
    icon: Building2,
    title: 'Departments',
    description: 'Organize team into departments',
    href: '/departments',
  },
  {
    id: 'transfers',
    icon: PhoneForwarded,
    title: 'Transfers',
    description: 'Call handoff logic',
    href: '/transfers',
  },
]

const RECOMMENDED_IMPROVEMENTS_CARDS: {
  id: string
  icon: LucideIcon
  title: string
  description: string
  href: string
}[] = [
  {
    id: 'tags',
    icon: Tag,
    title: 'Tags',
    description: 'Organize and label conversations',
    href: '/tags',
  },
  {
    id: 'schedules',
    icon: CalendarClock,
    title: 'Schedules',
    description: 'Availability and working hours',
    href: '/schedules',
  },
  {
    id: 'transfers-rec',
    icon: PhoneForwarded,
    title: 'Transfers',
    description: 'Call handoff logic',
    href: '/transfers',
  },
  {
    id: 'agent-rec',
    icon: Bot,
    title: 'Voice & Personality',
    description: 'Prompt and agent configuration',
    href: '/agent',
  },
]

const KNOWLEDGE_BASE_CARDS: {
  id: string
  icon: LucideIcon
  title: string
  description: string
  href: string
}[] = [
  {
    id: 'agent-kb',
    icon: Bot,
    title: 'Agent',
    description: 'Logo, name, prompt, variables',
    href: '/agent',
  },
  {
    id: 'services-kb',
    icon: Wrench,
    title: 'Services',
    description: 'Core services offered',
    href: '/services',
  },
  {
    id: 'scenarios-kb',
    icon: GitBranch,
    title: 'Scenarios',
    description: 'Conversation flows and restrictions',
    href: '/scenarios',
  },
  {
    id: 'team-kb',
    icon: Users,
    title: 'Team',
    description: 'Team members and contacts',
    href: '/team',
  },
  {
    id: 'departments-kb',
    icon: Building2,
    title: 'Departments',
    description: 'Organize team into departments',
    href: '/departments',
  },
  {
    id: 'tags-kb',
    icon: Tag,
    title: 'Tags',
    description: 'Organize or label conversations',
    href: '/tags',
  },
]

function ConfigCard({
  icon: Icon,
  title,
  description,
  href,
}: {
  icon: LucideIcon
  title: string
  description: string
  href: string
}) {
  return (
    <Link to={href}>
      <Card
        className={cn(
          'hover:shadow-lg transition-shadow cursor-pointer h-full',
          'border-slate-200 dark:border-slate-700'
        )}
      >
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-2">
            <div className="size-10 rounded-xl flex items-center justify-center bg-slate-100 dark:bg-slate-800">
              <Icon className="size-5 text-slate-600 dark:text-slate-400" />
            </div>
          </div>
          <div className="mb-2">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">
              {title}
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
              {description}
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <ChevronRight className="w-4 h-4" />
            <span>Configure</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

export function TrainAgentPage() {
  const { completedCards, totalCards, progress, isPending } =
    useSetupProgress()

  return (
    <>
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
            <Bot className="w-4 h-4 text-slate-600 dark:text-slate-400" />
          </div>
          <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
            Setup Your AI Assistant
          </span>
        </div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
          Train Agent
        </h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 max-w-2xl">
          Configure these settings to ensure your agent can handle customer
          interactions effectively.
        </p>
      </div>

      {/* Setup Progress */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Setup Progress
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                {isPending
                  ? 'Loading…'
                  : `${completedCards} of ${totalCards} items completed`}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Star className="w-5 h-5 text-slate-500 dark:text-slate-400" />
              <span className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {isPending ? '…' : `${Math.round(progress)}%`}
              </span>
            </div>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
            <div
              className="h-full rounded-full bg-accent transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Required Steps */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <RefreshCw className="w-6 h-6 text-slate-600 dark:text-slate-400" />
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Required Steps
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {REQUIRED_STEPS_CARDS.map((card) => (
            <ConfigCard key={card.id} {...card} />
          ))}
        </div>
      </section>

      {/* Recommended Improvements */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-6 h-6 text-slate-600 dark:text-slate-400" />
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Recommended Improvements
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {RECOMMENDED_IMPROVEMENTS_CARDS.map((card) => (
            <ConfigCard key={card.id} {...card} />
          ))}
        </div>
      </section>

      {/* Knowledge Base */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-6 h-6 text-slate-600 dark:text-slate-400" />
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Knowledge Base
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {KNOWLEDGE_BASE_CARDS.map((card) => (
            <ConfigCard key={card.id} {...card} />
          ))}
        </div>
      </section>
    </div>

    <Link
      to="/test-agent"
      className="fixed bottom-6 right-6 z-50 shadow-lg rounded-lg"
    >
      <Button
        variant="accent"
        size="lg"
        className="gap-2"
      >
        <Mic className="w-5 h-5" />
        Test Agent
      </Button>
    </Link>
    </>
  )
}
