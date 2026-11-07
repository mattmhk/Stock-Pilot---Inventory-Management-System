import { useState, type FormEvent } from 'react'
import { api, type MovementType, type Product } from '../lib/api'
import { formatNumber } from '../lib/stock'

interface StockMovementFormProps {
  product: Product
  type: MovementType
  onSaved: () => void
  onCancel: () => void
}

export function StockMovementForm({ product, type, onSaved, onCancel }: StockMovementFormProps) {
  const [quantity, setQuantity] = useState('1')
  const [note, setNote] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const amount = Number(quantity)
  const valid = Number.isInteger(amount) && amount > 0
  const after = type === 'IN' ? product.quantity + amount : product.quantity - amount
  const exceedsStock = type === 'OUT' && valid && amount > product.quantity

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError(null)

    try {
      await api.createStockMovement({
        product_id: product.id,
        movement_type: type,
        quantity: amount,
        note: note.trim() || null,
      })
      onSaved()
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
        <span>Quantity {type === 'IN' ? 'received' : 'removed'}</span>
        <input
          type="number"
          min={1}
          max={type === 'OUT' ? product.quantity : undefined}
          step={1}
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
          autoFocus
        />
      </label>

      <label className="field">
        <span>Note (optional)</span>
        <input
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder={type === 'IN' ? 'Supplier delivery' : 'Customer order'}
        />
      </label>

      <div className={`preview ${exceedsStock ? 'preview-error' : ''}`}>
        {exceedsStock ? (
          <>Only {formatNumber(product.quantity)} in stock.</>
        ) : (
          <>
            Stock: {formatNumber(product.quantity)} →{' '}
            <strong>{valid ? formatNumber(after) : '—'}</strong>
          </>
        )}
      </div>

      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel}>
          Cancel
        </button>
        <button
          type="submit"
          className={`btn ${type === 'IN' ? 'btn-in' : 'btn-out'}`}
          disabled={saving || !valid || exceedsStock}
        >
          {saving ? 'Saving…' : type === 'IN' ? 'Record stock in' : 'Record stock out'}
        </button>
      </div>
    </form>
  )
}
