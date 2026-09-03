import { describe, expect, it } from 'vitest'

import type {
  ExecutionEvidenceEvent,
  FlowGraph,
  HumanTask,
  PersistedSubflow,
  PersistedTaskRun,
} from '../../api/types'
import { buildExecutionTrace } from './executionTraceModel'

const executionId = 'execution-1'

function task(id: string, state: PersistedTaskRun['state'], extras: Partial<PersistedTaskRun> = {}): PersistedTaskRun {
  return {
    task_run_id: `run-${id}-${extras.iteration_key ?? '0'}`,
    execution_id: executionId,
    task_id: id,
    state,
    current_attempt: 1,
    version: 1,
    retry_at: null,
    result: null,
    iteration_key: null,
    labels: {},
    failure_category: null,
    lifecycle_phase: 'MAIN',
    evidence: {},
    ...extras,
  }
}

function event(cursor: number, taskRunId: string, eventType: string, payload: Record<string, unknown> = {}): ExecutionEvidenceEvent {
  const occurredAt = `2026-08-24T00:00:${String(cursor).padStart(2, '0')}Z`
  return { cursor, event_id: `event-${String(cursor)}`, execution_id: executionId, task_run_id: taskRunId, kind: 'STATE', event_type: eventType.toLocaleLowerCase(), payload: { entity: 'task', eventType, payload }, occurred_at: occurredAt, ingested_at: occurredAt }
}

const graph: FlowGraph = {
  namespace: 'team.data',
  flowId: 'publish',
  revision: 7,
  nodes: [
    { taskId: 'prepare', label: 'Prepare', taskType: 'core.return', order: 0, depth: 0, parentId: null, branchId: null, dependencies: [], children: [], mode: null, failurePolicy: 'FAIL_FAST', maxConcurrency: null, state: null, result: null, iterationCount: null, lifecyclePhase: 'MAIN', handlerOwnerId: null },
    { taskId: 'branch', label: 'Choose destination', taskType: 'core.if', order: 1, depth: 0, parentId: null, branchId: null, dependencies: ['prepare'], children: [], mode: 'DAG', failurePolicy: 'FAIL_FAST', maxConcurrency: null, state: null, result: null, iterationCount: null, lifecyclePhase: 'MAIN', handlerOwnerId: null },
    { taskId: 'loop', label: 'Publish item', taskType: 'core.foreach', order: 2, depth: 0, parentId: null, branchId: null, dependencies: ['branch'], children: [], mode: 'FOREACH', failurePolicy: 'FAIL_FAST', maxConcurrency: 2, state: null, result: null, iterationCount: 2, lifecyclePhase: 'MAIN', handlerOwnerId: null },
    { taskId: 'review', label: 'Review', taskType: 'core.approval', order: 3, depth: 0, parentId: null, branchId: null, dependencies: ['loop'], children: [], mode: null, failurePolicy: 'FAIL_FAST', maxConcurrency: null, state: null, result: null, iterationCount: null, lifecyclePhase: 'MAIN', handlerOwnerId: null },
    { taskId: 'not_selected', label: 'Unused destination', taskType: 'core.return', order: 4, depth: 1, parentId: 'branch', branchId: 'else', dependencies: ['branch'], children: [], mode: null, failurePolicy: 'FAIL_FAST', maxConcurrency: null, state: null, result: null, iterationCount: null, lifecyclePhase: 'MAIN', handlerOwnerId: null },
  ],
  edges: [],
}

describe('buildExecutionTrace', () => {
  it('orders success, conditional, loop, retry and failure evidence as a readable run story', () => {
    const prepare = task('prepare', 'SUCCESS', { result: { recordCount: 2 } })
    const branch = task('branch', 'SUCCESS', { evidence: { control: { branch: { selectedBranch: 'then' } } } })
    const loopA = task('loop', 'SUCCESS', { iteration_key: '0' })
    const loopB = task('loop', 'RETRY_DELAY', { iteration_key: '1', current_attempt: 2, retry_at: '2026-08-24T00:02:00Z' })
    const review = task('review', 'FAILED', { failure_category: 'CONFIGURATION' })
    const notSelected = task('not_selected', 'SUCCESS', { current_attempt: 0, result: { skipped: true, reason: "conditional branch 'then' selected" }, evidence: { control: { branch: 'else', selectedBranch: 'then' } } })
    const evidence = [
      event(1, prepare.task_run_id, 'TaskRunStarted', { workerGroup: 'local' }),
      event(2, prepare.task_run_id, 'TaskRunSucceeded'),
      event(3, branch.task_run_id, 'BranchEvaluated'),
      event(4, loopB.task_run_id, 'TaskRunRetryScheduled'),
      event(5, review.task_run_id, 'TaskRunFailed'),
    ]
    const model = buildExecutionTrace({ taskRuns: [review, loopB, prepare, loopA, branch, notSelected], evidence, graph, subflows: [], humanTasks: [], interventions: [], nowMs: Date.parse('2026-08-24T00:01:00Z') })

    expect(model.groups.map((group) => group.label)).toEqual(['Prepare', 'Choose destination', 'Publish item · 2 iterations', 'Review', '1 non-selected branch step'])
    expect(model.groups[1].steps[0].annotations).toContain('Decision: Branch Evaluated')
    expect(model.groups[1].steps[0].context).toContain('Selected path then')
    expect(model.groups[2].collapsible).toBe(true)
    expect(model.groups[2].steps[1]).toMatchObject({ attempt: 2, outcome: 'Retry at 2026-08-24T00:02:00Z' })
    expect(model.groups[3].steps[0].outcome).toBe('Failed: CONFIGURATION')
    expect(model.groups[0].steps[0].outcome).toBe('Completed with recordCount')
    expect(model.groups[4]).toMatchObject({ collapsible: true, steps: [{ nonSelected: true, outcome: "Not run: conditional branch 'then' selected" }] })
    expect(model.groups[4].steps[0].context).toContain('Branch else')
  })

  it('places approval and subflow context inline without exposing form values', () => {
    const review = task('review', 'WAITING')
    const approval: HumanTask = { humanTaskId: 'approval-1', namespace: 'team.data', executionId, taskRunId: review.task_run_id, attempt: 1, title: 'Approve release', description: '', form: { fields: [], layout: [] }, assigneeIds: [], groupIds: [], deadlineAt: null, state: 'OPEN', version: 1, createdAt: '2026-08-24T00:00:00Z', decidedBy: null, decidedAt: null, reason: '', formValues: { secret: 'must-not-appear' }, actions: [] }
    const subflow: PersistedSubflow = { relationship_id: 'relationship-1', parent_execution_id: executionId, parent_task_run_id: review.task_run_id, parent_attempt: 1, child_execution_id: 'child-1', invocation_key: 'child', mode: 'SYNC', depth: 1, target_revision: 3, parent_namespace: 'team.data', parent_flow_id: 'publish', parent_flow_revision: 7, child_namespace: 'team.data', child_flow_id: 'notify', child_state: 'RUNNING', created_by: 'executor', created_at: '2026-08-24T00:00:01Z', propagation: { cancellation: true, failure: true, pause: true, restart: true, success: true } }
    const model = buildExecutionTrace({ taskRuns: [review], evidence: [], graph, subflows: [subflow], humanTasks: [approval], interventions: [{ sequence: 1, action: 'PAUSE', event_type: 'ExecutionPaused', actor_id: 'operator', reason: 'investigating', occurred_at: '2026-08-24T00:00:02Z', payload: {} }], nowMs: Date.parse('2026-08-24T00:01:00Z') })
    const step = model.groups[0].steps[0]

    expect(step.outcome).toBe('Waiting for approval: Approve release')
    expect(step.annotations).toContain('Approve release: open')
    expect(step.childExecutions).toEqual([subflow])
    expect(JSON.stringify(model)).not.toContain('must-not-appear')
    expect(model.runAnnotations).toEqual(['pause by operator: investigating'])
  })

  it('bounds large traces while retaining stable graph order', () => {
    const model = buildExecutionTrace({ taskRuns: [task('review', 'WAITING'), task('prepare', 'SUCCESS'), task('branch', 'SUCCESS')], evidence: [], graph, subflows: [], humanTasks: [], interventions: [], nowMs: 0, limit: 2 })
    expect(model.groups.map((group) => group.steps[0].taskId)).toEqual(['prepare', 'branch'])
    expect(model).toMatchObject({ total: 3, hidden: 1 })
  })

  it('renders bounded agent phases, budgets, tool policy and output gates inline', () => {
    const agent = task('agent', 'SUCCESS', { result: { result: { answer: 'done' } } })
    const agentEvent = (cursor: number, eventType: string, payload: Record<string, unknown>): ExecutionEvidenceEvent => {
      const occurredAt = `2026-08-24T00:01:${String(cursor).padStart(2, '0')}Z`
      return { cursor, event_id: `agent-event-${String(cursor)}`, execution_id: executionId, task_run_id: agent.task_run_id, kind: 'STATE', event_type: eventType, payload: { entity: 'agentSession', payload }, occurred_at: occurredAt, ingested_at: occurredAt }
    }
    const evidence = [
      agentEvent(1, 'agent.session.started', { envelopeDigest: `sha256:${'1'.repeat(64)}`, memoryReads: [{ key: 'prior' }] }),
      agentEvent(2, 'agent.model.response', { turn: 1, action: 'tool', counters: { totalTokens: 18, costUsd: '0.002' } }),
      agentEvent(3, 'agent.policy.authorized', { tool: 'lookup', impact: 'HIGH_IMPACT', approval: { required: true, decision: 'APPROVED' } }),
      agentEvent(4, 'agent.tool.result', { tool: 'lookup', toolCalls: 1 }),
      agentEvent(5, 'agent.evaluation.completed', { key: 'quality', passed: true, deterministic: { rubricScore: '1' }, judge: { score: '0.9', uncertainty: '0.1' } }),
      agentEvent(6, 'agent.release.approved', { approvalTask: 'approve' }),
      agentEvent(7, 'agent.memory.written', { key: 'latest', scope: 'PRIVATE' }),
      agentEvent(8, 'agent.output.accepted', { businessAssertionsPassed: 2 }),
    ]
    const model = buildExecutionTrace({ taskRuns: [agent], evidence, subflows: [], humanTasks: [], interventions: [], nowMs: Date.parse('2026-08-24T00:02:00Z') })
    const annotations = model.groups[0].steps[0].annotations

    expect(annotations).toContain('Model turn 1 · proposed tool · 18 tokens · $0.002')
    expect(annotations).toContain('Tool authorized: lookup · HIGH_IMPACT · approval APPROVED')
    expect(annotations).toContain('Tool completed: lookup · call 1')
    expect(annotations).toContain('Evaluation quality passed · deterministic score 1 · judge 0.9 ± 0.1')
    expect(annotations).toContain('Human release approved · approve')
    expect(annotations).toContain('Memory written: latest · PRIVATE')
    expect(annotations).toContain('Output accepted · schema valid · 2 business gates')
  })

  it('renders routing, typed hand-offs and mesh budgets as a readable story', () => {
    const route = task('route', 'SUCCESS')
    const handoff = task('handoff', 'SUCCESS')
    const mesh = task('mesh', 'SUCCESS')
    const evidence = [
      event(1, route.task_run_id, 'TaskRunSucceeded', { agentRoute: { selectedMemberId: 'analyst', selectedAgent: 'incident-helper', selectedAgentRevision: 3 } }),
      event(2, handoff.task_run_id, 'TaskRunSucceeded', { agentHandoff: { source: { task: 'analyst-session' }, destination: { task: 'supervisor-session' }, context: { finding: 'validated' }, policy: { outcome: 'ALLOW' } } }),
      event(3, mesh.task_run_id, 'TaskRunSucceeded', { agentMesh: { topology: 'SUPERVISOR', usage: { sessions: 2, totalTokens: 828, costUsd: '0.0005' } } }),
    ]

    const model = buildExecutionTrace({ taskRuns: [route, handoff, mesh], evidence, subflows: [], humanTasks: [], interventions: [], nowMs: 0 })

    expect(model.groups[2].steps[0].annotations).toContain('Routed to analyst · incident-helper@3')
    expect(model.groups[0].steps[0].annotations).toContain('Hand-off analyst-session → supervisor-session · 1 context fields · policy ALLOW')
    expect(model.groups[1].steps[0].annotations).toContain('Mesh SUPERVISOR completed · 2 sessions · 828 tokens · $0.0005')
  })
})
