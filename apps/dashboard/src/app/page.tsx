import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
            Majster<span className="text-accent">AI</span>
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Voice AI Agent Platform - Build, test, and deploy intelligent voice assistants
          </p>
        </header>

        {/* Main Actions */}
        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
          {/* Test Agent Card */}
          <Link
            href="/test-agent"
            className="group relative bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8 hover:border-accent/50 transition-all duration-300 hover:shadow-lg hover:shadow-accent/10"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-6">
                <svg
                  className="w-7 h-7 text-accent"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-3">Test Agent</h2>
              <p className="text-slate-400">
                Start a voice conversation with your AI agent. Test prompts and configurations in real-time.
              </p>
            </div>
          </Link>

          {/* Configure Card */}
          <div className="relative bg-slate-800/30 backdrop-blur border border-slate-700/50 rounded-2xl p-8 opacity-60">
            <div className="w-14 h-14 bg-slate-700/50 rounded-xl flex items-center justify-center mb-6">
              <svg
                className="w-7 h-7 text-slate-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-slate-400 mb-3">Configure Agent</h2>
            <p className="text-slate-500">
              Customize your agent&apos;s prompt, voice, and behavior settings.
            </p>
            <span className="absolute top-4 right-4 text-xs font-medium text-slate-500 bg-slate-700/50 px-2 py-1 rounded">
              Coming Soon
            </span>
          </div>
        </div>

        {/* Status */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 text-sm text-slate-400">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            API Connected
          </div>
        </div>
      </div>
    </div>
  );
}
