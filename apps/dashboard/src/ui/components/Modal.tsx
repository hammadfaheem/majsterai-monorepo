import { useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Button } from './Button'
import { X } from 'lucide-react'

interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  className?: string
  size?: 'md' | 'lg'
}

export function Modal({ open, onClose, title, children, className, size = 'md' }: ModalProps) {
  useEffect(() => {
    const onEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (open) {
      document.addEventListener('keydown', onEscape)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', onEscape)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4">
      <div
        className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm"
        aria-hidden
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal
        aria-labelledby="modal-title"
        className={cn(
          'relative z-10 w-full max-h-[calc(100vh-1rem)] flex flex-col rounded-xl border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-900',
          size === 'lg' ? 'max-w-lg' : 'max-w-md',
          'sm:max-h-[calc(100vh-2rem)]',
          className
        )}
      >
        <div className="flex items-center justify-between flex-shrink-0 border-b border-slate-200 dark:border-slate-700 px-6 py-4">
          <h2 id="modal-title" className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {title}
          </h2>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close">
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="overflow-y-auto px-6 py-4">{children}</div>
      </div>
    </div>
  )
}
