def test_dashboard_summary_when_empty(client):
    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_products": 0,
        "total_units": 0,
        "low_stock_products": 0,
        "out_of_stock_products": 0
    }


def test_dashboard_summary(client, create_product):
    create_product(sku="SKU-001", quantity=50, reorder_level=10)  # healthy
    create_product(sku="SKU-002", quantity=8, reorder_level=10)   # low
    create_product(sku="SKU-003", quantity=0, reorder_level=5)    # low + out

    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_products": 3,
        "total_units": 58,
        "low_stock_products": 2,
        "out_of_stock_products": 1
    }


def test_dashboard_reflects_stock_movements(client, create_product, add_movement):
    product_id = create_product(quantity=10, reorder_level=5)["id"]

    add_movement(product_id, "OUT", 10)

    summary = client.get("/dashboard/summary").json()
    assert summary["total_units"] == 0
    assert summary["low_stock_products"] == 1
    assert summary["out_of_stock_products"] == 1
