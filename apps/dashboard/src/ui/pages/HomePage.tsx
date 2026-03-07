import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/ui/components/Card'
import { Mic, Settings } from 'lucide-react'
import { Button } from '@/ui/components/Button'
import { useTestAgentWidgetStore } from '@/store/testAgentWidget.store'

export function HomePage() {
  const openWidget = useTestAgentWidgetStore((s) => s.open)

  return (
    <div className="space-y-6">
      {/* Main Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Test Agent Card */}
        <Card className="group hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
              <Mic className="h-6 w-6 text-accent" />
            </div>
            <CardTitle>Test Agent</CardTitle>
            <CardDescription>
              Start a voice conversation with your AI agent. Test prompts and configurations in real-time.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="accent" className="w-full" onClick={openWidget}>
              Start Testing
            </Button>
          </CardContent>
        </Card>

        {/* Configure Card */}
        <Card className="opacity-60">
          <CardHeader>
            <div className="w-12 h-12 bg-slate-200 rounded-lg flex items-center justify-center mb-4">
              <Settings className="h-6 w-6 text-slate-500" />
            </div>
            <CardTitle>Configure Agent</CardTitle>
            <CardDescription>
              Customize your agent&apos;s prompt, voice, and behavior settings.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" disabled>
              Coming Soon
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Status - Bottom Right */}
      <div className="flex justify-end">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          API Connected
        </div>
      </div>
    </div>
  )
}
