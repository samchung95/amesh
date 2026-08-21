import { Construction, LockKeyhole } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export function PlaceholderPage({ title, denied = false }: { title: string; denied?: boolean }) {
  const { t } = useTranslation()
  const Icon = denied ? LockKeyhole : Construction
  return (
    <div className="page-stack">
      <header className="page-heading"><div><p className="eyebrow">WORKSPACE / RESERVED</p><h1>{title}</h1></div></header>
      <section className="reserved-panel"><Icon size={32} aria-hidden="true" /><p className="eyebrow">{denied ? 'POLICY / DENIED' : 'CAPABILITY / RESERVED'}</p><h2>{denied ? 'Permission required' : t('unavailableTitle')}</h2><p>{denied ? t('permissionDenied') : t('unavailableBody')}</p></section>
    </div>
  )
}
