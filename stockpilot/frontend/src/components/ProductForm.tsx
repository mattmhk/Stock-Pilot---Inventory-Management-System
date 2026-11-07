import { useState, type FormEvent } from 'react'
import { api, type Product } from '../lib/api'

interface ProductFormProps {
  /** Edit this product; omit to create a new one. */
  product?: Product
  onSaved: (product: Product) => void
  onCancel: () => void
}

export function ProductForm({ product, onSaved, onCancel }: ProductFormProps) {
  const editing = product !== undefined

  const [sku, setSku] = useState(product?.sku ?? '')
  const [name, setName] = useState(product?.name ?? '')
  const [quantity, setQuantity] = useState('0')
  const [reorderLevel, setReorderLevel] = useState(String(product?.reorder_level ?? 10))
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError(null)

    const fields = {
      sku: sku.trim(),
      name: name.trim(),
      reorder_level: Number(reorderLevel),
    }

    try {
      const saved = editing
        ? await api.updateProduct(product.id, fields)
        : await api.createProduct({ ...fields, quantity: Number(quantity) })
      onSaved(saved)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setSaving(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <label className="field">
        <span>SKU</span>
        <input
          value={sku}
          onChange={(e) => setSku(e.target.value)}
          placeholder="SKU-001"
          required
          autoFocus
        />
      </label>

      <label className="field">
        <span>Product name</span>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="USB-C Cable"
          required
        />
      </label>

      <div className="field-row">
        {!editing && (
          <label className="field">
            <span>Opening stock</span>
            <input
              type="number"
              min={0}
              step={1}
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
          </label>
        )}

        <label className="field">
          <span>Reorder level</span>
          <input
            type="number"
            min={0}
            step={1}
            value={reorderLevel}
            onChange={(e) => setReorderLevel(e.target.value)}
            required
          />
        </label>
      </div>

      {editing && (
        <p className="hint">Stock levels can only change through Stock In / Stock Out.</p>
      )}

      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : editing ? 'Save changes' : 'Add product'}
        </button>
      </div>
    </form>
  )
}
