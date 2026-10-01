import unittest
from unittest.mock import patch

from src.llm.client import decide_tool_calls
from src.tool_runner import execute_tool_call, execute_tool_calls
from src.tools.product_tools import (
    check_inventory,
    get_product,
    get_product_price,
)


class TestToolCalling(unittest.TestCase):
    def test_get_product_price_returns_expected_product(self):
        result = get_product_price("P1001")
        self.assertEqual(result["product_id"], "P1001")
        self.assertEqual(result["price"], 4999)
        self.assertEqual(result["currency"], "INR")

    def test_check_inventory_returns_stock_status_and_quantity(self):
        result = check_inventory("P1001")
        self.assertEqual(result, {
            "product_id": "P1001",
            "in_stock": True,
            "quantity": 12,
        })

    def test_get_product_returns_basic_information(self):
        result = get_product("P1001")
        self.assertEqual(result, {
            "product_id": "P1001",
            "name": "Running Shoes",
            "category": "Footwear",
        })

    def test_execute_tool_call_dispatches_correct_tool(self):
        result = execute_tool_call("get_product_price", {"product_id": "P1002"})
        self.assertEqual(result["product_id"], "P1002")
        self.assertEqual(result["price"], 1499)

    def test_execute_tool_call_dispatches_each_supported_tool(self):
        product = execute_tool_call("get_product", {"product_id": "P1001"})
        inventory = execute_tool_call("check_inventory", {"product_id": "P1001"})
        self.assertEqual(product["name"], "Running Shoes")
        self.assertEqual(inventory["quantity"], 12)

    def test_execute_tool_calls_returns_empty_list_for_empty_plan(self):
        self.assertEqual(execute_tool_calls([]), [])

    def test_execute_tool_calls_returns_one_structured_result(self):
        results = execute_tool_calls([{
            "tool": "get_product_price",
            "arguments": {"product_id": "P1001"},
        }])
        self.assertEqual(results, [{
            "tool": "get_product_price",
            "arguments": {"product_id": "P1001"},
            "result": {
                "product_id": "P1001",
                "price": 4999,
                "currency": "INR",
            },
        }])

    def test_execute_tool_calls_preserves_order_and_collects_multiple_results(self):
        plan = decide_tool_calls("What is the price of P1001 and is it in stock?")
        results = execute_tool_calls(plan["tool_calls"])
        self.assertEqual(
            [result["tool"] for result in results],
            ["get_product_price", "check_inventory"],
        )
        self.assertEqual(results[0]["result"]["price"], 4999)
        self.assertEqual(results[1]["result"]["quantity"], 12)

    def test_execute_tool_calls_rejects_unknown_tool_before_running_any_call(self):
        from unittest.mock import Mock

        price_tool = Mock(return_value={"price": 4999})
        tool_functions = {"get_product_price": price_tool}
        plan = [
            {
                "tool": "get_product_price",
                "arguments": {"product_id": "P1001"},
            },
            {"tool": "not_a_tool", "arguments": {"product_id": "P1001"}},
        ]

        with patch("src.tool_runner.TOOL_FUNCTIONS", tool_functions):
            with self.assertRaisesRegex(ValueError, "Unknown tool"):
                execute_tool_calls(plan)

        price_tool.assert_not_called()

    def test_execute_tool_calls_rejects_missing_product_id(self):
        with self.assertRaisesRegex(ValueError, "product_id"):
            execute_tool_calls([{
                "tool": "get_product_price",
                "arguments": {},
            }])

    def test_execute_tool_calls_records_failure_and_continues(self):
        from unittest.mock import Mock

        failing_tool = Mock(side_effect=Exception("Product database unavailable"))
        succeeding_tool = Mock(return_value={"quantity": 12})
        tool_functions = {
            "get_product_price": failing_tool,
            "check_inventory": succeeding_tool,
        }
        plan = [
            {
                "tool": "get_product_price",
                "arguments": {"product_id": "P1001"},
            },
            {
                "tool": "check_inventory",
                "arguments": {"product_id": "P1001"},
            },
        ]

        with patch("src.tool_runner.TOOL_FUNCTIONS", tool_functions):
            results = execute_tool_calls(plan)

        self.assertEqual(results[0]["error"], "Product database unavailable")
        self.assertEqual(results[1]["result"], {"quantity": 12})
        succeeding_tool.assert_called_once_with("P1001")

    def test_missing_product_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_product_price("Z999")

    def test_missing_product_id_is_rejected_before_tool_call(self):
        result = decide_tool_calls("What is the price of the product?")
        self.assertEqual(result["tool_calls"], [])
        self.assertIn("No product id found", result["reason"])

    def test_question_not_needing_tool_returns_no_tool(self):
        result = decide_tool_calls("What is an e-commerce website?")
        self.assertEqual(result["tool_calls"], [])
        self.assertIn("does not require", result["reason"])

    def test_price_question_selects_price_tool(self):
        result = decide_tool_calls("What is the price of P1001?")
        self.assertEqual(result["tool_calls"], [{
            "tool": "get_product_price",
            "arguments": {"product_id": "P1001"},
        }])

    def test_inventory_question_selects_inventory_tool(self):
        result = decide_tool_calls("How many P1001 are available?")
        self.assertEqual(result["tool_calls"], [{
            "tool": "check_inventory",
            "arguments": {"product_id": "P1001"},
        }])

    def test_product_information_question_selects_product_tool(self):
        result = decide_tool_calls("Tell me about P1001.")
        self.assertEqual(result["tool_calls"], [{
            "tool": "get_product",
            "arguments": {"product_id": "P1001"},
        }])

    def test_question_with_two_intents_selects_both_tools(self):
        result = decide_tool_calls("What is the price of P1001 and is it in stock?")
        self.assertEqual(result["tool_calls"], [
            {
                "tool": "get_product_price",
                "arguments": {"product_id": "P1001"},
            },
            {
                "tool": "check_inventory",
                "arguments": {"product_id": "P1001"},
            },
        ])

    def test_unknown_product_id_can_still_be_selected(self):
        result = decide_tool_calls("What is the price of P9999?")
        self.assertEqual(result["tool_calls"][0]["arguments"]["product_id"], "P9999")

    def test_invalid_product_id_is_rejected(self):
        with self.assertRaises(ValueError):
            get_product_price("")

    def test_tool_execution_failure_propagates_exception(self):
        from unittest.mock import Mock

        failing_tool = Mock(side_effect=Exception("Product database unavailable"))
        with patch("src.tool_runner.TOOL_FUNCTIONS", {"get_product_price": failing_tool}):
            with self.assertRaisesRegex(Exception, "Product database unavailable"):
                execute_tool_call("get_product_price", {"product_id": "P1001"})


if __name__ == "__main__":
    unittest.main()
