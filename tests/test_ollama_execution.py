import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from ollama_execution_demo import run_demo
from src.tool_runner import execute_tool_calls as run_tools


class TestOllamaExecutionHandoff(unittest.TestCase):
    def test_normalized_ollama_calls_reach_existing_runner(self):
        decision = {
            "model": "qwen3.5:latest",
            "raw_tool_calls": [
                {"function": {"name": "get_product_price", "arguments": {"product_id": "P1001"}}},
                {"function": {"name": "check_inventory", "arguments": {"product_id": "P1001"}}},
            ],
            "tool_calls": [
                {"tool": "get_product_price", "arguments": {"product_id": "P1001"}},
                {"tool": "check_inventory", "arguments": {"product_id": "P1001"}},
            ],
        }
        output = io.StringIO()
        captured_execution_results = []

        def execute_after_raw_calls_are_printed(tool_calls):
            self.assertIn("Raw model tool calls", output.getvalue())
            self.assertEqual(tool_calls, decision["tool_calls"])
            results = run_tools(tool_calls)
            captured_execution_results.extend(results)
            return results

        def generate_after_execution(question, execution_results):
            self.assertEqual(question, "What is the price of P1001 and is it in stock?")
            self.assertEqual(execution_results, captured_execution_results)
            self.assertIn("Execution results:", output.getvalue())
            return "P1001 costs ₹4,999 and is in stock with 12 units."

        with (
            patch("ollama_execution_demo.decide_tool_calls_with_ollama", return_value=decision),
            patch("ollama_execution_demo.execute_tool_calls", side_effect=execute_after_raw_calls_are_printed),
            patch("ollama_execution_demo.generate_response_with_ollama", side_effect=generate_after_execution),
            redirect_stdout(output),
        ):
            returned_decision, execution_results, final_answer = run_demo(
                "What is the price of P1001 and is it in stock?"
            )

        self.assertIs(returned_decision, decision)
        self.assertEqual(
            [result["tool"] for result in execution_results],
            ["get_product_price", "check_inventory"],
        )
        self.assertEqual(execution_results[0]["result"]["price"], 4999)
        self.assertEqual(execution_results[1]["result"]["quantity"], 12)
        self.assertEqual(final_answer, "P1001 costs ₹4,999 and is in stock with 12 units.")
        self.assertIn("Final answer from Ollama (second call, no tools provided):", output.getvalue())
        self.assertIn(final_answer, output.getvalue())

    def test_invalid_ollama_call_is_rejected_before_any_tool_executes(self):
        decision = {
            "model": "qwen3.5:latest",
            "raw_tool_calls": [],
            "tool_calls": [
                {"tool": "get_product_price", "arguments": {"product_id": "P1001"}},
                {"tool": "not_a_real_tool", "arguments": {"product_id": "P1001"}},
            ],
        }
        price_tool = Mock(return_value={"price": 4999})
        output = io.StringIO()

        with (
            patch("ollama_execution_demo.decide_tool_calls_with_ollama", return_value=decision),
            patch("src.tool_runner.TOOL_FUNCTIONS", {"get_product_price": price_tool}),
            redirect_stdout(output),
        ):
            with self.assertRaisesRegex(ValueError, "Unknown tool"):
                run_demo("What is the price of P1001?")

        price_tool.assert_not_called()


if __name__ == "__main__":
    unittest.main()