import { useMemo, useState, type FormEvent } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Check, Clock3, ExternalLink, LayoutGrid, MessageSquareText, Play, RefreshCw, X } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import type { AppForm, AppFormField, HumanTask, HumanTaskActionKind, UiSession, WorkflowApp } from '../api/types'
import { formatDate } from '../app/format'
import { useApiClient, useHumanTasks, useWorkflowApp, useWorkflowApps } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { EmptyState, ErrorState, LoadingState } from '../components/AsyncState'

function initialValues(form: AppForm): Record<string, unknown> {
  return Object.fromEntries(form.fields.flatMap((field) => field.default === null || field.default === undefined ? [] : [[field.id, field.default]]))
}

function parseField(field: AppFormField, value: string | boolean): unknown {
  if (field.type === 'checkbox') return Boolean(value)
  if (field.type === 'number') return value === '' ? undefined : Number(value)
  if (field.type === 'json') return value === '' ? undefined : JSON.parse(String(value)) as unknown
  if (field.type === 'select') {
    const option = field.options.find((candidate) => JSON.stringify(candidate) === value)
    return option === undefined ? value : option
  }
  return value
}

function DynamicForm({ form, values, onChange, disabled = false }: { form: AppForm; values: Record<string, unknown>; onChange: (values: Record<string, unknown>) => void; disabled?: boolean }) {
  const fields = useMemo(() => new Map(form.fields.map((field) => [field.id, field])), [form.fields])
  const sections = form.layout.length ? form.layout : [{ title: 'Inputs', helpText: '', columns: 1, fields: form.fields.map((field) => field.id) }]
  return <div className="app-form-sections">{sections.map((section) => <fieldset key={section.title} className={`app-form-grid columns-${String(section.columns)}`}><legend>{section.title}</legend>{section.helpText ? <p>{section.helpText}</p> : null}{section.fields.map((fieldId) => {
    const field = fields.get(fieldId)
    if (!field) return null
    const current = values[field.id]
    const update = (raw: string | boolean) => onChange({ ...values, [field.id]: parseField(field, raw) })
    return <label key={field.id}>{field.label}{field.required ? <span aria-hidden="true"> *</span> : null}
      {field.type === 'checkbox' ? <input type="checkbox" checked={Boolean(current)} onChange={(event) => update(event.target.checked)} disabled={disabled} />
        : field.type === 'select' ? <select value={current === undefined ? '' : JSON.stringify(current)} onChange={(event) => update(event.target.value)} required={field.required} disabled={disabled}><option value="">Select…</option>{field.options.map((option) => <option key={JSON.stringify(option)} value={JSON.stringify(option)}>{String(option)}</option>)}</select>
          : field.type === 'json' ? <textarea value={current === undefined ? '' : typeof current === 'string' ? current : JSON.stringify(current, null, 2)} onChange={(event) => onChange({ ...values, [field.id]: event.target.value })} required={field.required} disabled={disabled} spellCheck={false} />
            : <input type={field.type} value={typeof current === 'string' || typeof current === 'number' ? current : ''} placeholder={field.placeholder || ''} onChange={(event) => update(event.target.value)} required={field.required} disabled={disabled} />}
      {field.helpText ? <small>{field.helpText}</small> : null}</label>
  })}</fieldset>)}</div>
}

export function AppsPage({ session, embedded = false }: { session: UiSession; embedded?: boolean }) {
  const { namespace, appId } = useParams()
  const apps = useWorkflowApps(!appId)
  const selected = useWorkflowApp(namespace, appId)
  const tasks = useHumanTasks(!embedded && session.capabilities['humanTasks.view'])
  const { settings } = useAppSettings()

  if (embedded) return <main className="app-embed"><AppLaunch app={selected.data} pending={selected.isPending} error={selected.error} retry={() => void selected.refetch()} /></main>

  return <div className="page-stack">
    <header className="page-heading"><div><p className="eyebrow">BUILD / PARTICIPATE</p><h1>{appId ? selected.data?.title || 'Workflow app' : 'Apps & approvals'}</h1><p>{appId ? selected.data?.description || 'A permission-scoped form backed by a pinned workflow revision.' : 'Launch curated workflows and respond to durable human tasks.'}</p></div>{appId ? <Link className="button button-secondary" to="/apps"><ArrowLeft size={17} />All apps</Link> : <button className="button button-secondary" type="button" onClick={() => { void apps.refetch(); void tasks.refetch() }}><RefreshCw size={17} />Refresh</button>}</header>
    {appId ? <AppLaunch app={selected.data} pending={selected.isPending} error={selected.error} retry={() => void selected.refetch()} /> : <AppCatalog apps={apps.data} pending={apps.isPending} error={apps.error} retry={() => void apps.refetch()} />}
    {session.capabilities['humanTasks.view'] ? <ApprovalInbox session={session} /> : null}
    {!appId && !apps.isPending && !apps.error && !apps.data?.length && !tasks.data?.length ? <EmptyState title="No apps or approvals yet" body="Create an app through the API for a versioned flow, or add a core.approval task to a workflow." /> : null}
    <span className="sr-only">Workspace timezone {settings.timezone}</span>
  </div>
}

function AppCatalog({ apps, pending, error, retry }: { apps: WorkflowApp[] | undefined; pending: boolean; error: Error | null; retry: () => void }) {
  if (pending) return <LoadingState label="Loading workflow apps" />
  if (error) return <ErrorState message={error.message} retry={retry} />
  if (!apps?.length) return null
  return <section><div className="section-heading"><div><p className="eyebrow">CURATED ENTRY POINTS</p><h2>Workflow apps</h2></div><span>{apps.length} available</span></div><div className="app-card-grid">{apps.map((app) => <Link key={`${app.namespace}/${app.appId}`} className="app-card panel" to={`/apps/${encodeURIComponent(app.namespace)}/${encodeURIComponent(app.appId)}`}><span className="app-card-icon"><LayoutGrid size={20} /></span><div><p className="eyebrow">{app.namespace} · REV {app.revision}</p><h3>{app.title}</h3><p>{app.description || `Launch ${app.flowId} revision ${String(app.flowRevision)}.`}</p></div><ExternalLink size={17} /></Link>)}</div></section>
}

function AppLaunch({ app, pending, error, retry }: { app: WorkflowApp | undefined; pending: boolean; error: Error | null; retry: () => void }) {
  if (pending) return <LoadingState label="Loading app form" />
  if (error) return <ErrorState message={error.message} retry={retry} />
  if (!app) return null
  return <AppLaunchForm key={`${app.namespace}/${app.appId}/${String(app.revision)}`} app={app} />
}

function AppLaunchForm({ app }: { app: WorkflowApp }) {
  const api = useApiClient()
  const [values, setValues] = useState<Record<string, unknown>>(() => initialValues(app.form))
  const [failure, setFailure] = useState('')
  const launch = useMutation({ mutationFn: (inputs: Record<string, unknown>) => api.launchApp(app.namespace, app.appId, inputs) })
  const submit = (event: FormEvent) => {
    event.preventDefault()
    setFailure('')
    try {
      const parsed = { ...values }
      for (const field of app.form.fields) {
        if (field.type === 'json' && typeof parsed[field.id] === 'string') parsed[field.id] = parseField(field, parsed[field.id] as string)
      }
      launch.mutate(parsed)
    } catch (caught) { setFailure(caught instanceof Error ? caught.message : 'Form values are invalid.') }
  }
  return <section className="app-launch panel"><header><div><p className="eyebrow">{app.namespace} / {app.flowId} @ {app.flowRevision}</p><h2>{app.title}</h2></div><span>App revision {app.revision}</span></header><form onSubmit={submit}><DynamicForm form={app.form} values={values} onChange={setValues} disabled={launch.isPending} /><button className="button button-primary" type="submit" disabled={launch.isPending}><Play size={17} />{launch.isPending ? 'Launching…' : app.launchLabel}</button>{failure || launch.error ? <p className="resource-failure" role="alert">{failure || launch.error?.message}</p> : null}{launch.data ? <p className="resource-notice" role="status">Execution accepted. <Link to={`/executions/${launch.data.execution.execution_id}`}>Open execution</Link></p> : null}</form></section>
}

function ApprovalInbox({ session }: { session: UiSession }) {
  const tasks = useHumanTasks()
  const { settings } = useAppSettings()
  const [selectedId, setSelectedId] = useState('')
  const selected = tasks.data?.find((task) => task.humanTaskId === selectedId) || tasks.data?.find((task) => task.state === 'OPEN' || task.state === 'ESCALATED')
  if (tasks.isPending) return <LoadingState label="Loading approval inbox" />
  if (tasks.error) return <ErrorState message={tasks.error.message} retry={() => void tasks.refetch()} />
  if (!tasks.data?.length) return null
  const open = tasks.data.filter((task) => task.state === 'OPEN' || task.state === 'ESCALATED')
  return <section><div className="section-heading"><div><p className="eyebrow">HUMAN TASKS</p><h2>Approval inbox</h2></div><span>{open.length} waiting</span></div><div className="approval-layout"><div className="approval-list panel">{tasks.data.map((task) => <button key={task.humanTaskId} type="button" className={selected?.humanTaskId === task.humanTaskId ? 'selected' : ''} onClick={() => setSelectedId(task.humanTaskId)}><span data-state={task.state}>{task.state.replace('_', ' ')}</span><strong>{task.title}</strong><small>{task.namespace}{task.deadlineAt ? ` · due ${formatDate(task.deadlineAt, settings.locale, settings.timezone)}` : ''}</small></button>)}</div>{selected ? <ApprovalDetail key={selected.humanTaskId} selected={selected} session={session} /> : null}</div></section>
}

function ApprovalDetail({ selected, session }: { selected: HumanTask; session: UiSession }) {
  const api = useApiClient()
  const queryClient = useQueryClient()
  const { settings } = useAppSettings()
  const [reason, setReason] = useState('')
  const [comment, setComment] = useState('')
  const [values, setValues] = useState<Record<string, unknown>>(() => initialValues(selected.form))
  const act = useMutation({
    mutationFn: ({ action }: { action: HumanTaskActionKind }) => api.actOnHumanTask(selected.humanTaskId, action, { reason, comment, formValues: values }),
    onSuccess: async () => { setReason(''); setComment(''); await queryClient.invalidateQueries({ queryKey: ['human-tasks'] }) },
  })
  return <article className="approval-detail panel"><header><div><p className="eyebrow">{selected.namespace} · ATTEMPT {selected.attempt}</p><h3>{selected.title}</h3></div><span data-state={selected.state}>{selected.state.replace('_', ' ')}</span></header><p>{selected.description || 'No additional approval instructions.'}</p><DynamicForm form={selected.form} values={values} onChange={setValues} disabled={!['OPEN', 'ESCALATED'].includes(selected.state)} /><label>Decision reason<textarea value={reason} onChange={(event) => setReason(event.target.value)} disabled={!['OPEN', 'ESCALATED'].includes(selected.state)} /></label><label>Participant comment<textarea value={comment} onChange={(event) => setComment(event.target.value)} /></label>{['OPEN', 'ESCALATED'].includes(selected.state) && session.capabilities['humanTasks.update'] ? <div className="approval-actions"><button className="button button-primary" type="button" onClick={() => act.mutate({ action: 'APPROVE' })}><Check size={17} />Approve</button><button className="button button-secondary" type="button" onClick={() => act.mutate({ action: 'REQUEST_CHANGES' })}><MessageSquareText size={17} />Request changes</button><button className="button button-danger" type="button" onClick={() => act.mutate({ action: 'REJECT' })}><X size={17} />Reject</button></div> : null}{comment ? <button className="button button-ghost" type="button" onClick={() => act.mutate({ action: 'COMMENT' })}>Add comment</button> : null}{selected.deadlineAt ? <small className="approval-deadline"><Clock3 size={14} />Deadline {formatDate(selected.deadlineAt, settings.locale, settings.timezone)}</small> : null}{act.error ? <p className="resource-failure" role="alert">{act.error.message}</p> : null}</article>
}
