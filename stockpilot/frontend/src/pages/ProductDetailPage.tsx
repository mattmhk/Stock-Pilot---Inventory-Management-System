import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { api, ApiError, type MovementType } from '../lib/api'
import { formatDateTime, formatNumber } from '../lib/stock'
import { useApi } from '../lib/useApi'
import { Modal } from '../components/Modal'
import { ProductForm } from '../components/ProductForm'
import { StatusBadge } from '../components/StatusBadge'
import { StockMovementForm } from '../components/StockMovementForm'
import { EmptyState, ErrorMessage, Loading } from '../components/States'
import { NotFoundPage } from './NotFoundPage'

type Dialog = { kind: 'movement'; type: MovementType } | { kind: 'edit' } | { kind: 'delete' } | null

export function ProductDetailPage() {
  const id = Number(useParams().id)
  const navigate = useNavigate()
  const [dialog, setDialog] = useState<Dialog>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  const product = useApi(() => api.getProduct(id), [id])
  const movements = useApi(() => api.getProductMovements(id), [id])

  function close() {
    setDialog(null)
    setDeleteError(null)
  }

  function refresh() {
    close()
    product.reload()
    movements.reload()
  }

  async function handleDelete() {
    setDeleting(true)
    try {
      await api.deleteProduct(id)
      navigate('/products', { replace: true })
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Something went wrong')
      setDeleting(false)
    }
  }

  if (!Number.isInteger(id) || (product.error instanceof ApiError && product.error.status === 404)) {
    return <NotFoundPage message="This product doesn't exist or was deleted." />
  }

  if (product.error) return <ErrorMessage error={product.error} onRetry={product.reload} />
  if (!product.data) return <Loading label="Loading product…" />

  const p = product.data

  return (
    <>
      <Link to="/products" className="back-link">
        ← Products
      </Link>

      <div className="page-header">
        <div>
          <h1>{p.name}</h1>
          <p className="subtle mono">{p.sku}</p>
        </div>
        <div className="actions">
          <button type="button" className="btn" onClick={() => setDialog({ kind: 'edit' })}>
            Edit
          </button>
          <button type="button" className="btn btn-danger-ghost" onClick={() => setDialog({ kind: 'delete' })}>
            Delete
          </button>
        </div>
      </div>

      <section className="card detail">
        <dl className="detail-stats">
          <div>
            <dt>Current stock</dt>
            <dd className="detail-value">{formatNumber(p.quantity)}</dd>
          </div>
          <div>
            <dt>Reorder level</dt>
            <dd className="detail-value">{formatNumber(p.reorder_level)}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>
              <StatusBadge product={p} />
            </dd>
          </div>
        </dl>

        <div className="actions">
          <button
            type="button"
            className="btn btn-in"
            onClick={() => setDialog({ kind: 'movement', type: 'IN' })}
          >
            + Stock in
          </button>
          <button
            type="button"
            className="btn btn-out"
            disabled={p.quantity === 0}
            title={p.quantity === 0 ? 'Nothing in stock to remove' : undefined}
            onClick={() => setDialog({ kind: 'movement', type: 'OUT' })}
          >
            − Stock out
          </button>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <h2>Movement history</h2>
        </div>

        {movements.error ? (
          <ErrorMessage error={movements.error} onRetry={movements.reload} />
        ) : !movements.data ? (
          <Loading />
        ) : movements.data.length === 0 ? (
          <EmptyState title="No stock movements yet">
            <p>Deliveries and orders you record will appear here.</p>
          </EmptyState>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th className="num">Quantity</th>
                  <th>Note</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {movements.data.map((movement) => (
                  <tr key={movement.id}>
                    <td>
                      <span className={`badge badge-${movement.movement_type === 'IN' ? 'in' : 'outflow'}`}>
                        {movement.movement_type}
                      </span>
                    </td>
                    <td className={`num delta-${movement.movement_type === 'IN' ? 'in' : 'out'}`}>
                      {movement.movement_type === 'IN' ? '+' : '−'}
                      {formatNumber(movement.quantity)}
                    </td>
                    <td>{movement.note ?? <span className="subtle">—</span>}</td>
                    <td className="subtle nowrap">{formatDateTime(movement.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {dialog?.kind === 'movement' && (
        <Modal title={dialog.type === 'IN' ? 'Stock in' : 'Stock out'} onClose={close}>
          <StockMovementForm product={p} type={dialog.type} onSaved={refresh} onCancel={close} />
        </Modal>
      )}

      {dialog?.kind === 'edit' && (
        <Modal title="Edit product" onClose={close}>
          <ProductForm product={p} onSaved={refresh} onCancel={close} />
        </Modal>
      )}

      {dialog?.kind === 'delete' && (
        <Modal title="Delete product?" onClose={close}>
          <div className="form">
            {deleteError && (
              <div className="alert alert-error" role="alert">
                {deleteError}
              </div>
            )}
            <p>
              <strong>{p.name}</strong> and its entire movement history will be permanently deleted.
            </p>
            <div className="form-actions">
              <button type="button" className="btn" onClick={close}>
                Cancel
              </button>
              <button type="button" className="btn btn-danger" disabled={deleting} onClick={handleDelete}>
                {deleting ? 'Deleting…' : 'Delete product'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </>
  )
}
