import re


def decide_tool_call(user_question: str):
    """
    A tiny learning stub for tool selection.

    This is intentionally simple: we are not using a real model yet.
    The goal is to make the request/decision flow visible and deterministic.
    """
    text = user_question.lower().strip()

    if "price" in text or "cost" in text:
        match = re.search(r"p\d+", text)
        if not match:
            return {
                "tool": None,
                "arguments": {},
                "reason": "No product id found in the question."
            }

        product_id = match.group(0).upper()
        return {
            "tool": "get_product_price",
            "arguments": {"product_id": product_id},
            "reason": "The user asks for product pricing."
        }

    return {
        "tool": None,
        "arguments": {},
        "reason": "This request does not require a product tool."
    }
