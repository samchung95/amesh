import { describe, expect, it } from 'vitest'

import type { SearchDocument } from '../../api/types'
import { parseSearchPairs, searchResultPath, searchTypeLabel } from './searchModel'

const document: SearchDocument = {
  documentType: 'FLOW',
  documentId: 'flow-uuid',
  namespace: 'team.data',
  title: 'team.data.daily',
  summary: 'Daily flow',
  state: 'ACTIVE',
  labels: {},
  fields: { flowId: 'daily' },
  occurredAt: '2026-08-23T00:00:00Z',
  updatedAt: '2026-08-23T00:00:00Z',
  sourceVersion: 2,
  relevance: 1,
}

describe('search model', () => {
  it('parses only complete structured pairs', () => {
    expect(parseSearchPairs('team=platform, env = prod, invalid, empty=')).toEqual({
      team: 'platform',
      env: 'prod',
    })
  })

  it('maps every projected resource to its public route', () => {
    expect(searchResultPath(document)).toBe('/flows/team.data/daily')
    expect(searchResultPath({ ...document, documentType: 'EXECUTION', fields: { executionId: 'run/1' } })).toBe('/executions/run%2F1')
    expect(searchResultPath({ ...document, documentType: 'TASK_RUN', fields: { executionId: 'run-1' } })).toBe('/executions/run-1')
    expect(searchResultPath({ ...document, documentType: 'LOG', fields: { executionId: 'run-1' } })).toBe('/executions/run-1?view=logs')
    expect(searchResultPath({ ...document, documentType: 'METRIC', fields: { executionId: 'run-1' } })).toBe('/executions/run-1')
    expect(searchResultPath({ ...document, documentType: 'ASSET' })).toBe('/assets?asset=flow-uuid')
    expect(searchResultPath({ ...document, documentType: 'AUDIT' })).toBe('/administration?view=audit&event=flow-uuid')
  })

  it('provides readable labels for all document types', () => {
    expect(['FLOW', 'EXECUTION', 'TASK_RUN', 'LOG', 'METRIC', 'ASSET', 'AUDIT'].map((type) => searchTypeLabel(type as never))).toEqual([
      'Flow', 'Execution', 'Task run', 'Log', 'Metric', 'Asset', 'Audit',
    ])
  })
})
