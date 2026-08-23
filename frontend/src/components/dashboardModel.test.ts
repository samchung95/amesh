import { describe, expect, it } from 'vitest'

import { buildDashboardSpec, dashboardFilters, displayValue, normalizedChartValues, parsePairs, rowLabel } from './dashboardModel'

describe('dashboard model', () => {
  it('builds bounded typed queries with all operational filters', () => {
    const filters = dashboardFilters({
      hours: 24,
      namespace: 'team.data',
      flowId: 'daily',
      states: 'SUCCESS, FAILED',
      workerGroups: 'cpu',
      labels: 'team=platform,env=prod',
      dimensions: 'region=apac',
    }, new Date('2026-08-23T12:00:00Z'))
    const spec = buildDashboardSpec({
      dashboardId: 'ops.daily', title: 'Daily operations', description: '', visibility: 'TENANT',
      viewerIds: 'viewer-a', editorIds: 'editor-a', widgetTitle: 'Duration', source: 'EXECUTIONS',
      visualization: 'DISTRIBUTION', measure: 'DURATION_MS', aggregation: 'P95', groupBy: 'state,label.team',
      limit: 900, timeoutMs: 9000, sampleRate: 0,
    }, filters)
    expect(spec.widgets[0].query.filters).toEqual(filters)
    expect(spec.widgets[0].query.limit).toBe(500)
    expect(spec.widgets[0].query.timeoutMs).toBe(5000)
    expect(spec.widgets[0].query.sampleRate).toBe(0.01)
    expect(spec.viewerIds).toEqual(['viewer-a'])
  })

  it('rejects arbitrary dimensions and malformed key-value filters', () => {
    expect(() => parsePairs('broken')).toThrow(/key=value/)
    expect(() => buildDashboardSpec({
      dashboardId: 'ops', title: 'Ops', description: '', visibility: 'PRIVATE', viewerIds: '', editorIds: '',
      widgetTitle: 'Unsafe', source: 'EXECUTIONS', visualization: 'COUNTER', measure: 'COUNT', aggregation: 'COUNT',
      groupBy: 'sql.drop', limit: 100, timeoutMs: 1000, sampleRate: 1,
    }, {})).toThrow(/Unsupported dimensions/)
  })

  it('normalizes chart values and derives accessible labels', () => {
    expect(normalizedChartValues([{ value: 5 }, { value: 10 }])).toEqual([0.5, 1])
    expect(rowLabel({ state: 'FAILED', value: 2 })).toBe('FAILED')
    expect(displayValue({ region: 'apac' })).toBe('{"region":"apac"}')
  })
})
