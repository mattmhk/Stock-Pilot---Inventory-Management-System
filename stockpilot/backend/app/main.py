
from fastapi import FastAPI, HTTPException

from app.schemas import ProductCreate


app = FastAPI(title="StockPilot Inventory API")


# Temporary product storage
products = [
    {
        "id": 1,
        "sku": "SKU-001",
        "name": "USB-C Cable",
        "quantity": 25,
        "reorder_level": 10
    }
]


@app.get("/")
def home():
    return {"message": "Welcome to StockPilot"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/products")
def get_products():
    return products


@app.post("/products", status_code=201)
def create_product(product: ProductCreate):

    # Check whether the SKU already exists
    for existing_product in products:
        if existing_product["sku"] == product.sku:
            raise HTTPException(
                status_code=409,
                detail="Product SKU already exists"
            )

    # Generate a new product ID
    new_id = max(
        [p["id"] for p in products],
        default=0
    ) + 1

    # Create a product dictionary
    new_product = {
        "id": new_id,
        **product.model_dump()
    }

    # Add the product to our list
    products.append(new_product)

    return new_product