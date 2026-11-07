import type { Product } from './api'

export type StockStatus = 'good' | 'low' | 'out'

/** Mirrors the backend rules: out at 0, low at or below the reorder level. */
export function stockStatus(product: Pick<Product, 'quantity' | 'reorder_level'>): StockStatus {
  if (product.quantity === 0) return 'out'
  if (product.quantity <= product.reorder_level) return 'low'
  return 'good'
}

export const STATUS_LABELS: Record<StockStatus, string> = {
  good: 'In stock',
  low: 'Low stock',
  out: 'Out of stock',
}

const numberFormat = new Intl.NumberFormat()

export function formatNumber(value: number): string {
  return numberFormat.format(value)
}

const dateFormat = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
})

/**
 * Formats an API timestamp in the viewer's local time.
 * SQLite returns timestamps without an offset; they are stored as UTC,
 * so a missing offset is treated as UTC.
 */
export function formatDateTime(value: string): string {
  const hasOffset = /(Z|[+-]\d{2}:?\d{2})$/.test(value)
  return dateFormat.format(new Date(hasOffset ? value : `${value}Z`))
}
