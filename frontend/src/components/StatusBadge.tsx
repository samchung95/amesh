import { CircleCheck, CircleDashed, CircleX, LoaderCircle, TimerReset } from 'lucide-react'

const definitions = {
  SUCCESS: { icon: CircleCheck, label: 'Success', tone: 'success' },
  RUNNING: { icon: LoaderCircle, label: 'Running', tone: 'running' },
  FAILED: { icon: CircleX, label: 'Failed', tone: 'failed' },
  WAITING: { icon: TimerReset, label: 'Waiting', tone: 'waiting' },
  RETRY_DELAY: { icon: TimerReset, label: 'Retry delay', tone: 'warning' },
} as const

export function StatusBadge({ state }: { state: string }) {
  const definition = definitions[state as keyof typeof definitions] || {
    icon: CircleDashed,
    label: state,
    tone: 'unknown',
  }
  const Icon = definition.icon
  return (
    <span className={`status status-${definition.tone}`}>
      <Icon size={14} aria-hidden="true" />
      {definition.label}
    </span>
  )
}
