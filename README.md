# QE Tool Calling From Scratch

Repository: https://github.com/rajeshyemul/qe-tool-calling-from-scratch

A hands-on learning project that builds tool calling in clear, testable stages: first with deterministic selection and response generation, then with a local Qwen model served by Ollama.

## Learning progression

### V1 — single deterministic tool

V1 introduced one product-price tool and a small local catalog, along with tests for expected failures.

Tag: `v1-tool-calling-baseline`

### V2 — deterministic multi-tool flow

The deterministic path demonstrates three separate tools:

- `get_product(product_id)` — basic product details
- `get_product_price(product_id)` — price and currency
- `check_inventory(product_id)` — stock status and quantity

A rule-based selector chooses zero or more tools. The application validates the complete plan before it dispatches calls, collects results, and uses a deterministic response generator.

### V2.5 — real local LLM tool calling

The Ollama path uses Qwen to select tools, then leaves validation and execution to the Python application. A second Qwen call receives the original question and execution results **without tool definitions** and generates the final answer.

The model proposes calls; the application validates and executes them. The model does not run Python functions directly. This remains tool calling, not an agent: there is no autonomous loop, retries, memory, or planning.

## Choose a run mode

Run commands from the project root.

### Deterministic V2 flow

```bash
python3 main.py
```

This runs the rule-based selector, existing Python tools, and deterministic response generator. It does not call Ollama. Edit `user_question` in `main.py` to try a different question.

### Local Ollama/Qwen end-to-end flow

Prerequisites:

- Ollama installed and running locally
- The `qwen3.5:latest` model pulled in Ollama

Run:

```bash
python3 ollama_execution_demo.py
```

This prints Qwen's raw tool calls, sends the normalized calls through the existing application validator and runner, displays the tool results, then prints the response from the second Qwen call. The second request is sent with no tools.

The default endpoint is `http://localhost:11434`; the default model is `qwen3.5:latest`. Override them using `OLLAMA_HOST` and `OLLAMA_MODEL`, respectively.

For a selector-only preview that does not execute tools, run:

```bash
python3 ollama_tool_call_preview.py
```

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

The test suite covers the tools, deterministic decisions and responses, Ollama request/response handling, call normalization, validation-before-execution, multi-tool dispatch, and the two-call response handoff. Tests use mocked Ollama responses and do not require network access.

## Project structure

```text
qe-tool-calling-from-scratch/
├── data/
│   └── products.json
├── src/
│   ├── llm/
│   │   ├── client.py                 # deterministic selector
│   │   ├── ollama_client.py          # Ollama tool selection and final response
│   │   └── response.py               # deterministic response generator
│   ├── tools/
│   │   └── product_tools.py          # local product data functions
│   └── tool_runner.py                # validation, dispatch, result collection
├── tests/
├── main.py                           # deterministic V2 entry point
├── ollama_execution_demo.py          # real local LLM end-to-end entry point
├── ollama_tool_call_preview.py       # tool-call preview only
└── requirements.txt
```

## Current checkpoint

V2 and V2.5 tool-calling flows are implemented and tested. The next learning stage is a separate Single Agent project; this repository intentionally does not add an agent loop.

Suggested checkpoint tags:

- `v1-tool-calling-baseline`
- `v2-multi-tool-selection`
- `v2.5-ollama-tool-calling`
