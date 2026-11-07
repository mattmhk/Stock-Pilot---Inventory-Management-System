from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


#Headline inventory numbers for the dashboard
@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db)
):

    total_products = db.scalar(
        select(func.count(Product.id))
    )

    # SUM() returns None when there are no products
    total_units = db.scalar(
        select(func.sum(Product.quantity))
    ) or 0

    low_stock_products = db.scalar(
        select(func.count(Product.id))
        .where(Product.quantity <= Product.reorder_level)
    )

    out_of_stock_products = db.scalar(
        select(func.count(Product.id))
        .where(Product.quantity == 0)
    )

    return {
        "total_products": total_products,
        "total_units": total_units,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products
    }
