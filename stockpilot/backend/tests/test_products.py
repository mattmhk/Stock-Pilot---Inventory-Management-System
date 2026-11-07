from tests.conftest import USB_CABLE

WIRELESS_MOUSE = {
    "sku": "SKU-002",
    "name": "Wireless Mouse",
    "quantity": 15,
    "reorder_level": 5
}


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------- POST /products ----------

def test_create_product(client):
    response = client.post("/products", json=USB_CABLE)

    assert response.status_code == 201

    data = response.json()
    assert data["sku"] == "SKU-001"
    assert data["name"] == "USB-C Cable"
    assert data["quantity"] == 25
    assert data["reorder_level"] == 10
    assert "id" in data


def test_duplicate_sku_is_rejected(client):
    client.post("/products", json=USB_CABLE)

    response = client.post("/products", json=USB_CABLE)

    assert response.status_code == 409
    assert response.json() == {"detail": "Product SKU already exists"}


def test_create_product_rejects_negative_quantity(client):
    response = client.post("/products", json={**USB_CABLE, "quantity": -1})

    assert response.status_code == 422


def test_create_product_rejects_empty_name(client):
    response = client.post("/products", json={**USB_CABLE, "name": ""})

    assert response.status_code == 422


# ---------- GET /products ----------

def test_get_products(client):
    client.post("/products", json=USB_CABLE)
    client.post("/products", json=WIRELESS_MOUSE)

    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_products_empty(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == []


def test_search_products(client):
    client.post("/products", json=USB_CABLE)
    client.post("/products", json=WIRELESS_MOUSE)

    response = client.get("/products?search=mouse")

    assert response.status_code == 200

    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Wireless Mouse"


def test_search_matches_sku(client):
    client.post("/products", json=USB_CABLE)
    client.post("/products", json=WIRELESS_MOUSE)

    products = client.get("/products?search=sku-002").json()

    assert [p["sku"] for p in products] == ["SKU-002"]


def test_filter_by_quantity_range(client, create_product):
    create_product(sku="SKU-001", quantity=5)
    create_product(sku="SKU-002", quantity=15)
    create_product(sku="SKU-003", quantity=30)

    products = client.get("/products?min_quantity=10&max_quantity=20").json()

    assert [p["sku"] for p in products] == ["SKU-002"]


def test_invalid_quantity_range(client):
    response = client.get("/products?min_quantity=100&max_quantity=10")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "min_quantity cannot be greater than max_quantity"
    }


def test_filter_low_stock_true_and_false(client, create_product):
    create_product(sku="LOW", quantity=5, reorder_level=10)
    create_product(sku="EXACT", quantity=10, reorder_level=10)
    create_product(sku="OK", quantity=50, reorder_level=10)

    low = client.get("/products?low_stock=true").json()
    not_low = client.get("/products?low_stock=false").json()

    assert [p["sku"] for p in low] == ["LOW", "EXACT"]
    assert [p["sku"] for p in not_low] == ["OK"]


# ---------- GET /products/low-stock ----------

def test_low_stock_endpoint(client, create_product):
    create_product(sku="LOW", quantity=2, reorder_level=10)
    create_product(sku="EXACT", quantity=10, reorder_level=10)
    create_product(sku="OK", quantity=11, reorder_level=10)

    response = client.get("/products/low-stock")

    assert response.status_code == 200
    # "At or below" the reorder level counts as low stock
    assert sorted(p["sku"] for p in response.json()) == ["EXACT", "LOW"]


# ---------- GET /products/{id} ----------

def test_get_product_by_id(client, create_product):
    product = create_product()

    response = client.get(f"/products/{product['id']}")

    assert response.status_code == 200
    assert response.json() == product


def test_get_missing_product_returns_404(client):
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


# ---------- PUT /products/{id} ----------

def test_update_product(client, create_product):
    product = create_product()

    response = client.put(
        f"/products/{product['id']}",
        json={"sku": "SKU-001-B", "name": "USB-C Cable 2m", "reorder_level": 3}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["sku"] == "SKU-001-B"
    assert data["name"] == "USB-C Cable 2m"
    assert data["reorder_level"] == 3
    assert data["quantity"] == 25


def test_update_ignores_quantity_field(client, create_product):
    product = create_product(quantity=25)

    # Stock changes must go through /stock-movements, not PUT
    response = client.put(
        f"/products/{product['id']}",
        json={
            "sku": "SKU-001",
            "name": "USB-C Cable",
            "reorder_level": 10,
            "quantity": 9999
        }
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 25


def test_update_can_keep_same_sku(client, create_product):
    product = create_product()

    response = client.put(
        f"/products/{product['id']}",
        json={"sku": "SKU-001", "name": "Renamed", "reorder_level": 10}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"


def test_update_to_another_products_sku_is_rejected(client, create_product):
    create_product(sku="SKU-001")
    second = create_product(sku="SKU-002")

    response = client.put(
        f"/products/{second['id']}",
        json={"sku": "SKU-001", "name": "Clash", "reorder_level": 1}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Product SKU already exists"}


def test_update_missing_product_returns_404(client):
    response = client.put(
        "/products/999",
        json={"sku": "SKU-999", "name": "Ghost", "reorder_level": 1}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


# ---------- DELETE /products/{id} ----------

def test_delete_product(client, create_product):
    product = create_product()

    response = client.delete(f"/products/{product['id']}")

    assert response.status_code == 200
    assert response.json() == {"message": "Product deleted successfully"}
    assert client.get(f"/products/{product['id']}").status_code == 404


def test_delete_missing_product_returns_404(client):
    response = client.delete("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


def test_deleting_product_deletes_its_movements(client, create_product, add_movement):
    product = create_product()
    movement_id = add_movement(product["id"], "IN", 5).json()["id"]

    client.delete(f"/products/{product['id']}")

    assert client.get(f"/stock-movements/{movement_id}").status_code == 404
    assert client.get("/stock-movements").json() == []
