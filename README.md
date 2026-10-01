# QE Tool Calling From Scratch

Repository: https://github.com/rajeshyemul/qe-tool-calling-from-scratch

This project is the next step in the learning journey after RAG.

It intentionally stays small and explicit. The goal is not to build a full agent or production workflow yet. The goal is to understand the mechanics of tool calling in a way that is visible, testable, and easy to reason about.

## What this project teaches

This project teaches the core pattern behind tool-calling systems:

- the model decides which tool to call
- the application executes the tool
- the function returns real data
- the result is sent back to the model
- the model turns that result into a final answer

This is the foundation for later stages such as single-agent loops, planning, memory, MCP, and multi-agent systems.

## Learning boundary

This repository is intentionally limited to the following scope:

- one product tool
- one deterministic catalog
- no agents
- no memory
- no MCP
- no multi-agent orchestration
- no external API integration

This project is a controlled interaction loop, not a full autonomous system.

## Version 1: single tool

The first milestone is a single tool:

- `get_product_price(product_id)`

Example user question:

> What is the price of product P1001?

The flow is conceptually:

```text
User request
   ↓
LLM decides: call get_product_price(P1001)
   ↓
Application executes the tool
   ↓
Tool returns product data
   ↓
LLM generates final answer
```

This is the baseline for the learning project.

## Failure lab

This repo also includes a deliberate failure-learning phase.

It tests:

- missing product ID
- unknown product
- non-tool question
- invalid input
- tool execution failure

The purpose is to understand how tool-calling systems fail safely and how the application boundary controls those failures.

## Project structure

```text
qe-tool-calling-from-scratch/
├── data/
│   └── products.json
├── src/
│   ├── __init__.py
│   ├── tool_runner.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py
│   └── tools/
│       ├── __init__.py
│       └── product_tools.py
├── tests/
│   └── test_tool_calling.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── .venv/   # local only; not committed
```

## Why this matters

The critical distinction is:

- the model decides what to do
- the application executes the action
- the model interprets the result

That separation is the heart of tool calling, and it becomes the basis for single-agent systems later.

## Run the demo

```bash
python3 main.py
```

Current demo question:

```text
What is the price of product P1001?
```

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

## Status

This repository is currently at the V1 baseline for tool calling.

The next stage is the planned V2 bridge:

- multiple tools
- tool selection among alternatives
- combined results from more than one tool

After that, the next conceptual stage is the single-agent loop.

## Repository intent

This repository is meant to preserve a clean learning checkpoint before adding complexity.

Each stage is intentionally kept small enough to understand deeply before moving to the next one.

## Recommended versioning

Suggested tags for this project:

- `v1-tool-calling-baseline`
- `v1-tool-calling-failure-lab`
- `v2-multi-tool-selection`
- `v3-single-agent-loop`

This makes it easy to preserve the learning progression as separate, reviewable checkpoints.

