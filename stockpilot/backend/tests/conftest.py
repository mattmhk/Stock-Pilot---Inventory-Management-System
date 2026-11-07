import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base


# In-memory SQLite database, so tests never touch stockpilot.db.
# StaticPool keeps a single connection so every session sees the same in-memory DB.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Any endpoint that depends on get_db gets the test database instead
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    # Every test starts with empty tables
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


USB_CABLE = {
    "sku": "SKU-001",
    "name": "USB-C Cable",
    "quantity": 25,
    "reorder_level": 10
}


@pytest.fixture
def create_product(client):
    """Factory fixture: create a product (USB cable by default) and return its JSON.

    Usage: create_product(sku="SKU-002", quantity=0)
    """
    def _create_product(**overrides):
        response = client.post("/products", json={**USB_CABLE, **overrides})
        assert response.status_code == 201
        return response.json()

    return _create_product


@pytest.fixture
def add_movement(client):
    """Factory fixture: post a stock movement and return the response."""
    def _add_movement(product_id, movement_type, quantity, note=None):
        return client.post(
            "/stock-movements",
            json={
                "product_id": product_id,
                "movement_type": movement_type,
                "quantity": quantity,
                "note": note
            }
        )

    return _add_movement
