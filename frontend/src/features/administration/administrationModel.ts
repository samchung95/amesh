import type {
  AdministrationControl,
  AdministrationControlDraft,
  AdministrationControlKey,
  ConfigurationSnapshot,
} from '../../api/types'

export const CONTROL_COPY: Record<AdministrationControlKey, { title: string; summary: string; valueLabel?: string }> = {
  RETENTION: { title: 'Execution retention', summary: 'Set the tenant retention horizon before lifecycle sweeps.', valueLabel: 'Days' },
  ANNOUNCEMENT: { title: 'Operator announcement', summary: 'Publish a tenant-wide banner for signed-in operators.', valueLabel: 'Message' },
  MAINTENANCE: { title: 'Maintenance mode', summary: 'Signal a restricted-change maintenance window.' },
  KILL_SWITCH: { title: 'Execution kill switch', summary: 'Stop new execution admission during an incident.' },
}

export function namespaceHierarchy(namespaces: string[]): Array<{ namespace: string; depth: number; direct: boolean }> {
  const direct = new Set(namespaces.filter(Boolean))
  const all = new Set<string>()
  for (const namespace of direct) {
    const parts = namespace.split('.')
    for (let index = 1; index <= parts.length; index += 1) all.add(parts.slice(0, index).join('.'))
  }
  return [...all].sort().map((namespace) => ({
    namespace,
    depth: namespace.split('.').length - 1,
    direct: direct.has(namespace),
  }))
}

export function administrationControlDraft(
  control: AdministrationControl,
  enabled: boolean,
  value: string,
  reason: string,
): AdministrationControlDraft {
  const parsedValue = control.key === 'RETENTION'
    ? Number.parseInt(value, 10)
    : control.key === 'ANNOUNCEMENT' ? value.trim() : null
  if (control.key === 'RETENTION' && (!Number.isInteger(parsedValue) || Number(parsedValue) < 1 || Number(parsedValue) > 3650)) {
    throw new Error('Retention days must be an integer between 1 and 3650.')
  }
  if (control.key === 'ANNOUNCEMENT' && enabled && !String(parsedValue).trim()) {
    throw new Error('An enabled announcement requires a message.')
  }
  if (reason.trim().length < 3) throw new Error('Give a reason of at least three characters.')
  return {
    key: control.key,
    enabled,
    value: parsedValue,
    reason: reason.trim(),
    expectedVersion: control.version,
  }
}

export function visibleConfiguration(entries: ConfigurationSnapshot['entries'], query: string) {
  const normalized = query.trim().toLowerCase()
  return entries.filter((entry) => !normalized || `${entry.name} ${entry.source}`.toLowerCase().includes(normalized))
}

export function configurationValue(entry: ConfigurationSnapshot['entries'][number]): string {
  if (entry.secret) return '[REDACTED]'
  if (entry.value === null) return 'null'
  return typeof entry.value === 'string' ? entry.value : JSON.stringify(entry.value)
}
