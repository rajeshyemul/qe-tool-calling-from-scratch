from pprint import pprint

from src.llm.ollama_client import decide_tool_calls_with_ollama


def main():
    user_question = "What is the price of P1001 and is it in stock?"
    decision = decide_tool_calls_with_ollama(user_question)

    print(f"Model: {decision['model']}")
    print("Raw model tool calls (before application validation or execution):")
    pprint(decision["raw_tool_calls"], sort_dicts=False)
    print("Normalized calls for the application validator:")
    pprint(decision["tool_calls"], sort_dicts=False)
    print("No tools were executed by this preview.")


if __name__ == "__main__":
    main()