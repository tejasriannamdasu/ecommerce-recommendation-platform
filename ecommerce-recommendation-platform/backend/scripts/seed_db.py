"""
Loads the generated CSVs (see generate_dataset.py) into PostgreSQL.
Run after the DB container is up and generate_dataset.py has produced
seed_csv/{products,interactions,ratings}.csv.

Usage:
    python scripts/seed_db.py
"""
import os
import csv
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, Base, engine
from app.models.product import Product, Category
from app.models.user import User, UserRole
from app.models.interaction import UserInteraction, Rating, InteractionType
from app.models.order import Order, OrderItem
from app.auth.security import hash_password

# Locally: backend/scripts/../../database/seed_csv
# In Docker: the compose file mounts ./database -> /app/database, so this
# env var override is used instead (see docker-compose.yml).
SEED_DIR = os.environ.get(
    "SEED_DATA_DIR",
    os.path.join(os.path.dirname(__file__), "..", "..", "database", "seed_csv"),
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Product).count() > 0:
            print("Database already seeded. Skipping. (Drop tables to re-seed.)")
            return

        # --- Categories ---
        with open(os.path.join(SEED_DIR, "products.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        category_names = sorted({r["category"] for r in rows})
        category_map = {}
        for name in category_names:
            cat = Category(name=name)
            db.add(cat)
            db.flush()
            category_map[name] = cat.id

        # --- Products ---
        for r in rows:
            db.add(Product(
                id=int(r["id"]), title=r["title"], description=r["description"],
                tags=r["tags"], price=float(r["price"]), brand=r["brand"],
                image_url=r["image_url"], category_id=category_map[r["category"]],
            ))
        db.commit()
        print(f"Seeded {len(rows)} products across {len(category_names)} categories")

        # --- Admin + demo users ---
        admin = User(email="admin@example.com", username="admin", hashed_password=hash_password("Admin@123"), role=UserRole.ADMIN)
        db.add(admin)
        max_user_id = 0
        with open(os.path.join(SEED_DIR, "interactions.csv"), encoding="utf-8") as f:
            interaction_rows = list(csv.DictReader(f))
        max_user_id = max(int(r["user_id"]) for r in interaction_rows)

        for i in range(1, max_user_id + 1):
            db.add(User(
                email=f"user{i}@example.com", username=f"user{i}",
                hashed_password=hash_password("Password@123"), role=UserRole.CUSTOMER,
            ))
        db.commit()
        print(f"Seeded 1 admin + {max_user_id} demo users (password: Password@123)")

        # --- Interactions ---
        for r in interaction_rows:
            db.add(UserInteraction(
                user_id=int(r["user_id"]), product_id=int(r["product_id"]),
                interaction_type=InteractionType(r["interaction_type"]),
            ))
        db.commit()
        print(f"Seeded {len(interaction_rows)} interactions")

        # --- Ratings ---
        with open(os.path.join(SEED_DIR, "ratings.csv"), encoding="utf-8") as f:
            rating_rows = list(csv.DictReader(f))
        for r in rating_rows:
            db.add(Rating(user_id=int(r["user_id"]), product_id=int(r["product_id"]), score=float(r["score"])))
        db.commit()
        print(f"Seeded {len(rating_rows)} ratings")

        # --- Recompute avg_rating / num_ratings on products ---
        from sqlalchemy import func
        stats = db.query(Rating.product_id, func.avg(Rating.score), func.count(Rating.id)).group_by(Rating.product_id).all()
        for product_id, avg_score, count in stats:
            p = db.query(Product).filter(Product.id == product_id).first()
            if p:
                p.avg_rating = round(float(avg_score), 2)
                p.num_ratings = count
        db.commit()

        # --- A handful of synthetic orders (purchases -> order + order_items) ---
        purchase_rows = [r for r in interaction_rows if r["interaction_type"] == "purchase"]
        orders_by_user = {}
        for r in purchase_rows:
            uid = int(r["user_id"])
            orders_by_user.setdefault(uid, []).append(int(r["product_id"]))

        for uid, product_ids in orders_by_user.items():
            order = Order(user_id=uid, status="completed", total_amount=0.0)
            db.add(order)
            db.flush()
            total = 0.0
            for pid in product_ids:
                p = db.query(Product).filter(Product.id == pid).first()
                if not p:
                    continue
                db.add(OrderItem(order_id=order.id, product_id=pid, quantity=1, unit_price=p.price))
                total += p.price
            order.total_amount = round(total, 2)
        db.commit()
        print(f"Seeded orders for {len(orders_by_user)} users")

        print("Database seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
