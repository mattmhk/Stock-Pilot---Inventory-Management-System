import { NavLink, Outlet } from 'react-router'

export function Layout() {
  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar-inner">
          <NavLink to="/" className="brand">
            <span className="brand-mark" aria-hidden="true">
              SP
            </span>
            StockPilot
          </NavLink>

          <nav className="nav" aria-label="Main">
            <NavLink to="/" end>
              Dashboard
            </NavLink>
            <NavLink to="/products">Products</NavLink>
          </nav>

          <span className="topbar-tag">Inventory Admin</span>
        </div>
      </header>

      <main className="page">
        <Outlet />
      </main>
    </div>
  )
}
