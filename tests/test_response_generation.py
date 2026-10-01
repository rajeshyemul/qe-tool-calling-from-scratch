import unittest

from src.llm.response import generate_response


class TestResponseGeneration(unittest.TestCase):
    def test_generates_answer_from_product_price_and_inventory_results(self):
        execution_results = [
            {
                "tool": "get_product",
                "arguments": {"product_id": "P1001"},
                "result": {
                    "product_id": "P1001",
                    "name": "Running Shoes",
                    "category": "Footwear",
                },
            },
            {
                "tool": "get_product_price",
                "arguments": {"product_id": "P1001"},
                "result": {
                    "product_id": "P1001",
                    "price": 4999,
                    "currency": "INR",
                },
            },
            {
                "tool": "check_inventory",
                "arguments": {"product_id": "P1001"},
                "result": {
                    "product_id": "P1001",
                    "in_stock": True,
                    "quantity": 12,
                },
            },
        ]

        response = generate_response("Tell me about P1001, its price and stock.", execution_results)

        self.assertEqual(
            response,
            "Running Shoes (P1001) is in the Footwear category. "
            "Running Shoes (P1001) costs ₹4,999. "
            "Running Shoes (P1001) is in stock (12 units).",
        )
        self.assertNotIn("popular", response)
        self.assertNotIn("beginners", response)

    def test_generates_partial_answer_without_guessing_failed_inventory(self):
        execution_results = [
            {
                "tool": "get_product_price",
                "arguments": {"product_id": "P1001"},
                "result": {
                    "product_id": "P1001",
                    "price": 4999,
                    "currency": "INR",
                },
            },
            {
                "tool": "check_inventory",
                "arguments": {"product_id": "P1001"},
                "error": "Product database unavailable",
            },
        ]

        response = generate_response("What is the price and stock for P1001?", execution_results)

        self.assertEqual(
            response,
            "P1001 costs ₹4,999. "
            "I couldn't retrieve inventory information for P1001.",
        )
        self.assertNotIn("in stock", response)
        self.assertNotIn("out of stock", response)

    def test_handles_explicit_success_flags(self):
        execution_results = [{
            "tool": "get_product_price",
            "success": True,
            "result": {
                "product_id": "P1001",
                "price": 4999,
                "currency": "INR",
            },
        }]

        self.assertEqual(
            generate_response("What is the price of P1001?", execution_results),
            "P1001 costs ₹4,999.",
        )

    def test_empty_results_produce_no_data_response(self):
        self.assertEqual(
            generate_response("What is the price of P1001?", []),
            "I don't have tool results to answer that question.",
        )

    def test_does_not_infer_currency_when_currency_is_missing(self):
        response = generate_response("What is the price of P1001?", [{
            "tool": "get_product_price",
            "arguments": {"product_id": "P1001"},
            "result": {"product_id": "P1001", "price": 4999},
        }])

        self.assertEqual(response, "P1001 costs 4,999.")
        self.assertNotIn("₹", response)

    def test_rejects_unknown_tool_in_execution_results(self):
        with self.assertRaisesRegex(ValueError, "Unknown tool"):
            generate_response("Question", [{
                "tool": "unknown_tool",
                "result": {},
            }])


if __name__ == "__main__":
    unittest.main()