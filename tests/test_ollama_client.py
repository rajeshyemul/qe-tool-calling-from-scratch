import json
import unittest
from unittest.mock import Mock, patch

from src.llm.ollama_client import (
    DEFAULT_OLLAMA_MODEL,
    NO_TOOL_RESULTS_RESPONSE,
    TOOL_DEFINITIONS,
    decide_tool_calls_with_ollama,
    generate_response_with_ollama,
)


class TestOllamaToolCallSelection(unittest.TestCase):
    def test_normalizes_calls_and_preserves_raw_tool_calls(self):
        raw_tool_calls = [
            {
                "id": "call-price",
                "function": {
                    "name": "get_product_price",
                    "arguments": {"product_id": "P1001"},
                },
            },
            {
                "id": "call-stock",
                "function": {
                    "name": "check_inventory",
                    "arguments": {"product_id": "P1001"},
                },
            },
        ]
        response_body = {
            "message": {
                "role": "assistant",
                "content": "",
                "thinking": "Not exposed as part of the decision result.",
                "tool_calls": raw_tool_calls,
            },
        }
        http_response = Mock()
        http_response.__enter__ = Mock(return_value=http_response)
        http_response.__exit__ = Mock(return_value=False)
        http_response.read.return_value = json.dumps(response_body).encode("utf-8")

        with patch("src.llm.ollama_client.urlopen", return_value=http_response) as open_url:
            decision = decide_tool_calls_with_ollama(
                "What is the price of P1001 and is it in stock?"
            )

        self.assertEqual(decision["model"], DEFAULT_OLLAMA_MODEL)
        self.assertEqual(decision["raw_tool_calls"], raw_tool_calls)
        self.assertEqual(decision["tool_calls"], [
            {
                "tool": "get_product_price",
                "arguments": {"product_id": "P1001"},
            },
            {
                "tool": "check_inventory",
                "arguments": {"product_id": "P1001"},
            },
        ])
        self.assertNotIn("thinking", decision)

        request = open_url.call_args.args[0]
        request_body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "http://localhost:11434/api/chat")
        self.assertEqual(request_body["model"], DEFAULT_OLLAMA_MODEL)
        self.assertEqual(request_body["tools"], TOOL_DEFINITIONS)
        self.assertEqual(request_body["messages"][0]["content"],
                         "What is the price of P1001 and is it in stock?")

    def test_returns_empty_call_lists_when_model_selects_no_tools(self):
        http_response = Mock()
        http_response.__enter__ = Mock(return_value=http_response)
        http_response.__exit__ = Mock(return_value=False)
        http_response.read.return_value = b'{"message":{"content":"Hello."}}'

        with patch("src.llm.ollama_client.urlopen", return_value=http_response):
            decision = decide_tool_calls_with_ollama("Hello")

        self.assertEqual(decision["raw_tool_calls"], [])
        self.assertEqual(decision["tool_calls"], [])

    def test_rejects_empty_question_without_calling_ollama(self):
        with patch("src.llm.ollama_client.urlopen") as open_url:
            with self.assertRaisesRegex(ValueError, "non-empty"):
                decide_tool_calls_with_ollama(" ")

        open_url.assert_not_called()

    def test_rejects_response_without_message_object(self):
        http_response = Mock()
        http_response.__enter__ = Mock(return_value=http_response)
        http_response.__exit__ = Mock(return_value=False)
        http_response.read.return_value = b'{"error":"model not found"}'

        with patch("src.llm.ollama_client.urlopen", return_value=http_response):
            with self.assertRaisesRegex(ValueError, "message object"):
                decide_tool_calls_with_ollama("What is the price of P1001?")

    def test_response_request_includes_question_and_results_but_no_tools(self):
        http_response = Mock()
        http_response.__enter__ = Mock(return_value=http_response)
        http_response.__exit__ = Mock(return_value=False)
        http_response.read.return_value = (
            b'{"message":{"content":"P1001 costs 4999 INR and is in stock."}}'
        )

        with patch("src.llm.ollama_client.urlopen", return_value=http_response) as open_url:
            answer = generate_response_with_ollama(
                "What is the price and stock for P1001?",
                [{
                    "tool": "get_product_price",
                    "result": {
                        "product_id": "P1001",
                        "price": 4999,
                        "currency": "INR",
                    },
                }],
            )

        self.assertEqual(answer, "P1001 costs 4999 INR and is in stock.")
        request = open_url.call_args.args[0]
        request_body = json.loads(request.data.decode("utf-8"))
        self.assertNotIn("tools", request_body)
        self.assertEqual(request_body["model"], DEFAULT_OLLAMA_MODEL)
        self.assertIs(request_body["think"], False)
        self.assertEqual(request_body["messages"][0]["role"], "system")
        user_message = request_body["messages"][1]["content"]
        self.assertIn("What is the price and stock for P1001?", user_message)
        self.assertIn('"price": 4999', user_message)

    def test_empty_execution_results_return_no_data_without_another_model_call(self):
        with patch("src.llm.ollama_client.urlopen") as open_url:
            answer = generate_response_with_ollama("Question", [])

        self.assertEqual(answer, NO_TOOL_RESULTS_RESPONSE)
        open_url.assert_not_called()

    def test_rejects_empty_final_response(self):
        http_response = Mock()
        http_response.__enter__ = Mock(return_value=http_response)
        http_response.__exit__ = Mock(return_value=False)
        http_response.read.return_value = b'{"message":{"content":"  "}}'

        with patch("src.llm.ollama_client.urlopen", return_value=http_response):
            with self.assertRaisesRegex(ValueError, "empty final response"):
                generate_response_with_ollama("Question", [{"tool": "get_product"}])


if __name__ == "__main__":
    unittest.main()