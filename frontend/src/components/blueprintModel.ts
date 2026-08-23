import type {
  AuthenticationProvider,
  ConfigurationSnapshot,
  ReadinessResponse,
  ServiceTopology,
} from '../api/types'

export interface OnboardingCheck {
  id: 'stack' | 'sample' | 'draft' | 'run'
  title: string
  detail: string
}

export interface ReadinessCheck {
  id: 'database' | 'storage' | 'runner' | 'authentication'
  title: string
  ready: boolean
  detail: string
}

export const ONBOARDING_CHECKS: OnboardingCheck[] = [
  { id: 'stack', title: 'Start the local stack', detail: 'Run docker compose up --build and open this control room.' },
  { id: 'sample', title: 'Preview a sample', detail: 'Open the built-in Hello, workflow blueprint.' },
  { id: 'draft', title: 'Create a draft', detail: 'Choose parameters and open the unsaved draft in the flow editor.' },
  { id: 'run', title: 'Save and run locally', detail: 'Save the validated draft, then execute it manually from Flow details.' },
]

export function blueprintDraftTransferKey(
  tenant: string,
  principalId: string,
  blueprintId: string,
  version: string,
): string {
  return `amesh.blueprint-draft.v1:${tenant}:${principalId}:${blueprintId}:${version}`
}

export function onboardingProgressKey(tenant: string, principalId: string): string {
  return `amesh.onboarding.v1:${tenant}:${principalId}`
}

export function readOnboardingProgress(storage: Storage, key: string): string[] {
  try {
    const value = JSON.parse(storage.getItem(key) || '[]') as unknown
    return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
  } catch {
    return []
  }
}

export function configurationEntry(
  configuration: ConfigurationSnapshot | undefined,
  name: string,
): unknown {
  return configuration?.entries.find((entry) => entry.name === name)?.value
}

function configurationText(value: unknown): string {
  return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
    ? String(value)
    : ''
}

export function onboardingReadiness(
  readiness: ReadinessResponse | undefined,
  configuration: ConfigurationSnapshot | undefined,
  providers: AuthenticationProvider[] | undefined,
  topology?: ServiceTopology,
): ReadinessCheck[] {
  const databaseReady = readiness?.status === 'ready' && readiness.database === 'ready'
  const storageBackend = configurationEntry(configuration, 'object_storage_backend')
  const runnerMode = configurationEntry(configuration, 'execution_runner_mode')
  const localRunner = configurationEntry(configuration, 'local_process_runner_enabled')
  const storageText = configurationText(storageBackend)
  const runnerText = configurationText(runnerMode)
  const readyRunnerRole = topology?.roles.find(
    (role) => ['executor', 'worker'].includes(role.role) && role.readyInstances > 0,
  )
  return [
    {
      id: 'database',
      title: 'Database',
      ready: databaseReady,
      detail: databaseReady
        ? `${String(readiness?.migrations_applied)} migrations applied`
        : readiness?.error || 'Database readiness has not been confirmed.',
    },
    {
      id: 'storage',
      title: 'Object storage',
      ready: storageText.length > 0,
      detail: storageText ? `${storageText.toUpperCase()} backend configured` : 'No object storage backend reported.',
    },
    {
      id: 'runner',
      title: 'Runner',
      ready: Boolean(readyRunnerRole) || runnerMode === 'local' || localRunner === true,
      detail: readyRunnerRole
        ? `${readyRunnerRole.role} service is ready.`
        : runnerMode === 'local' || localRunner === true
          ? 'Local process runner is available.'
        : `${runnerText || 'unknown'} runner requires its external infrastructure.`,
    },
    {
      id: 'authentication',
      title: 'Authentication',
      ready: Boolean(providers?.some((provider) => provider.interactive)),
      detail: providers?.length ? `${String(providers.length)} provider${providers.length === 1 ? '' : 's'} available` : 'No interactive provider reported.',
    },
  ]
}
