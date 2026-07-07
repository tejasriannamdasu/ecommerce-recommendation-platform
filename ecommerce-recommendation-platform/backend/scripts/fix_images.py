import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.product import Product

ITEM_IMAGE_KEYWORDS = {
    "Headphones": "headphones", "Smartwatch": "smartwatch", "Bluetooth Speaker": "bluetooth,speaker",
    "Laptop Stand": "laptop,stand", "Webcam": "webcam", "Gaming Mouse": "computer,mouse",
    "Mechanical Keyboard": "mechanical,keyboard", "Power Bank": "power,bank", "USB-C Hub": "usb,hub",
    "Wireless Earbuds": "earbuds",
    "Air Fryer": "air,fryer", "Coffee Maker": "coffee,maker", "Blender": "blender",
    "Non-Stick Pan Set": "frying,pan", "Vacuum Cleaner": "vacuum,cleaner", "Electric Kettle": "electric,kettle",
    "Cutlery Set": "cutlery", "Storage Containers": "food,container", "Cutting Board": "cutting,board", "Toaster": "toaster",
    "Running Shoes": "running,shoes", "Denim Jacket": "denim,jacket", "Cotton T-Shirt": "tshirt",
    "Leather Wallet": "leather,wallet", "Sunglasses": "sunglasses", "Backpack": "backpack",
    "Formal Shirt": "dress,shirt", "Sneakers": "sneakers", "Wrist Watch": "wristwatch", "Hoodie": "hoodie",
    "Science Fiction Novel": "scifi,book", "Self-Help Guide": "book", "Programming Handbook": "programming,book",
    "Mystery Thriller": "book", "Biography": "book", "Cookbook": "cookbook", "History Book": "book",
    "Business Strategy Book": "book", "Poetry Collection": "book", "Fantasy Novel": "fantasy,book",
    "Yoga Mat": "yoga,mat", "Dumbbell Set": "dumbbell", "Camping Tent": "camping,tent",
    "Cycling Helmet": "bike,helmet", "Water Bottle": "water,bottle", "Resistance Bands": "resistance,band",
    "Hiking Backpack": "hiking,backpack", "Football": "football", "Badminton Racket": "badminton,racket",
    "Fitness Tracker": "fitness,tracker",
    "Face Moisturizer": "skincare,cream", "Electric Toothbrush": "toothbrush", "Hair Dryer": "hair,dryer",
    "Sunscreen SPF 50": "sunscreen", "Beard Trimmer": "beard,trimmer", "Shampoo": "shampoo",
    "Perfume": "perfume,bottle", "Lip Balm Set": "lip,balm", "Skincare Kit": "skincare", "Nail Care Kit": "nail,care",
}
SORTED_ITEMS = sorted(ITEM_IMAGE_KEYWORDS.keys(), key=len, reverse=True)
DEFAULT_KEYWORD = "product"


def keyword_for_title(title: str) -> str:
    for item in SORTED_ITEMS:
        if item in title:
            return ITEM_IMAGE_KEYWORDS[item]
    return DEFAULT_KEYWORD


def fix_images():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        updated = 0
        for p in products:
            keyword = keyword_for_title(p.title)
            p.image_url = f"https://loremflickr.com/400/400/{keyword}?lock={p.id}"
            updated += 1
        db.commit()
        print(f"Updated image_url for {updated} products with item-specific keywords.")
    finally:
        db.close()


if __name__ == "__main__":
    fix_images()
