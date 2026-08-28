import { describe, expect, it } from 'vitest'

import type { ExecutionEvidenceEvent, PersistedExecution, PersistedTaskRun } from '../api/types'
import {
  buildGanttAttempts,
  EVIDENCE_BUFFER_LIMIT,
  filterLogs,
  frozenReplaySource,
  logsFromEvidence,
  mergeEvidence,
  permittedActions,
} from './executionDebugModel'

const execution: PersistedExecution = {
  execution_id: 'execution-1', tenant_id: 'default', state: 'SUCCESS', epoch: 1, version: 4,
  namespace: 'examples', flow_id: 'debug', flow_revision: 3,
  inputs: { name: 'Ada' }, outputs: { message: 'done' }, labels: { team: 'data' },
  trigger: { type: 'manual' }, created_by: 'operator',
  created_at: '2026-08-23T00:00:00Z', updated_at: '2026-08-23T00:00:10Z',
  timeout_at: null, cancel_deadline_at: null, lifecycle_evidence: {},
}

const task: PersistedTaskRun = {
  task_run_id: 'task-run-1', execution_id: execution.execution_id, task_id: 'extract',
  state: 'SUCCESS', current_attempt: 1, version: 3, retry_at: null,
  result: { rows: 4 }, iteration_key: null, labels: {}, failure_category: null,
  lifecycle_phase: 'MAIN', evidence: {},
}

function event(
  cursor: number,
  eventType: string,
  occurredAt: string,
  payload: Record<string, unknown> = {},
  kind: ExecutionEvidenceEvent['kind'] = 'STATE',
): ExecutionEvidenceEvent {
  return {
    cursor, event_id: `event-${String(cursor)}`, execution_id: execution.execution_id,
    task_run_id: kind === 'STATE' || kind === 'LOG' ? task.task_run_id : null,
    kind, event_type: eventType.toLocaleLowerCase(),
    payload: kind === 'STATE' ? { entity: 'task', eventType, payload } : payload,
    occurred_at: occurredAt, ingested_at: occurredAt,
  }
}

describe('execution debug model', () => {
  it('derives queue and runner timing from durable task state events', () => {
    const attempts = buildGanttAttempts(execution, [task], [
      event(1, 'TaskRunCreated', '2026-08-23T00:00:01Z'),
      event(2, 'TaskRunStarted', '2026-08-23T00:00:03Z', { workerGroup: 'local' }),
      event(3, 'TaskRunSucceeded', '2026-08-23T00:00:08Z'),
    ])

    expect(attempts).toHaveLength(1)
    expect(attempts[0]).toMatchObject({ taskId: 'extract', attempt: 1, queueMs: 2_000, runnerMs: 5_000, worker: 'local' })
  })

  it('filters streamed logs by task, attempt, level, worker, time and text', () => {
    const logs = logsFromEvidence([
      event(4, 'log.info', '2026-08-23T00:00:05Z', { level: 'INFO', attempt: 1, workerId: 'worker-a', message: 'loaded rows', fields: { count: 4 } }, 'LOG'),
      event(5, 'log.error', '2026-08-23T00:00:06Z', { level: 'ERROR', attempt: 1, workerId: 'worker-b', message: 'failed' }, 'LOG'),
    ], [task])

    expect(filterLogs(logs, { task: 'extract', attempt: '1', level: 'INFO', worker: 'worker-a', from: '2026-08-23T00:00:04Z', to: '2026-08-23T00:00:06Z', text: 'count' })).toHaveLength(1)
  })

  it('exposes only state-valid lifecycle actions', () => {
    expect(permittedActions('RUNNING').map((item) => item.action)).toEqual(['PAUSE', 'REQUEST_CANCEL'])
    expect(permittedActions('CANCELLING')).toEqual([{ label: 'Kill', action: 'FORCE_CANCEL' }])
    expect(permittedActions('SUCCESS')).toEqual([{ label: 'Restart', action: 'RESTART' }])
  })

  it('attests frozen replay inputs and exact source pins', async () => {
    const source = {
      ...execution,
      trigger: {
        type: 'manual',
        _ameshDeterminism: {
          schemaVersion: 'amesh.determinism-envelope/v1', revision: 3,
          semanticHash: 'a'.repeat(64), pluginSetHash: 'b'.repeat(64), envelopeDigest: 'c'.repeat(64),
          policyPins: [{ category: 'ADMISSION', key: 'approved', revision: 2, digest: 'd'.repeat(64) }],
          nodes: [], dynamicBounds: [], maximumTaskNestingDepth: 16, configuredTaskNestingDepth: 1,
          worstCaseTaskRuns: 1, nondeterministicOperations: [],
        },
      },
    }

    await expect(frozenReplaySource(source)).resolves.toEqual({
      sourceExecutionId: 'execution-1',
      frozenInputDigest: 'sha256:88bab6d8f6dc68a877064d584cbb5b6c50e74f617ea50d81d3a53c2ee6ffbc4f',
      resourcePins: [
        { key: 'flow', revision: 3, digest: 'a'.repeat(64) },
        { key: 'plugin-set', revision: 3, digest: 'b'.repeat(64) },
        { key: 'determinism-envelope', revision: 3, digest: 'c'.repeat(64) },
        { key: 'ADMISSION:approved', revision: 2, digest: 'd'.repeat(64) },
      ],
    })
  })

  it('keeps a bounded, ordered evidence window at 100,000 events', () => {
    const started = performance.now()
    const events = Array.from({ length: 100_000 }, (_, index) => event(index + 1, 'TaskRunStarted', '2026-08-23T00:00:01Z'))
    const merged = mergeEvidence([], events)
    const elapsed = performance.now() - started

    expect(merged).toHaveLength(EVIDENCE_BUFFER_LIMIT)
    expect(merged[0].cursor).toBe(95_001)
    expect(merged.at(-1)?.cursor).toBe(100_000)
    expect(elapsed).toBeLessThan(1_000)
  })
})
