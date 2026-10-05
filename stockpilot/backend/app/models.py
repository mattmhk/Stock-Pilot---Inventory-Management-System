from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int]
    reorder_level: Mapped[int]