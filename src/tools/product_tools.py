import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "products.json"

with DATA_FILE.open("r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


def get_product_price(product_id: str):
    """
    Return the product data for a given product ID.
    """
    for product in PRODUCTS:
        if product["product_id"] == product_id:
            return {
                "product_id": product["product_id"],
                "name": product["name"],
                "price": product["price"],
                "currency": product["currency"],
                "stock": product["stock"],
            }

    raise ValueError(f"Product {product_id} was not found.")
