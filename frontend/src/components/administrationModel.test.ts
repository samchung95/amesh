import { describe, expect, it } from 'vitest'

import type { AdministrationControl } from '../api/types'
import {
  administrationControlDraft,
  configurationValue,
  namespaceHierarchy,
  visibleConfiguration,
} from './administrationModel'

describe('administration model', () => {
  it('builds a dotted namespace hierarchy including inherited parents', () => {
    expect(namespaceHierarchy(['team.data.prod', 'team.ops'])).toEqual([
      { namespace: 'team', depth: 0, direct: false },
      { namespace: 'team.data', depth: 1, direct: false },
      { namespace: 'team.data.prod', depth: 2, direct: true },
      { namespace: 'team.ops', depth: 1, direct: true },
    ])
  })

  it('creates typed version-bound control drafts and rejects unsafe input', () => {
    const retention: AdministrationControl = {
      key: 'RETENTION', flagKey: 'admin-retention-executions', enabled: false,
      value: 30, version: 4, updatedBy: null, updatedAt: null,
    }
    expect(administrationControlDraft(retention, true, '90', 'extend recovery window')).toEqual({
      key: 'RETENTION', enabled: true, value: 90, reason: 'extend recovery window', expectedVersion: 4,
    })
    expect(() => administrationControlDraft(retention, true, '0', 'too small')).toThrow('between 1 and 3650')
  })

  it('keeps secret display redacted and filters configuration by provenance', () => {
    const entries = [
      { name: 'token', value: 'should-not-render', source: 'environment', reloadable: false, secret: true },
      { name: 'log_level', value: 'INFO', source: 'default', reloadable: true, secret: false },
    ]
    expect(configurationValue(entries[0])).toBe('[REDACTED]')
    expect(visibleConfiguration(entries, 'default')).toEqual([entries[1]])
  })
})
