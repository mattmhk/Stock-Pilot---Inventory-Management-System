import type { Product } from '../lib/api'
import { STATUS_LABELS, stockStatus } from '../lib/stock'

export function StatusBadge({ product }: { product: Pick<Product, 'quantity' | 'reorder_level'> }) {
  const status = stockStatus(product)

  return <span className={`badge badge-${status}`}>{STATUS_LABELS[status]}</span>
}
