import json
import os
from urllib.request import Request, urlopen


DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3.5:latest"
OLLAMA_TIMEOUT_SECONDS = 300
NO_TOOL_RESULTS_RESPONSE = "I don't have tool results to answer that question."

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": "Get basic product information such as name and category.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "string"}},
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_price",
            "description": "Get the price and currency for a product.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "string"}},
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Get stock availability and quantity for a product.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "string"}},
                "required": ["product_id"],
            },
        },
    },
]


def _post_chat(request_body: dict) -> dict:
    ollama_host = os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/")
    request = Request(
        f"{ollama_host}/api/chat",
        data=json.dumps(request_body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
        ollama_response = json.loads(response.read().decode("utf-8"))

    if not isinstance(ollama_response, dict):
        raise ValueError("Ollama returned an invalid response object.")

    message = ollama_response.get("message")
    if not isinstance(message, dict):
        raise ValueError("Ollama response did not contain a message object.")

    return message


def decide_tool_calls_with_ollama(user_question: str) -> dict:
    """Ask local Ollama to select tools and preserve its raw tool-call output.

    This function does not validate or execute the selected tools. Those remain
    application responsibilities handled after this decision is inspected.
    """
    if not isinstance(user_question, str) or not user_question.strip():
        raise ValueError("user_question must be a non-empty string.")

    model = os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    request_body = {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": user_question}],
        "tools": TOOL_DEFINITIONS,
    }
    message = _post_chat(request_body)

    raw_tool_calls = message.get("tool_calls", [])
    if not isinstance(raw_tool_calls, list):
        raise ValueError("Ollama message tool_calls must be a list.")

    tool_calls = []
    for raw_tool_call in raw_tool_calls:
        if not isinstance(raw_tool_call, dict):
            raise ValueError("Each Ollama tool call must be an object.")
        function_call = raw_tool_call.get("function")
        if not isinstance(function_call, dict):
            raise ValueError("Each Ollama tool call must contain a function object.")

        tool_calls.append({
            "tool": function_call.get("name"),
            "arguments": function_call.get("arguments", {}),
        })

    return {
        "model": model,
        "raw_tool_calls": raw_tool_calls,
        "tool_calls": tool_calls,
    }


def generate_response_with_ollama(
    user_question: str,
    execution_results: list[dict],
) -> str:
    """Ask Ollama to answer from execution evidence, without giving it tools."""
    if not isinstance(user_question, str) or not user_question.strip():
        raise ValueError("user_question must be a non-empty string.")
    if not isinstance(execution_results, list):
        raise ValueError("execution_results must be a list.")
    if not execution_results:
        return NO_TOOL_RESULTS_RESPONSE

    model = os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    request_body = {
        "model": model,
        "stream": False,
        "think": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer the user's question using only facts in the supplied "
                    "tool execution results. Do not use outside knowledge, infer "
                    "missing facts, or claim a failed tool returned data. If a "
                    "requested fact is missing or its tool failed, say that it "
                    "could not be retrieved. Return only a concise final answer; "
                    "do not include reasoning or analysis."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{user_question}\n\n"
                    "Tool execution results (JSON evidence):\n"
                    f"{json.dumps(execution_results, ensure_ascii=False)}"
                ),
            },
        ],
    }
    message = _post_chat(request_body)
    response_text = message.get("content")
    if not isinstance(response_text, str) or not response_text.strip():
        raise ValueError("Ollama returned an empty final response.")

    return response_text.strip()