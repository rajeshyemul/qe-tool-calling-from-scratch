import re


def decide_tool_calls(user_question: str):
    """
    A tiny learning stub that returns a structured tool-call plan.

    This is intentionally simple: we are not using a real model yet.
    The goal is to make the request/decision flow visible and deterministic.
    """
    text = user_question.lower().strip()
    product_id_match = re.search(r"\bp\d+\b", text)

    wants_product = any(
        phrase in text
        for phrase in ("tell me about", "details", "information", "name")
    )
    wants_price = "price" in text or "cost" in text
    wants_inventory = any(
        phrase in text
        for phrase in (
            "stock",
            "inventory",
            "in stock",
            "available",
            "availability",
            "how many",
            "quantity",
        )
    )

    if not any((wants_product, wants_price, wants_inventory)):
        return {
            "tool_calls": [],
            "reason": "This request does not require a product tool.",
        }

    if not product_id_match:
        return {
            "tool_calls": [],
            "reason": "No product id found in the question.",
        }

    product_id = product_id_match.group(0).upper()
    tool_calls = []

    # Use a stable order so equivalent requests produce predictable plans.
    if wants_product:
        tool_calls.append({
            "tool": "get_product",
            "arguments": {"product_id": product_id},
        })
    if wants_price:
        tool_calls.append({
            "tool": "get_product_price",
            "arguments": {"product_id": product_id},
        })
    if wants_inventory:
        tool_calls.append({
            "tool": "check_inventory",
            "arguments": {"product_id": product_id},
        })

    return {
        "tool_calls": tool_calls,
        "reason": "Selected tools based on the product information requested.",
    }
