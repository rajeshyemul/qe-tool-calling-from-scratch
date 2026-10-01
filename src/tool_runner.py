from src.tools.product_tools import (
    check_inventory,
    get_product,
    get_product_price,
)


TOOL_FUNCTIONS = {
    "get_product": get_product,
    "get_product_price": get_product_price,
    "check_inventory": check_inventory,
}


def _validate_tool_call(tool_call: dict):
    if not isinstance(tool_call, dict):
        raise ValueError("Each tool call must be an object.")

    tool_name = tool_call.get("tool")
    if not isinstance(tool_name, str) or tool_name not in TOOL_FUNCTIONS:
        raise ValueError(f"Unknown tool: {tool_name}")

    arguments = tool_call.get("arguments")
    if not isinstance(arguments, dict):
        raise ValueError(f"Arguments for {tool_name} must be an object.")

    product_id = arguments.get("product_id")
    if not isinstance(product_id, str) or not product_id.strip():
        raise ValueError(f"{tool_name} requires a non-empty product_id.")

    return tool_name, arguments


def execute_tool_call(tool_name: str, arguments: dict):
    """
    Dispatch a tool call to the correct implementation.
    """
    validated_tool_name, validated_arguments = _validate_tool_call({
        "tool": tool_name,
        "arguments": arguments,
    })
    return TOOL_FUNCTIONS[validated_tool_name](validated_arguments["product_id"])


def execute_tool_calls(tool_calls: list[dict]):
    """Execute an ordered tool-call plan and collect each call's outcome.

    The entire plan is validated before any tool runs. A runtime failure for
    one call is recorded in that call's result, and later calls still run.
    """
    if not isinstance(tool_calls, list):
        raise ValueError("tool_calls must be a list.")

    validated_calls = [_validate_tool_call(tool_call) for tool_call in tool_calls]
    results = []

    for tool_name, arguments in validated_calls:
        try:
            result = execute_tool_call(tool_name, arguments)
        except Exception as error:
            results.append({
                "tool": tool_name,
                "arguments": arguments,
                "error": str(error),
            })
        else:
            results.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": result,
            })

    return results
