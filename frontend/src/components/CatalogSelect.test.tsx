import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { CatalogMultiSelect, CatalogSelect } from './CatalogSelect'

const options = [
  { value: 'examples.engine', label: 'Engine · examples.engine' },
  { value: 'examples.agent', label: 'Agent · examples.agent' },
]

describe('catalog selectors', () => {
  it('selects an authorized stable value by its human label', () => {
    const onChange = vi.fn()
    render(<CatalogSelect label="Namespace" value="" options={options} onChange={onChange} emptyLabel="All namespaces" />)
    fireEvent.change(screen.getByLabelText('Namespace'), { target: { value: 'examples.engine' } })
    expect(onChange).toHaveBeenCalledWith('examples.engine')
    expect(screen.getByRole('option', { name: 'Engine · examples.engine' })).toHaveValue('examples.engine')
  })

  it('reveals text entry only after the explicit custom path is selected', () => {
    const onChange = vi.fn()
    render(<CatalogSelect label="Package" value="" options={options} onChange={onChange} allowCustom required />)
    expect(screen.queryByLabelText('Package custom value')).not.toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Package'), { target: { value: '__amesh_custom_value__' } })
    expect(screen.getByLabelText('Package custom value')).toBeVisible()
  })

  it('uses ordinary checkboxes and removable chips for multiple values', () => {
    const onChange = vi.fn()
    render(<CatalogMultiSelect label="States" values={['examples.engine']} options={options} onChange={onChange} />)
    fireEvent.click(screen.getByRole('button', { name: 'Remove Engine · examples.engine' }))
    expect(onChange).toHaveBeenCalledWith([])
  })
})
