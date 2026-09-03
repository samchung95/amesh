import { autocompletion, type Completion, type CompletionContext } from '@codemirror/autocomplete'
import { yaml } from '@codemirror/lang-yaml'
import { setDiagnostics, type Diagnostic } from '@codemirror/lint'
import { Compartment, EditorState } from '@codemirror/state'
import { EditorView } from '@codemirror/view'
import { basicSetup } from 'codemirror'
import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react'

import type { FlowValidationIssue, JsonSchema } from '../../api/types'
import type { WorkflowEditorSchema } from './workflowEditorSchemaModel'

export interface FlowCodeEditorHandle {
  focusRange: (from: number, to: number) => void
}

interface FlowCodeEditorProps {
  value: string
  schema?: WorkflowEditorSchema
  issues: FlowValidationIssue[]
  onChange: (value: string) => void
}

function propertyCompletion(name: string, property: JsonSchema): Completion {
  const detail = Array.isArray(property.type) ? property.type.join(' | ') : property.type
  return {
    label: name,
    apply: `${name}: `,
    type: 'property',
    detail,
    info: property.description || property.title,
  }
}

// eslint-disable-next-line react-refresh/only-export-components
export function buildFlowCompletions(schema?: WorkflowEditorSchema): {
  properties: Completion[]
  resourceTypes: Completion[]
} {
  if (!schema) return { properties: [], resourceTypes: [] }
  const properties = Object.entries(schema.flowSchema.properties || {}).map(([name, value]) =>
    propertyCompletion(name, value),
  )
  for (const resource of schema.resourceCatalog.resources) {
    for (const [name, value] of Object.entries(resource.configurationSchema.properties || {})) {
      if (!properties.some((option) => option.label === name)) {
        properties.push(propertyCompletion(name, value))
      }
    }
  }
  const resourceTypes = schema.resourceCatalog.resources.map((resource) => ({
    label: resource.type,
    type: resource.kind === 'trigger' ? 'event' : 'class',
    detail: resource.editor.category,
    info: resource.editor.description || resource.editor.title,
  }))
  return { properties, resourceTypes }
}

function completionSource(schema?: WorkflowEditorSchema) {
  const options = buildFlowCompletions(schema)
  return (context: CompletionContext) => {
    const token = context.matchBefore(/[\w.-]*/)
    if (!token || (!context.explicit && token.from === token.to)) return null
    const linePrefix = context.state.sliceDoc(context.state.doc.lineAt(token.from).from, token.from)
    return {
      from: token.from,
      options: /\btype:\s*$/.test(linePrefix) ? options.resourceTypes : options.properties,
      validFor: /^[\w.-]*$/,
    }
  }
}

// eslint-disable-next-line react-refresh/only-export-components
export function validationDiagnostics(
  issues: FlowValidationIssue[],
  documentLength: number,
): Diagnostic[] {
  return issues.map((issue) => {
    const start = Math.max(0, Math.min(issue.sourceRange?.start.offset ?? 0, documentLength))
    const end = Math.max(start, Math.min(issue.sourceRange?.end.offset ?? start + 1, documentLength))
    return {
      from: start,
      to: end,
      severity: issue.severity === 'warning' ? 'warning' : 'error',
      message: issue.hint ? `${issue.message}\n${issue.hint}` : issue.message,
    }
  })
}

export const FlowCodeEditor = forwardRef<FlowCodeEditorHandle, FlowCodeEditorProps>(
  function FlowCodeEditor({ value, schema, issues, onChange }, forwardedRef) {
    const host = useRef<HTMLDivElement>(null)
    const view = useRef<EditorView | null>(null)
    const onChangeRef = useRef(onChange)
    const completion = useRef(new Compartment())

    useEffect(() => {
      onChangeRef.current = onChange
    }, [onChange])

    useEffect(() => {
      if (!host.current) return
      const editor = new EditorView({
        parent: host.current,
        state: EditorState.create({
          doc: value,
          extensions: [
            basicSetup,
            yaml(),
            EditorState.allowMultipleSelections.of(true),
            completion.current.of(autocompletion({ override: [completionSource(schema)] })),
            EditorView.lineWrapping,
            EditorView.updateListener.of((update) => {
              if (update.docChanged) onChangeRef.current(update.state.doc.toString())
            }),
          ],
        }),
      })
      editor.contentDOM.setAttribute('aria-label', 'Flow YAML source')
      editor.contentDOM.setAttribute('aria-multiline', 'true')
      view.current = editor
      return () => {
        view.current = null
        editor.destroy()
      }
      // EditorView owns its lifecycle; subsequent prop changes are dispatched below.
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    useEffect(() => {
      const editor = view.current
      if (!editor || editor.state.doc.toString() === value) return
      editor.dispatch({ changes: { from: 0, to: editor.state.doc.length, insert: value } })
    }, [value])

    useEffect(() => {
      const editor = view.current
      if (!editor) return
      editor.dispatch({
        effects: completion.current.reconfigure(
          autocompletion({ override: [completionSource(schema)] }),
        ),
      })
    }, [schema])

    useEffect(() => {
      const editor = view.current
      if (!editor) return
      editor.dispatch(setDiagnostics(
        editor.state,
        validationDiagnostics(issues, editor.state.doc.length),
      ))
    }, [issues, value])

    useImperativeHandle(forwardedRef, () => ({
      focusRange: (from, to) => {
        const editor = view.current
        if (!editor) return
        const start = Math.max(0, Math.min(from, editor.state.doc.length))
        const end = Math.max(start, Math.min(to, editor.state.doc.length))
        editor.dispatch({ selection: { anchor: start, head: end }, scrollIntoView: true })
        editor.focus()
      },
    }), [])

    return <div className="flow-code-editor" ref={host} />
  },
)
