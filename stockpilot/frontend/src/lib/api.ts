// Typed client for the StockPilot FastAPI backend.

export interface Product {
  id: number
  sku: string
  name: string
  quantity: number
  reorder_level: number
}

export interface ProductCreate {
  sku: string
  name: string
  quantity: number
  reorder_level: number
}

// Quantity is deliberately not editable: stock changes go through movements
export type ProductUpdate = Omit<ProductCreate, 'quantity'>

export type MovementType = 'IN' | 'OUT'

export interface StockMovement {
  id: number
  product_id: number
  movement_type: MovementType
  quantity: number
  note: string | null
  created_at: string
}

export interface StockMovementCreate {
  product_id: number
  movement_type: MovementType
  quantity: number
  note: string | null
}

export interface DashboardSummary {
  total_products: number
  total_units: number
  low_stock_products: number
  out_of_stock_products: number
}

export interface ProductFilters {
  search?: string
  min_quantity?: number
  max_quantity?: number
  low_stock?: boolean
}

const API_URL = (import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')

/** An error response from the API, with FastAPI's `detail` turned into readable text. */
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

interface ValidationIssue {
  loc?: (string | number)[]
  msg?: string
}

function describeDetail(detail: unknown): string | null {
  if (typeof detail === 'string') return detail

  // 422 responses: [{ loc: ["body", "quantity"], msg: "..." }, ...]
  if (Array.isArray(detail)) {
    return detail
      .map((issue: ValidationIssue) => {
        const field = issue.loc?.filter((part) => part !== 'body').join('.')
        return field ? `${field}: ${issue.msg}` : issue.msg
      })
      .join('; ')
  }

  return null
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response

  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError(0, `Can't reach the StockPilot API at ${API_URL}. Is the backend running?`)
  }

  const body = await response.json().catch(() => null)

  if (!response.ok) {
    const message = describeDetail(body?.detail) ?? `Request failed (${response.status})`
    throw new ApiError(response.status, message)
  }

  return body as T
}

function toQueryString(filters: ProductFilters): string {
  const params = new URLSearchParams()

  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') params.set(key, String(value))
  }

  const query = params.toString()
  return query ? `?${query}` : ''
}

export const api = {
  getDashboardSummary: () => request<DashboardSummary>('/dashboard/summary'),

  getProducts: (filters: ProductFilters = {}) =>
    request<Product[]>(`/products${toQueryString(filters)}`),

  getLowStockProducts: () => request<Product[]>('/products/low-stock'),

  getProduct: (id: number) => request<Product>(`/products/${id}`),

  createProduct: (product: ProductCreate) =>
    request<Product>('/products', { method: 'POST', body: JSON.stringify(product) }),

  updateProduct: (id: number, product: ProductUpdate) =>
    request<Product>(`/products/${id}`, { method: 'PUT', body: JSON.stringify(product) }),

  deleteProduct: (id: number) =>
    request<{ message: string }>(`/products/${id}`, { method: 'DELETE' }),

  getProductMovements: (id: number) =>
    request<StockMovement[]>(`/products/${id}/stock-movements`),

  createStockMovement: (movement: StockMovementCreate) =>
    request<StockMovement>('/stock-movements', {
      method: 'POST',
      body: JSON.stringify(movement),
    }),
}
