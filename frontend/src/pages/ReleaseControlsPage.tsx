import {
  AlertTriangle,
  GitPullRequest,
  History,
  OctagonX,
  RefreshCw,
  RotateCcw,
  ShieldCheck,
} from 'lucide-react'
import { type FormEvent, useMemo, useState } from 'react'

import { ApiError } from '../api/client'
import type {
  PromotionGate,
  PromotionTargetKind,
  ReleaseHistoryEntry,
  ReleaseTarget,
  UiSession,
} from '../api/types'
import { formatDate } from '../app/format'
import { useApiClient } from '../app/queries'
import { useAppSettings } from '../app/settings'
import { EmptyState, LoadingState } from '../components/AsyncState'
import { StatusBadge } from '../components/StatusBadge'

type RecoveryAction = 'rollback' | 'kill-switch'

export function ReleaseControlsPage({ session }: { session: UiSession }) {
  const api = useApiClient()
  const { settings } = useAppSettings()
  const [targetKind, setTargetKind] = useState<PromotionTargetKind>('WORKFLOW')
  const [targetKey, setTargetKey] = useState('')
  const [policyId, setPolicyId] = useState('')
  const [target, setTarget] = useState<ReleaseTarget | null>(null)
  const [history, setHistory] = useState<ReleaseHistoryEntry[]>([])
  const [gate, setGate] = useState<PromotionGate | null>(null)
  const [reason, setReason] = useState('')
  const [recoveryReason, setRecoveryReason] = useState('')
  const [rollbackRevision, setRollbackRevision] = useState('')
  const [pendingRecovery, setPendingRecovery] = useState<RecoveryAction | null>(null)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [failure, setFailure] = useState('')

  const canManage = session.capabilities['releases.manage']
  const rollbackOptions = useMemo(
    () => Array.from(new Set(
      history
        .map((event) => event.toRevision)
        .filter((revision): revision is number => revision !== null && revision !== target?.activeRevision),
    )).sort((left, right) => right - left),
    [history, target?.activeRevision],
  )

  const loadTarget = async (kind: PromotionTargetKind, key: string) => {
    setBusy(true)
    setFailure('')
    try {
      const [nextTarget, nextHistory] = await Promise.all([
        api.releaseTarget(kind, key),
        api.releaseHistory(kind, key),
      ])
      setTarget(nextTarget)
      setHistory(nextHistory)
      const options = nextHistory
        .map((event) => event.toRevision)
        .filter((revision): revision is number => revision !== null && revision !== nextTarget.activeRevision)
        .sort((left, right) => right - left)
      setRollbackRevision(options[0] ? String(options[0]) : '')
    } catch (error) {
      setTarget(null)
      setHistory([])
      setRollbackRevision('')
      setFailure(error instanceof ApiError && error.status === 404
        ? 'No release record exists for this target yet. Preview a policy before its first promotion.'
        : error instanceof Error ? error.message : 'Could not load release state.')
    } finally {
      setBusy(false)
    }
  }

  const inspectTarget = async (event: FormEvent) => {
    event.preventDefault()
    const key = targetKey.trim()
    if (!key) return
    setNotice('')
    await loadTarget(targetKind, key)
  }

  const previewPolicy = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setNotice('')
    setFailure('')
    try {
      const preview = await api.previewRelease(policyId.trim())
      setGate(preview)
      setTargetKind(preview.targetKind)
      setTargetKey(preview.targetKey)
      setNotice(preview.passed
        ? `Gate passed for ${preview.targetKind.toLowerCase()} revision ${String(preview.targetRevision)}.`
        : 'Gate blocked promotion. Review the evidence failures below.')
      await loadTarget(preview.targetKind, preview.targetKey)
    } catch (error) {
      setGate(null)
      setFailure(error instanceof Error ? error.message : 'Could not preview this policy.')
      setBusy(false)
    }
  }

  const applyPolicy = async (event: FormEvent) => {
    event.preventDefault()
    if (!gate?.passed || !canManage) return
    setBusy(true)
    setNotice('')
    setFailure('')
    try {
      const result = await api.applyRelease(policyId.trim(), target?.version ?? 0, reason.trim())
      setTarget(result.target)
      setHistory((current) => [result.event, ...current])
      setReason('')
      setGate(null)
      setNotice(`Revision ${String(result.target.activeRevision)} is active at version ${String(result.target.version)}.`)
    } catch (error) {
      setFailure(error instanceof Error ? error.message : 'Could not apply this release policy.')
    } finally {
      setBusy(false)
    }
  }

  const confirmRecovery = async () => {
    if (!target || !pendingRecovery || !canManage) return
    setBusy(true)
    setNotice('')
    setFailure('')
    try {
      const result = pendingRecovery === 'rollback'
        ? await api.rollbackRelease(
            target.targetKind,
            target.targetKey,
            Number(rollbackRevision),
            target.version,
            recoveryReason.trim(),
          )
        : await api.killSwitchRelease(
            target.targetKind,
            target.targetKey,
            target.version,
            recoveryReason.trim(),
          )
      setTarget(result.target)
      setHistory((current) => [result.event, ...current])
      setPendingRecovery(null)
      setRecoveryReason('')
      setNotice(pendingRecovery === 'rollback'
        ? `Rolled back to exact revision ${String(result.target.activeRevision)}.`
        : 'Kill switch activated; this target is no longer active.')
    } catch (error) {
      setFailure(error instanceof Error ? error.message : 'Could not apply the recovery action.')
      setPendingRecovery(null)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page-stack release-page">
      <header className="page-heading resource-heading">
        <div>
          <p className="eyebrow">GOVERN / EVIDENCE GATES</p>
          <h1>Releases</h1>
          <p>Preview evidence before promotion, then recover an exact recorded revision without changing client policy.</p>
        </div>
        <span className="admin-boundary"><ShieldCheck size={16} aria-hidden="true" />{canManage ? 'Release manager' : 'Preview only'} · {settings.tenant}</span>
      </header>

      {notice ? <p className="inline-notice" role="status">{notice}</p> : null}
      {failure ? <p className="form-error" role="alert">{failure}</p> : null}

      <section className="data-section" aria-labelledby="release-target-heading">
        <div className="section-heading">
          <div><p className="eyebrow">TARGET / CURRENT STATE</p><h2 id="release-target-heading">Inspect a release target</h2></div>
          {target ? <StatusBadge state={target.state} /> : null}
        </div>
        <form className="admin-form release-target-form" onSubmit={(event) => void inspectTarget(event)}>
          <label>Target type<select value={targetKind} onChange={(event) => setTargetKind(event.target.value as PromotionTargetKind)}><option value="WORKFLOW">Workflow</option><option value="AGENT">Agent</option></select></label>
          <label>Stable target key<input value={targetKey} onChange={(event) => setTargetKey(event.target.value)} placeholder="namespace.resource" required /></label>
          <button className="button button-secondary" type="submit" disabled={busy || !targetKey.trim()}><RefreshCw className={busy ? 'spin' : ''} size={17} aria-hidden="true" />Inspect target</button>
        </form>
        {busy && !target && !gate ? <LoadingState label="Loading release state" /> : null}
        {target ? <dl className="release-facts" aria-label="Current release state"><div><dt>State</dt><dd>{target.state}</dd></div><div><dt>Active revision</dt><dd>{target.activeRevision ?? 'none'}</dd></div><div><dt>Concurrency version</dt><dd>{target.version}</dd></div><div><dt>Updated</dt><dd>{formatDate(target.updatedAt, settings.locale, settings.timezone)}</dd></div><div className="span-two"><dt>Configuration digest</dt><dd><code>{target.activeConfigurationDigest || 'none'}</code></dd></div></dl> : null}
      </section>

      <div className="release-columns">
        <section className="data-section" aria-labelledby="release-preview-heading">
          <div className="section-heading"><div><p className="eyebrow">STEP 1 / READ-ONLY</p><h2 id="release-preview-heading">Preview policy gate</h2></div><GitPullRequest size={20} aria-hidden="true" /></div>
          <p className="section-copy">Use the immutable policy ID returned when the client created its release contract. Preview never changes the target.</p>
          <form className="admin-form release-policy-form" onSubmit={(event) => void previewPolicy(event)}>
            <label className="span-two">Policy ID<input value={policyId} onChange={(event) => setPolicyId(event.target.value)} placeholder="00000000-0000-0000-0000-000000000000" required /></label>
            <button className="button button-secondary" type="submit" disabled={busy || !policyId.trim()}>Preview evidence</button>
          </form>
          {gate ? <div className={gate.passed ? 'release-gate release-gate-pass' : 'release-gate release-gate-fail'} aria-live="polite">
            <header><div><strong>{gate.passed ? 'Gate passed' : 'Promotion blocked'}</strong><small>{gate.targetKind} · {gate.targetKey} · revision {gate.targetRevision}</small></div><StatusBadge state={gate.passed ? 'PASS' : 'FAILED'} /></header>
            <dl><div><dt>Evidence</dt><dd>{gate.evidenceDigests.length} immutable digests</dd></div><div><dt>Evaluated</dt><dd>{formatDate(gate.evaluatedAt, settings.locale, settings.timezone)}</dd></div></dl>
            {gate.failures.length ? <ul>{gate.failures.map((item) => <li key={item}>{item}</li>)}</ul> : <p>All pinned evidence, health, budget and approval requirements passed.</p>}
          </div> : <EmptyState title="No gate preview" body="Enter a policy ID to evaluate fresh evidence without changing a release." />}
        </section>

        <section className="data-section" aria-labelledby="release-apply-heading">
          <div className="section-heading"><div><p className="eyebrow">STEP 2 / MUTATION</p><h2 id="release-apply-heading">Apply passing gate</h2></div><ShieldCheck size={20} aria-hidden="true" /></div>
          {!canManage ? <EmptyState title="Preview-only access" body="A release.manage permission is required to promote, roll back or activate the kill switch." /> : null}
          {canManage ? <form className="admin-form release-policy-form" onSubmit={(event) => void applyPolicy(event)}>
            <label className="span-two">Change reason<textarea value={reason} onChange={(event) => setReason(event.target.value)} minLength={3} placeholder="Why this exact revision is ready" required /></label>
            <div className="release-version-note"><span>Expected version</span><strong>{target?.version ?? 0}</strong><small>Reload after any concurrency conflict.</small></div>
            <button className="button button-primary" type="submit" disabled={busy || !gate?.passed || reason.trim().length < 3}>Apply promotion</button>
          </form> : null}
          {canManage && !gate?.passed ? <p className="admin-safety-note"><ShieldCheck size={17} aria-hidden="true" />A passing preview is required before Apply is enabled.</p> : null}
        </section>
      </div>

      <section className="data-section release-recovery" aria-labelledby="release-recovery-heading">
        <div className="section-heading"><div><p className="eyebrow">RECOVERY / EXACT HISTORY</p><h2 id="release-recovery-heading">Rollback or stop</h2></div><AlertTriangle size={20} aria-hidden="true" /></div>
        <p className="section-copy">Recovery uses the loaded target version. Every successful action appends immutable history and rejects stale concurrent changes.</p>
        <form className="admin-form" onSubmit={(event) => event.preventDefault()}>
          <label>Prior revision<select value={rollbackRevision} onChange={(event) => setRollbackRevision(event.target.value)} disabled={!rollbackOptions.length}><option value="">No prior revision</option>{rollbackOptions.map((revision) => <option key={revision} value={revision}>Revision {revision}</option>)}</select></label>
          <label className="span-two">Recovery reason<input value={recoveryReason} onChange={(event) => setRecoveryReason(event.target.value)} minLength={3} placeholder="Incident or rollback decision" /></label>
          <button className="button button-secondary" type="button" disabled={!canManage || busy || !target || !rollbackRevision || recoveryReason.trim().length < 3} onClick={() => setPendingRecovery('rollback')}><RotateCcw size={17} aria-hidden="true" />Rollback revision</button>
          <button className="button button-danger" type="button" disabled={!canManage || busy || !target || target.state === 'KILLED' || recoveryReason.trim().length < 3} onClick={() => setPendingRecovery('kill-switch')}><OctagonX size={17} aria-hidden="true" />Activate kill switch</button>
        </form>
      </section>

      <section className="data-section" aria-labelledby="release-history-heading">
        <div className="section-heading"><div><p className="eyebrow">AUDIT / APPEND-ONLY</p><h2 id="release-history-heading">Release history</h2></div><span className="result-count"><History size={15} aria-hidden="true" />{history.length} events</span></div>
        {!history.length ? <EmptyState title="No recorded release actions" body="Inspect a promoted target or apply its first passing gate." /> : <div className="table-shell"><table><thead><tr><th>Version</th><th>Action</th><th>Revision</th><th>Reason</th><th>Actor</th><th>Time</th></tr></thead><tbody>{history.map((event) => <tr key={event.eventId}><td><strong>v{event.version}</strong></td><td><StatusBadge state={event.action} /></td><td>{event.fromRevision ?? 'none'} → {event.toRevision ?? 'stopped'}</td><td>{event.reason}</td><td><code>{event.actorId}</code></td><td><time dateTime={event.occurredAt}>{formatDate(event.occurredAt, settings.locale, settings.timezone)}</time></td></tr>)}</tbody></table></div>}
      </section>

      {pendingRecovery && target ? <div className="modal-backdrop"><section className="confirmation-dialog admin-impact-dialog" role="dialog" aria-modal="true" aria-labelledby="release-confirm-title"><p className="eyebrow">EXACT TARGET / VERSION {target.version}</p><h2 id="release-confirm-title">Confirm {pendingRecovery === 'rollback' ? `rollback to revision ${rollbackRevision}` : 'kill switch'}</h2><p>This changes <code>{target.targetKind}:{target.targetKey}</code> and records the reason “{recoveryReason.trim()}”.</p><div><button className="button button-secondary" type="button" onClick={() => setPendingRecovery(null)}>Cancel</button><button className="button button-danger" type="button" disabled={busy} onClick={() => void confirmRecovery()}>{pendingRecovery === 'rollback' ? 'Confirm rollback' : 'Confirm kill switch'}</button></div></section></div> : null}
    </div>
  )
}
