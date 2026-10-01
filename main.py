from src.llm.client import decide_tool_calls
from src.llm.response import generate_response
from src.tool_runner import execute_tool_calls


def run_demo(user_question: str):
    tool_decision = decide_tool_calls(user_question)
    print("STEP 1: Select zero or more tools")
    print(tool_decision)

    if tool_decision["tool_calls"]:
        tool_results = execute_tool_calls(tool_decision["tool_calls"])
        print("STEP 2: Application executes the selected tools")
        print(tool_results)
    else:
        tool_results = []
        print("No tool calls selected.")

    final_response = generate_response(user_question, tool_results)
    print("STEP 3: Deterministic response generator answers from tool results")
    print(final_response)


if __name__ == "__main__":
    user_question = "What is the price of P1001 and is it in stock?"
    run_demo(user_question)
