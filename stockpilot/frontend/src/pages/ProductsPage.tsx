import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import { api, type ProductFilters } from '../lib/api'
import { formatNumber } from '../lib/stock'
import { useApi, useDebouncedValue } from '../lib/useApi'
import { Modal } from '../components/Modal'
import { ProductForm } from '../components/ProductForm'
import { StatusBadge } from '../components/StatusBadge'
import { EmptyState, ErrorMessage, Loading } from '../components/States'

type StatusFilter = 'all' | 'good' | 'low' | 'out'

const STATUS_OPTIONS: { value: StatusFilter; label: string }[] = [
  { value: 'all', label: 'All statuses' },
  { value: 'good', label: 'In stock' },
  { value: 'low', label: 'Low stock' },
  { value: 'out', label: 'Out of stock' },
]

function toNumber(value: string): number | undefined {
  return value === '' ? undefined : Number(value)
}

export function ProductsPage() {
  const navigate = useNavigate()
  // Filters live in the URL so they survive refreshes and can be linked to
  const [params, setParams] = useSearchParams()
  const [adding, setAdding] = useState(false)

  const search = params.get('search') ?? ''
  const status = (params.get('status') as StatusFilter | null) ?? 'all'
  const minQuantity = params.get('min') ?? ''
  const maxQuantity = params.get('max') ?? ''

  function setParam(key: string, value: string) {
    setParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        if (value === '' || (key === 'status' && value === 'all')) next.delete(key)
        else next.set(key, value)
        return next
      },
      { replace: true },
    )
  }

  const debouncedSearch = useDebouncedValue(search.trim())

  const filters: ProductFilters = {
    search: debouncedSearch || undefined,
    min_quantity: toNumber(minQuantity),
    max_quantity: status === 'out' ? 0 : toNumber(maxQuantity),
    low_stock: status === 'low' ? true : status === 'good' ? false : undefined,
  }
  const filterKey = JSON.stringify(filters)

  const products = useApi(() => api.getProducts(filters), [filterKey])
  const hasFilters = search !== '' || status !== 'all' || minQuantity !== '' || maxQuantity !== ''

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Products</h1>
          <p className="subtle">
            {products.data ? `${formatNumber(products.data.length)} shown` : 'Your product catalogue.'}
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setAdding(true)}>
          + Add product
        </button>
      </div>

      <section className="card">
        <div className="toolbar">
          <input
            type="search"
            className="input search"
            placeholder="Search by name or SKU…"
            aria-label="Search products"
            value={search}
            onChange={(e) => setParam('search', e.target.value)}
          />

          <select
            className="input"
            aria-label="Stock status"
            value={status}
            onChange={(e) => setParam('status', e.target.value)}
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <div className="range">
            <input
              type="number"
              min={0}
              className="input"
              placeholder="Min qty"
              aria-label="Minimum quantity"
              value={minQuantity}
              onChange={(e) => setParam('min', e.target.value)}
            />
            <span aria-hidden="true">–</span>
            <input
              type="number"
              min={0}
              className="input"
              placeholder="Max qty"
              aria-label="Maximum quantity"
              value={status === 'out' ? '0' : maxQuantity}
              disabled={status === 'out'}
              onChange={(e) => setParam('max', e.target.value)}
            />
          </div>

          {hasFilters && (
            <button type="button" className="btn btn-ghost" onClick={() => setParams({}, { replace: true })}>
              Clear
            </button>
          )}
        </div>

        {products.error ? (
          <ErrorMessage error={products.error} onRetry={products.reload} />
        ) : products.loading && !products.data ? (
          <Loading label="Loading products…" />
        ) : products.data && products.data.length === 0 ? (
          hasFilters ? (
            <EmptyState title="No products match these filters">
              <button type="button" className="btn" onClick={() => setParams({}, { replace: true })}>
                Clear filters
              </button>
            </EmptyState>
          ) : (
            <EmptyState title="No products yet">
              <p>Add your first product to start tracking stock.</p>
              <button type="button" className="btn btn-primary" onClick={() => setAdding(true)}>
                + Add product
              </button>
            </EmptyState>
          )
        ) : (
          <div className={`table-wrap ${products.loading ? 'is-refreshing' : ''}`}>
            <table className="table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Product</th>
                  <th className="num">Stock</th>
                  <th className="num">Reorder at</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {products.data?.map((product) => (
                  <tr key={product.id}>
                    <td className="mono">{product.sku}</td>
                    <td>
                      <Link to={`/products/${product.id}`} className="row-link">
                        {product.name}
                      </Link>
                    </td>
                    <td className="num">{formatNumber(product.quantity)}</td>
                    <td className="num">{formatNumber(product.reorder_level)}</td>
                    <td>
                      <StatusBadge product={product} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {adding && (
        <Modal title="Add product" onClose={() => setAdding(false)}>
          <ProductForm
            onCancel={() => setAdding(false)}
            onSaved={(product) => navigate(`/products/${product.id}`)}
          />
        </Modal>
      )}
    </>
  )
}
