/** Train Agent Knowledge Base config – used by internal sidebar. */

export interface TrainAgentNavItem {
  id: string
  title: string
  href: string
  icon: 'building2' | 'wrench' | 'git-branch' | 'file-text' | 'help-circle' | 'message-circle' | 'phone-forwarded'
}

export const TRAIN_AGENT_KNOWLEDGE_BASE_ITEMS: TrainAgentNavItem[] = [
  {
    id: 'business-information',
    title: 'Business Information',
    href: '/train-agent/business-information',
    icon: 'building2',
  },
  {
    id: 'services',
    title: 'Services',
    href: '/train-agent/services',
    icon: 'wrench',
  },
  {
    id: 'scenarios',
    title: 'Scenarios',
    href: '/train-agent/scenarios',
    icon: 'git-branch',
  },
  {
    id: 'greeting-closing',
    title: 'Greeting and Closing',
    href: '/train-agent/greeting-closing',
    icon: 'message-circle',
  },
  {
    id: 'policies',
    title: 'Policies',
    href: '/train-agent/policies',
    icon: 'file-text',
  },
  {
    id: 'faqs',
    title: 'FAQs',
    href: '/train-agent/faqs',
    icon: 'help-circle',
  },
  {
    id: 'transfers',
    title: 'Transfers',
    href: '/train-agent/transfers',
    icon: 'phone-forwarded',
  },
]
