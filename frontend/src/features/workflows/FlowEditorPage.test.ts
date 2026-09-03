import { describe, expect, it } from 'vitest'
import { parse } from 'yaml'

import { cloneFlowDocument, flowDraftKey } from './FlowEditorPage'

describe('flow editor drafts and cloning', () => {
  it('isolates local drafts by tenant, principal and flow identity', () => {
    expect(flowDraftKey('tenant-a', 'user-1', 'team.data', 'daily')).toBe(
      'amesh.flow-draft.v1:tenant-a:user-1:team.data:daily',
    )
  })

  it('clones a canonical document under a new identity and initial revision', () => {
    const clone = parse(cloneFlowDocument({
      id: 'daily',
      namespace: 'team.data',
      revision: 8,
      tasks: [{ id: 'done', type: 'core.return' }],
    })) as Record<string, unknown>
    expect(clone).toMatchObject({ id: 'daily_copy', namespace: 'team.data', revision: 1 })
  })
})
