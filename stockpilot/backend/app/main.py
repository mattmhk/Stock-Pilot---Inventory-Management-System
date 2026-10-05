from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import engine, get_db
from app.models import Base, Product
from app.schemas import ProductCreate, ProductResponse


# Create database tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockPilot Inventory API")


@app.get("/")
def home():
    return {"message": "Welcome to StockPilot"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get(
    "/products",
    response_model=list[ProductResponse]
)
def get_products(db: Session = Depends(get_db)):
    return db.scalars(select(Product)).all()


#creating a new product
@app.post(
    "/products",
    status_code=201,
    response_model=ProductResponse
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    existing_product = db.scalar(
        select(Product).where(Product.sku == product.sku)
    )

    if existing_product:
        raise HTTPException(
            status_code=409,
            detail="Product SKU already exists"
        )

    new_product = Product(
        sku=product.sku,
        name=product.name,
        quantity=product.quantity,
        reorder_level=product.reorder_level
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


#Find product by product id
@app.get(
    "/products/{product_id}",
    response_model=ProductResponse
)
def get_product(product_id: int, db: Session = Depends(get_db)):

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    updated_product: ProductCreate,
    db: Session = Depends(get_db)
):

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Check whether the new SKU belongs to another product
    existing_product = db.scalar(
        select(Product).where(
            Product.sku == updated_product.sku,
            Product.id != product_id
        )
    )

    if existing_product:
        raise HTTPException(
            status_code=409,
            detail="Product SKU already exists"
        )

    product.sku = updated_product.sku
    product.name = updated_product.name
    product.quantity = updated_product.quantity
    product.reorder_level = updated_product.reorder_level

    db.commit()
    db.refresh(product)

    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
