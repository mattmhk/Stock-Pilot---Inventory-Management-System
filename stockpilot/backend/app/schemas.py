
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)