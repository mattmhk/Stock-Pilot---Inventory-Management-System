# ---------- POST /stock-movements ----------

def test_stock_increases(client, create_product, add_movement):
    product_id = create_product(quantity=20)["id"]

    response = add_movement(product_id, "IN", 10, "Supplier delivery")

    assert response.status_code == 201
    assert client.get(f"/products/{product_id}").json()["quantity"] == 30


def test_stock_decreases(client, create_product, add_movement):
    product_id = create_product(quantity=20)["id"]

    response = add_movement(product_id, "OUT", 5, "Customer order")

    assert response.status_code == 201
    assert client.get(f"/products/{product_id}").json()["quantity"] == 15


def test_movement_response_body(create_product, add_movement):
    product_id = create_product()["id"]

    data = add_movement(product_id, "IN", 7, "Restock").json()

    assert data["product_id"] == product_id
    assert data["movement_type"] == "IN"
    assert data["quantity"] == 7
    assert data["note"] == "Restock"
    assert "id" in data
    assert "created_at" in data


def test_cannot_remove_more_stock_than_available(client, create_product, add_movement):
    product_id = create_product(quantity=10, reorder_level=5)["id"]

    response = add_movement(product_id, "OUT", 50, "Customer order")

    assert response.status_code == 400
    assert response.json() == {"detail": "Insufficient stock"}

    # The failed movement must not change the stock level...
    assert client.get(f"/products/{product_id}").json()["quantity"] == 10
    # ...or be recorded in the history
    assert client.get("/stock-movements").json() == []


def test_can_remove_exactly_all_stock(client, create_product, add_movement):
    product_id = create_product(quantity=10)["id"]

    response = add_movement(product_id, "OUT", 10)

    assert response.status_code == 201
    assert client.get(f"/products/{product_id}").json()["quantity"] == 0


def test_movement_for_missing_product_returns_404(add_movement):
    response = add_movement(999, "IN", 5)

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_invalid_movement_type_is_rejected(create_product, add_movement):
    product_id = create_product()["id"]

    response = add_movement(product_id, "SIDEWAYS", 5)

    assert response.status_code == 422


def test_zero_quantity_movement_is_rejected(create_product, add_movement):
    product_id = create_product()["id"]

    response = add_movement(product_id, "IN", 0)

    assert response.status_code == 422


# ---------- GET /stock-movements ----------

def test_get_all_movements(client, create_product, add_movement):
    first = create_product(sku="SKU-001")["id"]
    second = create_product(sku="SKU-002")["id"]
    add_movement(first, "IN", 5)
    add_movement(second, "OUT", 3)

    response = client.get("/stock-movements")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_movement_by_id(client, create_product, add_movement):
    product_id = create_product()["id"]
    movement = add_movement(product_id, "IN", 5, "Delivery").json()

    response = client.get(f"/stock-movements/{movement['id']}")

    assert response.status_code == 200
    assert response.json() == movement


def test_get_missing_movement_returns_404(client):
    response = client.get("/stock-movements/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Stock movement not found"}


# ---------- GET /products/{id}/stock-movements ----------

def test_product_movement_history_only_shows_that_product(
    client, create_product, add_movement
):
    cable = create_product(sku="SKU-001")["id"]
    mouse = create_product(sku="SKU-002")["id"]
    add_movement(cable, "IN", 5)
    add_movement(cable, "OUT", 2)
    add_movement(mouse, "IN", 9)

    response = client.get(f"/products/{cable}/stock-movements")

    assert response.status_code == 200

    history = response.json()
    assert len(history) == 2
    assert all(m["product_id"] == cable for m in history)
    assert sorted(m["movement_type"] for m in history) == ["IN", "OUT"]


def test_product_movement_history_for_missing_product_returns_404(client):
    response = client.get("/products/999/stock-movements")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
