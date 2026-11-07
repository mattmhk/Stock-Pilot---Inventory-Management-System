from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, StockMovement
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    StockMovementResponse
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get(
    "",
    response_model=list[ProductResponse]
)
def get_products(
    search: str | None = Query(None, min_length=1),
    min_quantity: int | None = Query(None, ge=0),
    max_quantity: int | None = Query(None, ge=0),
    low_stock: bool | None = None,
    db: Session = Depends(get_db)
):

    if (
        min_quantity is not None
        and max_quantity is not None
        and min_quantity > max_quantity
    ):
        raise HTTPException(
            status_code=400,
            detail="min_quantity cannot be greater than max_quantity"
        )

    query = select(Product)

    # Case-insensitive partial match on name or SKU
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(pattern),
                Product.sku.ilike(pattern)
            )
        )

    if min_quantity is not None:
        query = query.where(Product.quantity >= min_quantity)

    if max_quantity is not None:
        query = query.where(Product.quantity <= max_quantity)

    if low_stock is True:
        query = query.where(Product.quantity <= Product.reorder_level)
    elif low_stock is False:
        query = query.where(Product.quantity > Product.reorder_level)

    return db.scalars(query.order_by(Product.id)).all()


#creating a new product
@router.post(
    "",
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


#Products at or below their reorder level
#Must stay above /{product_id} so "low-stock" isn't parsed as an id
@router.get(
    "/low-stock",
    response_model=list[ProductResponse]
)
def get_low_stock_products(
    db: Session = Depends(get_db)
):

    return db.scalars(
        select(Product).where(
            Product.quantity <= Product.reorder_level
        )
    ).all()


#Find product by product id
@router.get(
    "/{product_id}",
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


@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    updated_product: ProductUpdate,
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
    product.reorder_level = updated_product.reorder_level

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}")
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


#Movement history for a single product
@router.get(
    "/{product_id}/stock-movements",
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
