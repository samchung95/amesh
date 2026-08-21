import { ArrowRight, GitBranch, Layers3 } from 'lucide-react'

import type { FlowGraph } from '../api/types'
import { StatusBadge } from './StatusBadge'

export function FlowGraphView({ graph }: { graph: FlowGraph }) {
  return (
    <section className="data-section graph-section" aria-labelledby="flow-graph-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">EXPANDED PLAN</p>
          <h2 id="flow-graph-title">Workflow graph</h2>
        </div>
        <span>{graph.nodes.length} nodes · {graph.edges.length} edges</span>
      </div>
      <div className="flow-graph" role="list" aria-label={`${graph.flowId} expanded workflow graph`}>
        {graph.nodes.map((node) => (
          <article
            className={`flow-node flow-node-depth-${String(Math.min(node.depth, 4))}`}
            key={node.taskId}
            role="listitem"
          >
            <span className="flow-node-order">{String(node.order + 1).padStart(2, '0')}</span>
            <div className="flow-node-body">
              <div className="flow-node-title">
                {node.mode ? <Layers3 size={16} aria-hidden="true" /> : <GitBranch size={16} aria-hidden="true" />}
                <strong>{node.taskId}</strong>
                <code>{node.taskType}</code>
              </div>
              <div className="flow-node-meta">
                {node.parentId ? <span>inside {node.parentId}</span> : <span>root</span>}
                {node.mode ? <span>{node.mode.toLowerCase()} · {node.failurePolicy.toLowerCase().replaceAll('_', ' ')}</span> : null}
                {node.maxConcurrency ? <span>limit {node.maxConcurrency}</span> : null}
              </div>
              {node.dependencies.length ? (
                <div className="flow-node-dependencies" aria-label="Dependencies">
                  {node.dependencies.map((dependency) => <span key={dependency}>{dependency}<ArrowRight size={13} aria-hidden="true" /></span>)}
                </div>
              ) : null}
            </div>
            <StatusBadge state={node.state || 'DEFINED'} />
          </article>
        ))}
      </div>
    </section>
  )
}
