# StockPilot frontend

React + TypeScript (Vite) interface for the StockPilot API. See the [main README](../../README.md) for full setup.

```bash
npm install
npm run dev      # http://localhost:5173 (expects the API on http://127.0.0.1:8000)
npm run lint
npm run build
```

Set `VITE_API_URL` in `.env` (see `.env.example`) to use a different API address.

- `src/lib/api.ts`: typed API client; FastAPI error details become readable messages
- `src/lib/useApi.ts`: data-fetching hook (loading, error, reload) and a debounce hook
- `src/pages/`: Dashboard, Products (filters stored in the URL), Product detail
- `src/components/`: layout, product and stock-movement forms, modal, status badges, loading/empty/error states
