import math


TOOL_NAMES = {
    "get_product",
    "get_product_price",
    "check_inventory",
}
TOOL_FAILURE_LABELS = {
    "get_product": "product details",
    "get_product_price": "price",
    "check_inventory": "inventory information",
}


def _is_success(execution_result: dict) -> bool:
    if "success" in execution_result:
        success = execution_result["success"]
        if not isinstance(success, bool):
            raise ValueError("success must be a boolean when provided.")
        return success

    if "error" in execution_result:
        return False
    if "result" in execution_result:
        return True

    raise ValueError("Each execution result must contain result or error data.")


def _product_id(execution_result: dict, tool_result: dict | None = None):
    if tool_result is not None:
        product_id = tool_result.get("product_id")
        if isinstance(product_id, str) and product_id:
            return product_id

    arguments = execution_result.get("arguments", {})
    product_id = arguments.get("product_id") if isinstance(arguments, dict) else None
    return product_id if isinstance(product_id, str) and product_id else None


def _format_product_label(product_id: str | None, product_names: dict) -> str:
    if product_id is None:
        return "The product"

    name = product_names.get(product_id)
    if name:
        return f"{name} ({product_id})"
    return product_id


def _format_money(price, currency: str | None):
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return None
    if isinstance(price, float) and not math.isfinite(price):
        return None

    formatted_price = format(price, ",")
    if currency == "INR":
        return f"₹{formatted_price}"
    if isinstance(currency, str) and currency:
        return f"{formatted_price} {currency}"
    return formatted_price


def generate_response(question: str, execution_results: list[dict]) -> str:
    """Create a deterministic answer using only facts in execution results.

    The question remains part of the interface for a future model-backed
    implementation. This stub deliberately bases its claims only on tool data.
    """
    if not isinstance(question, str):
        raise ValueError("question must be a string.")
    if not isinstance(execution_results, list):
        raise ValueError("execution_results must be a list.")
    if not execution_results:
        return "I don't have tool results to answer that question."

    normalized_results = []
    for execution_result in execution_results:
        if not isinstance(execution_result, dict):
            raise ValueError("Each execution result must be an object.")

        tool_name = execution_result.get("tool")
        if not isinstance(tool_name, str) or tool_name not in TOOL_NAMES:
            raise ValueError(f"Unknown tool in execution results: {tool_name}")

        succeeded = _is_success(execution_result)
        tool_result = execution_result.get("result") if succeeded else None
        if succeeded and not isinstance(tool_result, dict):
            raise ValueError("A successful execution result must contain an object result.")

        normalized_results.append((execution_result, tool_name, tool_result))

    product_names = {}
    for execution_result, tool_name, tool_result in normalized_results:
        if tool_name != "get_product":
            continue
        product_id = _product_id(execution_result, tool_result)
        name = tool_result.get("name")
        if product_id is not None and isinstance(name, str) and name:
            product_names[product_id] = name

    statements = []
    for execution_result, tool_name, tool_result in normalized_results:
        product_id = _product_id(execution_result, tool_result)
        product_label = _format_product_label(product_id, product_names)

        if tool_result is None:
            data_label = TOOL_FAILURE_LABELS[tool_name]
            if product_id is None:
                statements.append(f"I couldn't retrieve {data_label}.")
            else:
                statements.append(f"I couldn't retrieve {data_label} for {product_id}.")
            continue

        if tool_name == "get_product":
            category = tool_result.get("category")
            name = tool_result.get("name")
            if isinstance(category, str) and category:
                if isinstance(name, str) and name and product_id is not None:
                    statements.append(
                        f"{name} ({product_id}) is in the {category} category."
                    )
                elif product_id is not None:
                    statements.append(f"{product_id} is in the {category} category.")
            elif isinstance(name, str) and name and product_id is not None:
                statements.append(f"The product name for {product_id} is {name}.")

        elif tool_name == "get_product_price":
            price = tool_result.get("price")
            currency = tool_result.get("currency")
            formatted_price = _format_money(price, currency)
            if formatted_price is not None:
                statements.append(f"{product_label} costs {formatted_price}.")

        elif tool_name == "check_inventory":
            in_stock = tool_result.get("in_stock")
            quantity = tool_result.get("quantity")
            if isinstance(in_stock, bool):
                availability = "is in stock" if in_stock else "is out of stock"
                if isinstance(quantity, int) and not isinstance(quantity, bool) and quantity >= 0:
                    unit = "unit" if quantity == 1 else "units"
                    statements.append(
                        f"{product_label} {availability} ({quantity} {unit})."
                    )
                else:
                    statements.append(f"{product_label} {availability}.")
            elif isinstance(quantity, int) and not isinstance(quantity, bool) and quantity >= 0:
                unit = "unit" if quantity == 1 else "units"
                statements.append(f"{product_label} has {quantity} {unit} recorded.")

    if not statements:
        return "The tool results did not contain supported facts to answer from."

    return " ".join(statements)