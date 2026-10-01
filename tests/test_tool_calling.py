import unittest
from unittest.mock import patch

from src.llm.client import decide_tool_call
from src.tool_runner import execute_tool_call
from src.tools.product_tools import get_product_price


class TestToolCalling(unittest.TestCase):
    def test_get_product_price_returns_expected_product(self):
        result = get_product_price("P1001")
        self.assertEqual(result["product_id"], "P1001")
        self.assertEqual(result["name"], "Running Shoes")
        self.assertEqual(result["price"], 4999)

    def test_execute_tool_call_dispatches_correct_tool(self):
        result = execute_tool_call("get_product_price", {"product_id": "P1002"})
        self.assertEqual(result["product_id"], "P1002")
        self.assertEqual(result["price"], 1499)

    def test_missing_product_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_product_price("Z999")

    def test_missing_product_id_is_rejected_before_tool_call(self):
        result = decide_tool_call("What is the price of the product?")
        self.assertIsNone(result["tool"])
        self.assertIn("No product id found", result["reason"])

    def test_question_not_needing_tool_returns_no_tool(self):
        result = decide_tool_call("What is an e-commerce website?")
        self.assertIsNone(result["tool"])
        self.assertIn("does not require", result["reason"])

    def test_invalid_product_id_is_rejected(self):
        with self.assertRaises(ValueError):
            get_product_price("")

    def test_tool_execution_failure_propagates_exception(self):
        with patch("src.tool_runner.get_product_price", side_effect=Exception("Product database unavailable")):
            with self.assertRaisesRegex(Exception, "Product database unavailable"):
                execute_tool_call("get_product_price", {"product_id": "P1001"})


if __name__ == "__main__":
    unittest.main()
