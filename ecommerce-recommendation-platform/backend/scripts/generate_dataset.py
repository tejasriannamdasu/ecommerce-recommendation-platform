"""
Realistic synthetic dataset generator.
-----------------------------------------
This project is wired to train on real-world data: point DATASET_SOURCE
at the Amazon Product Reviews dataset (https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/)
or the Retailrocket e-commerce dataset (https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset)
and set LOAD_REAL_DATASET=true — see the README "Using a Real Dataset" section
for the exact loader.

For local development / CI (no internet access required), this script
generates a large, realistic synthetic catalog + interaction log with
Zipfian popularity skew, coherent categories/brands, and text descriptions,
so the full ML pipeline (TF-IDF, NMF, FAISS) trains on non-trivial data
out of the box.

Usage:
    python scripts/generate_dataset.py --num-products 3000 --num-users 1500 --num-interactions 60000
"""
import argparse
import random
import csv
import os

random.seed(42)

CATEGORIES = {
    "Electronics": ["Headphones", "Smartwatch", "Bluetooth Speaker", "Laptop Stand", "Webcam", "Gaming Mouse", "Mechanical Keyboard", "Power Bank", "USB-C Hub", "Wireless Earbuds"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender", "Non-Stick Pan Set", "Vacuum Cleaner", "Electric Kettle", "Cutlery Set", "Storage Containers", "Cutting Board", "Toaster"],
    "Fashion": ["Running Shoes", "Denim Jacket", "Cotton T-Shirt", "Leather Wallet", "Sunglasses", "Backpack", "Formal Shirt", "Sneakers", "Wrist Watch", "Hoodie"],
    "Books": ["Science Fiction Novel", "Self-Help Guide", "Programming Handbook", "Mystery Thriller", "Biography", "Cookbook", "History Book", "Business Strategy Book", "Poetry Collection", "Fantasy Novel"],
    "Sports & Outdoors": ["Yoga Mat", "Dumbbell Set", "Camping Tent", "Cycling Helmet", "Water Bottle", "Resistance Bands", "Hiking Backpack", "Football", "Badminton Racket", "Fitness Tracker"],
    "Beauty & Personal Care": ["Face Moisturizer", "Electric Toothbrush", "Hair Dryer", "Sunscreen SPF 50", "Beard Trimmer", "Shampoo", "Perfume", "Lip Balm Set", "Skincare Kit", "Nail Care Kit"],
}

BRANDS = ["Nova", "Zenith", "Orbit", "Apex", "Vertex", "Pulse", "Aurora", "Fusion", "Crest", "Halo", "Lumen", "Drift", "Ember", "Quartz", "Sable"]

ADJECTIVES = ["Premium", "Portable", "Wireless", "Compact", "Professional", "Ergonomic", "Lightweight", "Durable", "Smart", "Eco-Friendly", "Rechargeable", "High-Performance"]

DESC_TEMPLATES = [
    "The {adj} {product} from {brand} is designed for everyday use, combining reliable performance with a sleek build.",
    "Experience {adj_lower} comfort with the {brand} {product}, engineered for durability and modern living.",
    "This {brand} {product} offers {adj_lower} functionality, perfect for {category_lower} enthusiasts looking for quality.",
    "Upgrade your routine with the {adj} {product} — {brand}'s answer to performance and style.",
    "A best-selling {category_lower} item, this {brand} {product} blends {adj_lower} design with practical features.",
]

TAG_POOL = ["bestseller", "new-arrival", "eco-friendly", "gift-idea", "trending", "limited-edition", "top-rated", "budget-friendly", "premium-quality", "fast-shipping"]


def generate_products(num_products: int):
    products = []
    pid = 1
    cat_names = list(CATEGORIES.keys())
    for _ in range(num_products):
        category = random.choice(cat_names)
        base_item = random.choice(CATEGORIES[category])
        brand = random.choice(BRANDS)
        adj = random.choice(ADJECTIVES)
        title = f"{brand} {adj} {base_item}"
        template = random.choice(DESC_TEMPLATES)
        description = template.format(adj=adj, adj_lower=adj.lower(), product=base_item, brand=brand, category_lower=category.lower())
        tags = ",".join(random.sample(TAG_POOL, k=random.randint(2, 4)))
        price = round(random.uniform(9.99, 899.99), 2)
        products.append({
            "id": pid, "title": title, "description": description,
            "category": category, "tags": tags, "brand": brand, "price": price,
            "image_url": f"https://picsum.photos/seed/product{pid}/400/400",
        })
        pid += 1
    return products


def zipf_weights(n, s=1.2):
    weights = [1 / (rank ** s) for rank in range(1, n + 1)]
    total = sum(weights)
    return [w / total for w in weights]


def generate_interactions(num_users: int, products: list, num_interactions: int):
    """Zipfian product popularity + a handful of 'power users' -> realistic long-tail data."""
    product_ids = [p["id"] for p in products]
    random.shuffle(product_ids)  # randomize which products are "popular" so it's not just id order
    weights = zipf_weights(len(product_ids))

    interactions = []
    interaction_types = ["view", "click", "purchase", "wishlist"]
    type_probs = [0.6, 0.25, 0.1, 0.05]

    for i in range(num_interactions):
        user_id = random.randint(1, num_users)
        product_id = random.choices(product_ids, weights=weights, k=1)[0]
        itype = random.choices(interaction_types, weights=type_probs, k=1)[0]
        interactions.append({"user_id": user_id, "product_id": product_id, "interaction_type": itype})

    ratings = []
    rating_pairs = random.sample(interactions, k=min(len(interactions), num_interactions // 4))
    seen = set()
    for r in rating_pairs:
        key = (r["user_id"], r["product_id"])
        if key in seen:
            continue
        seen.add(key)
        score = min(5, max(1, round(random.gauss(4.0, 1.0))))
        ratings.append({"user_id": r["user_id"], "product_id": r["product_id"], "score": score})

    return interactions, ratings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-products", type=int, default=3000)
    parser.add_argument("--num-users", type=int, default=1500)
    parser.add_argument("--num-interactions", type=int, default=60000)
    parser.add_argument("--out-dir", type=str, default="../../database/seed_csv")
    args = parser.parse_args()

    out_dir = os.path.join(os.path.dirname(__file__), args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    products = generate_products(args.num_products)
    interactions, ratings = generate_interactions(args.num_users, products, args.num_interactions)

    with open(os.path.join(out_dir, "products.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)

    with open(os.path.join(out_dir, "interactions.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "product_id", "interaction_type"])
        writer.writeheader()
        writer.writerows(interactions)

    with open(os.path.join(out_dir, "ratings.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "product_id", "score"])
        writer.writeheader()
        writer.writerows(ratings)

    print(f"Generated {len(products)} products, {len(interactions)} interactions, {len(ratings)} ratings")
    print(f"Written to: {out_dir}")


if __name__ == "__main__":
    main()
