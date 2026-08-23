import { describe, expect, it } from 'vitest'

import {
  blueprintDraftTransferKey,
  onboardingProgressKey,
  onboardingReadiness,
  readOnboardingProgress,
} from './blueprintModel'

describe('blueprint onboarding model', () => {
  it('scopes draft and progress keys to the active user and tenant', () => {
    expect(blueprintDraftTransferKey('default', 'user-1', 'hello-world', '1.0.0')).toBe(
      'amesh.blueprint-draft.v1:default:user-1:hello-world:1.0.0',
    )
    expect(onboardingProgressKey('default', 'user-1')).toBe('amesh.onboarding.v1:default:user-1')
  })

  it('ignores malformed browser progress', () => {
    const storage = { getItem: () => '{bad json' } as Pick<Storage, 'getItem'> as Storage
    expect(readOnboardingProgress(storage, 'key')).toEqual([])
  })

  it('derives the four contributor readiness gates from server facts', () => {
    const checks = onboardingReadiness(
      { status: 'ready', version: 'test', database: 'ready', migrations_applied: 44, migrations_expected: 44, latest_migration: '0044', error: null },
      {
        schema_version: 1,
        version: 1,
        fingerprint: 'local',
        loaded_at: '2026-08-23T00:00:00Z',
        precedence: [],
        warnings: [],
        entries: [
          { name: 'object_storage_backend', value: 's3', source: 'default', reloadable: false, secret: false },
          { name: 'execution_runner_mode', value: 'local', source: 'environment', reloadable: false, secret: false },
        ],
      },
      [{ id: 'local', kind: 'LOCAL', display_name: 'Local', interactive: true }],
    )

    expect(checks.map((check) => check.id)).toEqual(['database', 'storage', 'runner', 'authentication'])
    expect(checks.every((check) => check.ready)).toBe(true)
  })
})
