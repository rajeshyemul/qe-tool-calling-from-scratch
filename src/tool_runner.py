from src.tools.product_tools import get_product_price


def execute_tool_call(tool_name: str, arguments: dict):
    """
    Dispatch a tool call to the correct implementation.
    """
    if tool_name == "get_product_price":
        return get_product_price(arguments["product_id"])

    raise ValueError(f"Unknown tool: {tool_name}")
