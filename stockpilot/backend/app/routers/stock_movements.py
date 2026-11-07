from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, StockMovement
from app.schemas import StockMovementCreate, StockMovementResponse


router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movements"]
)


#Record stock coming in or going out and update the product quantity
@router.post(
    "",
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


@router.get(
    "",
    response_model=list[StockMovementResponse]
)
def get_stock_movements(db: Session = Depends(get_db)):
    return db.scalars(
        select(StockMovement).order_by(StockMovement.created_at.desc())
    ).all()


@router.get(
    "/{movement_id}",
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
