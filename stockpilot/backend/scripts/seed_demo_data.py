"""Fill the database with realistic demo products and stock-movement history.

Run from stockpilot/backend:

    python -m scripts.seed_demo_data            # uses DATABASE_URL from .env
    python -m scripts.seed_demo_data --dry-run  # show what would be added

Movements are spread over the last ~60 days, and every product's quantity
equals the sum of its movements, so the history always adds up. Products
whose SKU already exists are skipped, so running it twice is harmless.
"""

import argparse
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import SessionLocal, DATABASE_URL
from app.models import Product, StockMovement


# (sku, name, reorder_level, typical daily sales, target final quantity)
# The final quantities give the dashboard a realistic mix:
# mostly healthy stock, a few low, a couple out of stock.
PRODUCTS = [
    ("CBL-USBC-1M", "USB-C Cable 1m", 25, 4, 86),
    ("CBL-USBC-2M", "USB-C Cable 2m", 20, 3, 14),
    ("CBL-HDMI-2M", "HDMI 2.1 Cable 2m", 15, 2, 41),
    ("ADP-USBC-HDMI", "USB-C to HDMI Adapter", 12, 2, 9),
    ("CHG-65W-GAN", "65W GaN Charger", 15, 2, 37),
    ("KBD-MECH-TKL", "Mechanical Keyboard (TKL)", 8, 1, 0),
    ("MSE-WL-ERGO", "Wireless Ergonomic Mouse", 10, 2, 28),
    ("MSE-WL-COMPACT", "Compact Wireless Mouse", 12, 2, 53),
    ("MON-27-QHD", '27" QHD Monitor', 5, 1, 11),
    ("MON-ARM-DUAL", "Dual Monitor Arm", 4, 1, 3),
    ("STD-LAPTOP-ALU", "Aluminium Laptop Stand", 8, 1, 19),
    ("HUB-USBC-7IN1", "7-in-1 USB-C Hub", 10, 2, 0),
    ("CAM-1080P", "1080p Webcam", 6, 1, 22),
    ("HDS-WL-ANC", "Wireless ANC Headset", 6, 1, 5),
    ("SSD-EXT-1TB", "1TB Portable SSD", 8, 1, 31),
    ("PAD-DESK-XL", "XL Desk Mat", 10, 1, 64),
]

SALES_NOTES = [
    "Online order",
    "Customer order",
    "Retail sale",
    "Business account order",
]


def build_history(rng, reorder_level, daily_sales, target, start, days):
    """Simulate deliveries and sales, ending exactly at `target` units."""
    movements = []
    po_number = rng.randint(1040, 1090)

    def add(day, movement_type, quantity, note):
        moment = start + timedelta(
            days=day,
            hours=rng.randint(8, 17),
            minutes=rng.randint(0, 59)
        )
        movements.append((moment, movement_type, quantity, note))

    stock = reorder_level * 4 + rng.randint(5, 20)
    add(0, "IN", stock, "Opening stock")

    # Leave the last few days for the final adjustment
    for day in range(1, days - 5):
        if rng.random() < 0.55:
            sold = min(stock, max(1, round(rng.gauss(daily_sales, daily_sales / 2))))
            if sold:
                stock -= sold
                order = rng.randint(5100, 5999)
                add(day, "OUT", sold, f"{rng.choice(SALES_NOTES)} #{order}")

        # Restock when stock drops to the reorder level
        if stock <= reorder_level and rng.random() < 0.6:
            delivered = reorder_level * 3 + rng.randint(0, reorder_level)
            stock += delivered
            po_number += 1
            add(day, "IN", delivered, f"Supplier delivery PO-{po_number}")

        if rng.random() < 0.02 and stock > 2:
            add(day, "OUT", 1, "Damaged in warehouse")
            stock -= 1

    # Final movements land the product on its target quantity
    if stock > target:
        add(days - 3, "OUT", stock - target, f"Business account order #{rng.randint(5100, 5999)}")
    elif stock < target:
        po_number += 1
        add(days - 3, "IN", target - stock, f"Supplier delivery PO-{po_number}")

    return movements


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="show what would be added without writing")
    parser.add_argument("--days", type=int, default=60, help="days of history to generate (default 60)")
    args = parser.parse_args()

    rng = random.Random(42)  # same data every run
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=args.days)

    host = DATABASE_URL.split("@")[-1].split("/")[0] if "@" in DATABASE_URL else DATABASE_URL
    print(f"Database: {host}")

    added = skipped = movement_count = 0

    with SessionLocal() as db:
        existing = set(db.scalars(select(Product.sku)))

        for sku, name, reorder_level, daily_sales, target in PRODUCTS:
            history = build_history(rng, reorder_level, daily_sales, target, start, args.days)

            if sku in existing:
                skipped += 1
                continue

            quantity = sum(q if t == "IN" else -q for _, t, q, _ in history)
            assert quantity == target, (sku, quantity, target)

            product = Product(sku=sku, name=name, quantity=quantity, reorder_level=reorder_level)
            product.stock_movements = [
                StockMovement(movement_type=t, quantity=q, note=note, created_at=moment)
                for moment, t, q, note in history
            ]
            db.add(product)

            added += 1
            movement_count += len(history)
            print(f"  + {sku:<16} {name:<28} qty {quantity:>3}  ({len(history)} movements)")

        if args.dry_run:
            db.rollback()
            print("Dry run: nothing written.")
        else:
            db.commit()

    print(f"Added {added} products and {movement_count} movements; skipped {skipped} that already exist.")


if __name__ == "__main__":
    main()
