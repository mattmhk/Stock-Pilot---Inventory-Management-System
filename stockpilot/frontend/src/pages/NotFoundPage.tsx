import { Link } from 'react-router'
import { EmptyState } from '../components/States'

export function NotFoundPage({ message = "This page doesn't exist." }: { message?: string }) {
  return (
    <section className="card">
      <EmptyState title="Not found">
        <p>{message}</p>
        <Link to="/products" className="btn">
          Go to products
        </Link>
      </EmptyState>
    </section>
  )
}
