import {
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react'

import type { FlowGraph } from '../api/types'
import { StatusBadge } from './StatusBadge'

function graphElements(graph: FlowGraph): { nodes: Node[]; edges: Edge[] } {
  const ranks = new Map<string, number>()
  const byId = new Map(graph.nodes.map((node) => [node.taskId, node]))
  const visiting = new Set<string>()
  const rank = (taskId: string): number => {
    const known = ranks.get(taskId)
    if (known !== undefined) return known
    if (visiting.has(taskId)) return 0
    visiting.add(taskId)
    const task = byId.get(taskId)
    const value = task?.dependencies.length
      ? 1 + Math.max(...task.dependencies.map((dependency) => rank(dependency)))
      : task?.depth || 0
    visiting.delete(taskId)
    ranks.set(taskId, value)
    return value
  }
  graph.nodes.forEach((node) => rank(node.taskId))
  return {
    nodes: graph.nodes.map((node) => ({
      id: node.taskId,
      position: { x: (ranks.get(node.taskId) || 0) * 280 + node.depth * 28, y: node.order * 112 },
      data: {
        label: (
          <div className="flow-graph-node-label">
            <span>{node.lifecyclePhase.replaceAll('_', ' ')}</span>
            <strong>{node.label}</strong>
            <code>{node.taskType}</code>
            <StatusBadge state={node.state || 'DEFINED'} />
          </div>
        ),
      },
      ariaLabel: `${node.label}, ${node.taskType}, ${node.lifecyclePhase.toLowerCase().replaceAll('_', ' ')}`,
    })),
    edges: graph.edges.map((edge, index) => ({
      id: `${edge.kind}:${edge.source}:${edge.target}:${String(index)}`,
      source: edge.source,
      target: edge.target,
      label: edge.kind === 'dependsOn' ? undefined : edge.kind,
      markerEnd: edge.kind === 'dependsOn' ? { type: MarkerType.ArrowClosed } : undefined,
      animated: edge.kind === 'dependsOn',
      className: `visual-edge-${edge.kind.toLowerCase()}`,
    })),
  }
}

export function FlowGraphView({ graph }: { graph: FlowGraph }) {
  const elements = graphElements(graph)
  return (
    <section className="data-section graph-section" aria-labelledby="flow-graph-title">
      <div className="section-heading">
        <div><p className="eyebrow">EXPANDED PLAN</p><h2 id="flow-graph-title">Workflow graph</h2></div>
        <span>{graph.nodes.length} nodes · {graph.edges.length} edges</span>
      </div>
      <div className="flow-graph-canvas" aria-label={`${graph.flowId} interactive workflow graph`}>
        <ReactFlow
          key={`${graph.namespace}:${graph.flowId}:${String(graph.revision)}`}
          defaultNodes={elements.nodes}
          defaultEdges={elements.edges}
          fitView
          nodesDraggable={false}
          nodesConnectable={false}
          nodesFocusable
          edgesFocusable
          minZoom={0.15}
          maxZoom={2}
          aria-label={`${graph.flowId} task and dependency graph`}
        >
          <MiniMap pannable zoomable ariaLabel={`${graph.flowId} graph mini map`} />
          <Controls showInteractive={false} />
          <Background variant={BackgroundVariant.Dots} gap={18} size={1} />
        </ReactFlow>
      </div>
    </section>
  )
}
