import { AlertTriangle, Inbox, LoaderCircle, RotateCcw } from 'lucide-react'
import { Component, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'

export function LoadingState({ label }: { label?: string }) {
  const { t } = useTranslation()
  return (
    <div className="state-panel state-loading" role="status" aria-live="polite">
      <LoaderCircle className="spin" size={24} aria-hidden="true" />
      <p>{label || t('loading')}</p>
    </div>
  )
}

export function ErrorState({ message, retry, actionLabel }: { message: string; retry: () => void; actionLabel?: string }) {
  const { t } = useTranslation()
  return (
    <div className="state-panel state-error" role="alert">
      <AlertTriangle size={24} aria-hidden="true" />
      <div>
        <h2>Unable to load this view</h2>
        <p>{message}</p>
      </div>
      <button className="button button-secondary" type="button" onClick={retry}>
        <RotateCcw size={17} aria-hidden="true" />
        {actionLabel || t('retry')}
      </button>
    </div>
  )
}

interface ChunkLoadErrorBoundaryProps {
  children: ReactNode
  message: string
  actionLabel: string
  onReload: () => void
  resetKey?: string
}

export class ChunkLoadErrorBoundary extends Component<ChunkLoadErrorBoundaryProps, { failed: boolean }> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidUpdate(previousProps: ChunkLoadErrorBoundaryProps) {
    if (previousProps.resetKey !== this.props.resetKey && this.state.failed) {
      this.setState({ failed: false })
    }
  }

  render() {
    if (this.state.failed) {
      return <ErrorState message={this.props.message} retry={this.props.onReload} actionLabel={this.props.actionLabel} />
    }
    return this.props.children
  }
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="state-panel state-empty">
      <Inbox size={28} aria-hidden="true" />
      <div>
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
    </div>
  )
}
