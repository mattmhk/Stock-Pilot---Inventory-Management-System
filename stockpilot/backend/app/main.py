from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import engine, get_db
from app.models import Base, Product, StockMovement
from app.schemas import (
    ProductCreate,
    ProductResponse,
    StockMovementCreate,
    StockMovementResponse
)


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


#Record stock coming in or going out and update the product quantity
@app.post(
    "/stock-movements",
    status_code=201,
    response_model=StockMovementResponse
)
def create_stock_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db)
):

    product = db.get(Product, movement.product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if movement.movement_type == "OUT":
        if movement.quantity > product.quantity:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock"
            )
        product.quantity -= movement.quantity
    else:
        product.quantity += movement.quantity

    new_movement = StockMovement(
        product_id=movement.product_id,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        note=movement.note
    )

    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)

    return new_movement


@app.get(
    "/stock-movements",
    response_model=list[StockMovementResponse]
)
def get_stock_movements(db: Session = Depends(get_db)):
    return db.scalars(
        select(StockMovement).order_by(StockMovement.created_at.desc())
    ).all()


@app.get(
    "/stock-movements/{movement_id}",
    response_model=StockMovementResponse
)
def get_stock_movement(movement_id: int, db: Session = Depends(get_db)):

    movement = db.get(StockMovement, movement_id)

    if movement is None:
        raise HTTPException(
            status_code=404,
            detail="Stock movement not found"
        )

    return movement


#Movement history for a single product
@app.get(
    "/products/{product_id}/stock-movements",
    response_model=list[StockMovementResponse]
)
def get_product_stock_movements(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return db.scalars(
        select(StockMovement)
        .where(StockMovement.product_id == product_id)
        .order_by(StockMovement.created_at.desc())
    ).all()
