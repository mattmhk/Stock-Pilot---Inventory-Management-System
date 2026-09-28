
from fastapi import FastAPI

app = FastAPI(title="StockPilot Inventory API")


@app.get("/")
def home():
    return {"message": "Welcome to StockPilot"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products")
def get_products():
    return [
        {
            "id": 1,
            "sku": "SKU-001",
            "name": "USB-C Cable",
            "quantity": 25,
            "reorder_level": 10
        }
    ]