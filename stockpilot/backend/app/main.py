import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import products, stock_movements, dashboard


app = FastAPI(
    title="StockPilot Inventory API",
    version="1.0.0"
)


# Browser origins allowed to call the API (the React frontend).
# Comma-separated, e.g. "http://localhost:5173,https://stockpilot.example.com"
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
)

app.add_middleware(
    CORSMiddleware,
    # A trailing slash would never match the browser's Origin header, so drop it
    allow_origins=[
        origin.strip().rstrip("/")
        for origin in CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"]
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
