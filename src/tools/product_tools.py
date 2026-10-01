import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "products.json"

with DATA_FILE.open("r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)


def _find_product(product_id: str):
    for product in PRODUCTS:
        if product["product_id"] == product_id:
            return product

    raise ValueError(f"Product {product_id} was not found.")


def get_product_price(product_id: str):
    """
    Return pricing information for a product.
    """
    product = _find_product(product_id)
    return {
        "product_id": product["product_id"],
        "price": product["price"],
        "currency": product["currency"],
    }


def check_inventory(product_id: str):
    """Return stock availability and quantity for a product."""
    product = _find_product(product_id)
    return {
        "product_id": product["product_id"],
        "in_stock": product["stock"] > 0,
        "quantity": product["stock"],
    }


def get_product(product_id: str):
    """Return basic descriptive information for a product."""
    product = _find_product(product_id)
    return {
        "product_id": product["product_id"],
        "name": product["name"],
        "category": product["category"],
    }
