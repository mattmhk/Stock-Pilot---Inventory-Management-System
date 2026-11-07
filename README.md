# StockPilot

An inventory management REST API built with **FastAPI** and **SQLAlchemy**. It tracks products and stock levels, records every stock movement in and out, flags products that need reordering, and reports headline numbers for a dashboard.

Stock levels can't be edited directly. Every change goes through a recorded stock movement, so the full history of each product is always available, and the API refuses any withdrawal that would take stock below zero.

## Features

- **Product management**: create, read, update and delete products with unique SKUs
- **Search and filtering**: case-insensitive search across name and SKU, plus min/max quantity and low-stock filters
- **Stock movements**: record `IN` (deliveries) and `OUT` (orders) movements that update stock levels automatically
- **Business rules enforced by the API**:
  - Withdrawals larger than the available stock are rejected (`400 Insufficient stock`) and change nothing
  - Duplicate SKUs are rejected (`409`)
  - Quantity can't be edited through `PUT /products/{id}`; requests that try are rejected (`422`)
- **Movement history**: a timestamped audit trail for every product; deleting a product also deletes its history
- **Low-stock alerts**: products at or below their reorder level
- **Dashboard summary**: total products, total units, low-stock count and out-of-stock count
- **Automated tests**: 39 pytest tests covering success and failure cases, each run against a fresh in-memory database

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Validation | Pydantic v2 |
| Database | SQLite |
| Testing | pytest, FastAPI `TestClient` |

## Project structure

```
stockpilot/backend/
├── app/
│   ├── main.py              # App setup and router registration
│   ├── database.py          # Engine, session and get_db dependency
│   ├── models.py            # SQLAlchemy models (Product, StockMovement)
│   ├── schemas.py           # Pydantic request/response schemas
│   └── routers/
│       ├── products.py
│       ├── stock_movements.py
│       └── dashboard.py
├── tests/
│   ├── conftest.py          # Test database and shared fixtures
│   ├── test_products.py
│   ├── test_stock_movements.py
│   └── test_dashboard.py
└── requirements.txt
```

## Getting started

### Prerequisites

- Python 3.13 or newer

### Installation

```bash
git clone https://github.com/mattmhk/Stock-Pilot---Inventory-Management-System.git
cd Stock-Pilot---Inventory-Management-System/stockpilot/backend

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Run the API

```bash
uvicorn app.main:app --reload
```

Then open:

- Interactive API docs (Swagger UI): http://127.0.0.1:8000/docs
- Alternative docs (ReDoc): http://127.0.0.1:8000/redoc

The SQLite database file (`stockpilot.db`) is created automatically on first run.

## API endpoints

### Products

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/products` | List products (supports filters below) |
| `POST` | `/products` | Create a product |
| `GET` | `/products/low-stock` | Products at or below their reorder level |
| `GET` | `/products/{id}` | Get one product |
| `PUT` | `/products/{id}` | Update SKU, name and reorder level |
| `DELETE` | `/products/{id}` | Delete a product and its movement history |
| `GET` | `/products/{id}/stock-movements` | Movement history for one product |

Query parameters for `GET /products`:

| Parameter | Example | Description |
|---|---|---|
| `search` | `?search=cable` | Case-insensitive match on name or SKU |
| `min_quantity` | `?min_quantity=10` | Quantity greater than or equal to |
| `max_quantity` | `?max_quantity=50` | Quantity less than or equal to |
| `low_stock` | `?low_stock=true` | `true`: at or below reorder level; `false`: above it |

### Stock movements

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/stock-movements` | Record an `IN` or `OUT` movement |
| `GET` | `/stock-movements` | All movements, newest first |
| `GET` | `/stock-movements/{id}` | Get one movement |

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard/summary` | Inventory totals and stock-health counts |

### Example

Create a product:

```http
POST /products
Content-Type: application/json

{
  "sku": "SKU-001",
  "name": "USB-C Cable",
  "quantity": 20,
  "reorder_level": 10
}
```

Record a customer order that takes 5 units out:

```http
POST /stock-movements
Content-Type: application/json

{
  "product_id": 1,
  "movement_type": "OUT",
  "quantity": 5,
  "note": "Customer order"
}
```

The product's quantity is now `15`, and the movement appears in `GET /products/1/stock-movements`. Asking for more than the available stock returns:

```json
{ "detail": "Insufficient stock" }
```

## Running the tests

From `stockpilot/backend` with the virtual environment active:

```bash
pytest -v
```

The tests replace the `get_db` dependency with an in-memory SQLite database that is reset before every test, so they never touch `stockpilot.db` and don't depend on each other.

## Roadmap

- [ ] GitHub Actions CI to run the tests on every push
- [ ] Environment-based configuration and Alembic migrations
- [ ] PostgreSQL support
- [ ] React + TypeScript frontend
- [ ] Deployment
