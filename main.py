from src.llm.client import decide_tool_call
from src.tool_runner import execute_tool_call


def run_demo(user_question: str):
    tool_decision = decide_tool_call(user_question)
    print("STEP 1: LLM decides tool call")
    print(tool_decision)

    if tool_decision["tool"] is None:
        print("No tool call needed.")
        return

    tool_result = execute_tool_call(tool_decision["tool"], tool_decision["arguments"])
    print("STEP 2: Application executes the tool")
    print(tool_result)

    final_answer = (
        f"{tool_result['name']} costs ₹{tool_result['price']} "
        f"({tool_result['currency']}) and there are {tool_result['stock']} units in stock."
    )

    print("STEP 3: LLM responds with final answer")
    print(final_answer)


if __name__ == "__main__":
    user_question = "What is the price of product Z999?"
    run_demo(user_question)
