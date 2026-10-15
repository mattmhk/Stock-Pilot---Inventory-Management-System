from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)

# Quantity is left out on purpose: stock changes go through /stock-movements
class ProductUpdate(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    reorder_level: int = Field(ge=0)

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    quantity: int
    reorder_level: int

    model_config = ConfigDict(from_attributes=True)


class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: Literal["IN", "OUT"]
    quantity: int = Field(gt=0)
    note: str | None = None

class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: int
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
