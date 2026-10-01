from pprint import pprint

from src.llm.ollama_client import (
    decide_tool_calls_with_ollama,
    generate_response_with_ollama,
)
from src.tool_runner import execute_tool_calls


def run_demo(user_question: str):
    decision = decide_tool_calls_with_ollama(user_question)

    print(f"Model: {decision['model']}")
    print("Raw model tool calls (before application validation or execution):")
    pprint(decision["raw_tool_calls"], sort_dicts=False)
    print("Normalized calls passed to the application validator:")
    pprint(decision["tool_calls"], sort_dicts=False)

    execution_results = execute_tool_calls(decision["tool_calls"])
    print("Execution results:")
    pprint(execution_results, sort_dicts=False)

    final_answer = generate_response_with_ollama(user_question, execution_results)
    print("Final answer from Ollama (second call, no tools provided):")
    print(final_answer)

    return decision, execution_results, final_answer


def main():
    user_question = "What is the price of P1001 and is it in stock?"
    run_demo(user_question)


if __name__ == "__main__":
    main()