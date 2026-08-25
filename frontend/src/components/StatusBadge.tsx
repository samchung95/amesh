import { CircleCheck, CircleDashed, CircleX, LoaderCircle, TimerReset } from 'lucide-react'

const definitions = {
  SUCCESS: { icon: CircleCheck, label: 'Success', tone: 'success' },
  RUNNING: { icon: LoaderCircle, label: 'Running', tone: 'running' },
  FAILED: { icon: CircleX, label: 'Failed', tone: 'failed' },
  WAITING: { icon: TimerReset, label: 'Waiting', tone: 'waiting' },
  RETRY_DELAY: { icon: TimerReset, label: 'Retry delay', tone: 'warning' },
  ACCEPTED: { icon: TimerReset, label: 'Accepted', tone: 'waiting' },
  DEFERRED: { icon: TimerReset, label: 'Deferred', tone: 'warning' },
  PROCESSING: { icon: LoaderCircle, label: 'Processing', tone: 'running' },
  RETRY_WAIT: { icon: TimerReset, label: 'Retry wait', tone: 'warning' },
  SUCCEEDED: { icon: CircleCheck, label: 'Succeeded', tone: 'success' },
  DEAD_LETTERED: { icon: CircleX, label: 'Dead letter', tone: 'failed' },
  PAUSED: { icon: TimerReset, label: 'Paused', tone: 'warning' },
  ACTIVE: { icon: CircleCheck, label: 'Active', tone: 'success' },
  KILLED: { icon: CircleX, label: 'Killed', tone: 'failed' },
  PROMOTE: { icon: CircleCheck, label: 'Promote', tone: 'success' },
  ROLLBACK: { icon: TimerReset, label: 'Rollback', tone: 'warning' },
  KILL_SWITCH: { icon: CircleX, label: 'Kill switch', tone: 'failed' },
  PASS: { icon: CircleCheck, label: 'Pass', tone: 'success' },
  WARN: { icon: TimerReset, label: 'Warning', tone: 'warning' },
  FAIL: { icon: CircleX, label: 'Fail', tone: 'failed' },
  ERROR: { icon: CircleX, label: 'Error', tone: 'failed' },
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
