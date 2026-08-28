import { AlertTriangle, Inbox, LoaderCircle, RotateCcw } from 'lucide-react'
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

export function ErrorState({ message, retry }: { message: string; retry: () => void }) {
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
        {t('retry')}
      </button>
    </div>
  )
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
