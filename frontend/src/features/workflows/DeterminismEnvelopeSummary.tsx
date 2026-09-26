import type { DeterminismEnvelope, DynamicExecutionBound } from '../../api/types'

interface Props {
  envelope: DeterminismEnvelope
  heading?: string
}

function boundDescription(bound: DynamicExecutionBound): string {
  const limits = [
    bound.maxIterations === null ? null : `${String(bound.maxIterations)} iterations`,
    bound.maxDurationSeconds === null ? null : `${String(bound.maxDurationSeconds)}s duration`,
    bound.maxTaskRuns === null ? null : `${String(bound.maxTaskRuns)} direct task runs`,
    bound.maxConcurrency === null ? null : `${String(bound.maxConcurrency)} concurrent`,
    bound.maxDepth === null ? null : `${String(bound.maxDepth)} levels`,
    bound.inlinePayloadBytes === null ? null : `${String(bound.inlinePayloadBytes)} inline bytes`,
  ].filter((item): item is string => item !== null)
  return limits.join(' · ')
}

export function DeterminismEnvelopeSummary({ envelope, heading = 'Runtime limits' }: Props) {
  return <section className="simulation-summary" aria-label={heading} title="Deterministic envelope">
    <strong>{heading}</strong>
    <dl>
      <div><dt>Flow version</dt><dd>r{envelope.revision}</dd></div>
      <div><dt>Maximum runs</dt><dd>{envelope.worstCaseTaskRuns}</dd></div>
      <div><dt>Task nesting</dt><dd>{envelope.configuredTaskNestingDepth} / {envelope.maximumTaskNestingDepth}</dd></div>
      <div><dt title="Policy pins">Policy versions</dt><dd>{envelope.policyPins.length || 'None'}</dd></div>
    </dl>
    <dl>
      <div><dt title="Semantic hash">Definition fingerprint</dt><dd><code>{envelope.semanticHash}</code></dd></div>
      <div><dt title="Plugin set hash">Plugin versions fingerprint</dt><dd><code>{envelope.pluginSetHash}</code></dd></div>
      <div><dt title="Envelope digest">Runtime limits fingerprint</dt><dd><code>{envelope.envelopeDigest}</code></dd></div>
    </dl>
    {envelope.policyPins.length ? <ul>
      {envelope.policyPins.map((pin) => <li key={`${pin.category}:${pin.key}:${String(pin.revision)}`}><strong>{pin.category}</strong> · {pin.key}{pin.revision === null ? '' : ` r${String(pin.revision)}`} · <code>{pin.digest}</code></li>)}
    </ul> : null}
    {envelope.dynamicBounds.length ? <>
      <strong>Dynamic limits</strong>
      <ul>
        {envelope.dynamicBounds.map((bound) => <li key={bound.taskId}><strong>{bound.taskId}</strong> · {bound.kind} · ≤ {bound.worstCaseTaskRuns} total runs<br /><small>{boundDescription(bound)}{bound.iterationKeyPattern ? ` · keys ${bound.iterationKeyPattern}` : ''}</small></li>)}
      </ul>
    </> : <p>No dynamic expansion in this version.</p>}
    {envelope.nondeterministicOperations.length ? <p><strong>External output boundary:</strong> {envelope.nondeterministicOperations.map((item) => `${item.taskId} (${item.taskType})`).join(', ')} require recorded version metadata or a recorded fixture for replay. Provider output itself is not claimed to be identical.</p> : <p>Every runnable output in this version is locally repeatable.</p>}
  </section>
}
