import { describe, expect, it } from 'vitest'

import type { ExecutionDetail, HumanTask, PersistedExecution, WorkerInventory } from '../../api/types'
import { missionControlModel } from './missionControlModel'

const execution = (id: string, state: PersistedExecution['state']): PersistedExecution => ({
  execution_id: id, tenant_id: 'default', state, epoch: 1, version: 1, namespace: 'team.data', flow_id: `flow_${id}`, flow_revision: 3,
  inputs: {}, outputs: {}, labels: {}, trigger: { type: 'manual' }, created_by: 'operator', created_at: '2026-08-24T00:00:00Z', updated_at: '2026-08-24T00:01:00Z', timeout_at: null, cancel_deadline_at: null, lifecycle_evidence: {},
})

const details: Record<string, ExecutionDetail> = {
  run: { execution: execution('run', 'RUNNING'), taskRuns: [{ task_run_id: 'task-run', execution_id: 'run', task_id: 'transform', state: 'RUNNING', current_attempt: 1, version: 1, retry_at: null, result: null, iteration_key: null, labels: {}, failure_category: null, lifecycle_phase: 'MAIN', evidence: { workerGroup: 'local' } }], taskRunSummary: { total: 2, waiting: 1, running: 1, retry_delay: 0, succeeded: 0, failed: 0, cancelled: 0 }, taskRunOffset: 0 },
  failed: { execution: execution('failed', 'FAILED'), taskRuns: [{ task_run_id: 'task-failed', execution_id: 'failed', task_id: 'publish', state: 'FAILED', current_attempt: 2, version: 3, retry_at: null, result: null, iteration_key: null, labels: {}, failure_category: 'INFRASTRUCTURE', lifecycle_phase: 'MAIN', evidence: {} }], taskRunSummary: { total: 1, waiting: 0, running: 0, retry_delay: 0, succeeded: 0, failed: 1, cancelled: 0 }, taskRunOffset: 0 },
}

describe('missionControlModel', () => {
  it('projects active work, failures, approvals and degraded dependencies from server evidence', () => {
    const approval = { humanTaskId: 'approval-1', executionId: 'run', taskRunId: 'task-run', state: 'OPEN', title: 'Approve publication' } as HumanTask
    const worker = { worker_id: 'worker-1', worker_group: 'remote', instance_name: 'runner-1', liveness: 'STALE', compatibility: 'INCOMPATIBLE' } as WorkerInventory
    const model = missionControlModel({ executions: [execution('run', 'RUNNING'), execution('failed', 'FAILED'), execution('done', 'SUCCESS')], details, humanTasks: [approval], workers: [worker], admission: { active_reservations: 1, queued_requests: 2, oldest_queue_age_seconds: 8, pressure_by_policy: {} }, filters: { namespace: '', flowId: '', states: [] }, nowMs: new Date('2026-08-24T00:02:00Z').getTime() })
    expect(model.counts).toMatchObject({ running: 1, waitingApproval: 1, failedRecently: 1, completedRecently: 1 })
    expect(model.running[0]).toMatchObject({ progress: 0, workerGroup: 'local', trigger: 'manual', explanation: 'transform is running on local.' })
    expect(model.attention.map((item) => item.key)).toEqual(['approval:approval-1', 'failed:failed', 'worker:worker-1', 'admission:queue'])
  })

  it('applies namespace, flow and state filters before counting', () => {
    const model = missionControlModel({ executions: [execution('run', 'RUNNING'), execution('failed', 'FAILED')], details, humanTasks: [], workers: [], filters: { namespace: 'team.data', flowId: 'flow_failed', states: ['FAILED'] }, nowMs: new Date('2026-08-24T00:02:00Z').getTime() })
    expect(model.counts.failedRecently).toBe(1)
    expect(model.running).toEqual([])
    expect(model.attention[0].executionId).toBe('failed')
  })
})
