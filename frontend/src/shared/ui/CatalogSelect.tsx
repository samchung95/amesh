import { useId, useState } from 'react'

export interface CatalogOption {
  value: string
  label: string
  description?: string
}

interface CatalogSelectProps {
  label: string
  value: string
  options: CatalogOption[]
  onChange: (value: string) => void
  emptyLabel?: string
  required?: boolean
  disabled?: boolean
  loading?: boolean
  allowCustom?: boolean
  customLabel?: string
  helpText?: string
  className?: string
}

const CUSTOM_VALUE = '__amesh_custom_value__'

export function CatalogSelect({
  label,
  value,
  options,
  onChange,
  emptyLabel = 'All',
  required = false,
  disabled = false,
  loading = false,
  allowCustom = false,
  customLabel = 'Enter a custom value',
  helpText,
  className,
}: CatalogSelectProps) {
  const id = useId()
  const knownValue = options.some((option) => option.value === value)
  const [customMode, setCustomMode] = useState(allowCustom && Boolean(value) && !knownValue)
  const showCustom = allowCustom && !knownValue && (customMode || Boolean(value))

  return (
    <label className={className || 'catalog-select'} htmlFor={id}>
      <span>{label}</span>
      {helpText ? <small>{helpText}</small> : null}
      <select
        id={id}
        aria-label={label}
        value={showCustom ? CUSTOM_VALUE : value}
        required={required && !showCustom}
        disabled={disabled || loading}
        onChange={(event) => {
          if (event.target.value === CUSTOM_VALUE) {
            setCustomMode(true)
            onChange('')
          } else {
            setCustomMode(false)
            onChange(event.target.value)
          }
        }}
      >
        <option value="">{loading ? 'Loading authorized options…' : emptyLabel}</option>
        {options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        {allowCustom ? <option value={CUSTOM_VALUE}>{customLabel}</option> : null}
      </select>
      {showCustom ? <input aria-label={`${label} custom value`} value={value} required={required} onChange={(event) => onChange(event.target.value)} /> : null}
      {!loading && !options.length ? <small>No authorized options are available.</small> : null}
    </label>
  )
}

interface CatalogMultiSelectProps {
  label: string
  values: string[]
  options: CatalogOption[]
  onChange: (values: string[]) => void
  emptyLabel?: string
  className?: string
}

export function CatalogMultiSelect({ label, values, options, onChange, emptyLabel = 'Any value', className }: CatalogMultiSelectProps) {
  const id = useId()
  const toggle = (value: string) => onChange(values.includes(value) ? values.filter((item) => item !== value) : [...values, value])
  return (
    <fieldset className={className || 'catalog-multiselect'}>
      <legend>{label}</legend>
      <details>
        <summary id={id}>{values.length ? `${String(values.length)} selected` : emptyLabel}</summary>
        <div className="catalog-option-list" aria-labelledby={id}>
          {options.length ? options.map((option) => (
            <label key={option.value}>
              <input type="checkbox" checked={values.includes(option.value)} onChange={() => toggle(option.value)} />
              <span><strong>{option.label}</strong>{option.description ? <small>{option.description}</small> : null}</span>
            </label>
          )) : <p>No authorized options are available.</p>}
        </div>
      </details>
      {values.length ? <div className="catalog-chips" aria-label={`${label} selected values`}>{values.map((value) => {
        const option = options.find((item) => item.value === value)
        return <button key={value} type="button" onClick={() => toggle(value)} aria-label={`Remove ${option?.label || value}`}>{option?.label || value}<span aria-hidden="true">×</span></button>
      })}</div> : null}
    </fieldset>
  )
}
