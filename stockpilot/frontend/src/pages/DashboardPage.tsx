import { Link } from 'react-router'
import { api } from '../lib/api'
import { formatNumber } from '../lib/stock'
import { useApi } from '../lib/useApi'
import { StatusBadge } from '../components/StatusBadge'
import { EmptyState, ErrorMessage, Loading } from '../components/States'

export function DashboardPage() {
  const summary = useApi(() => api.getDashboardSummary(), [])
  const lowStock = useApi(() => api.getLowStockProducts(), [])

  const cards = summary.data && [
    { label: 'Total products', value: summary.data.total_products, to: '/products' },
    { label: 'Total units', value: summary.data.total_units, to: '/products' },
    {
      label: 'Low stock',
      value: summary.data.low_stock_products,
      to: '/products?status=low',
      tone: summary.data.low_stock_products > 0 ? 'warn' : undefined,
    },
    {
      label: 'Out of stock',
      value: summary.data.out_of_stock_products,
      to: '/products?status=out',
      tone: summary.data.out_of_stock_products > 0 ? 'danger' : undefined,
    },
  ]

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="subtle">An overview of your inventory.</p>
        </div>
      </div>

      {summary.error && <ErrorMessage error={summary.error} onRetry={summary.reload} />}

      <section className="stats" aria-label="Inventory summary">
        {cards
          ? cards.map((card) => (
              <Link key={card.label} to={card.to} className={`stat ${card.tone ? `stat-${card.tone}` : ''}`}>
                <span className="stat-label">{card.label}</span>
                <span className="stat-value">{formatNumber(card.value)}</span>
              </Link>
            ))
          : !summary.error &&
            [0, 1, 2, 3].map((i) => <div key={i} className="stat stat-skeleton" aria-hidden="true" />)}
      </section>

      <section className="card">
        <div className="card-header">
          <h2>Needs restocking</h2>
          <Link to="/products?status=low" className="link">
            View all
          </Link>
        </div>

        {lowStock.loading && !lowStock.data ? (
          <Loading />
        ) : lowStock.error ? (
          <ErrorMessage error={lowStock.error} onRetry={lowStock.reload} />
        ) : lowStock.data && lowStock.data.length === 0 ? (
          <EmptyState title="Everything is well stocked">
            <p>No products are at or below their reorder level.</p>
          </EmptyState>
        ) : (
          <div className="table-wrap">
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
                {lowStock.data?.map((product) => (
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
    </>
  )
}
