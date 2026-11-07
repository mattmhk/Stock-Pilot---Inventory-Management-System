from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import products, stock_movements, dashboard


# Create database tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockPilot Inventory API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"message": "Welcome to StockPilot"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(products.router)
app.include_router(stock_movements.router)
app.include_router(dashboard.router)
