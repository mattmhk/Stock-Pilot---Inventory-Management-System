from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    reorder_level: int = Field(ge=0)

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    quantity: int
    reorder_level: int

    model_config = ConfigDict(from_attributes=True)