# Homework 2 Architecture Summary

## Overview

The system is implemented with the OpenAI Agents SDK as a modular multi-agent workflow. A top-level router agent receives the user request, applies input guardrails, and either returns a structured routing decision for the routing demos or performs a real handoff to a specialist agent for the interactive app.

## Agents

- `Router Agent (few-shot)`: part A classification benchmark
- `Router Agent (structured)`: part B structured routing output with `intent`, `parameters`, and `confidence`
- `Router Agent (handoffs)`: production entrypoint that delegates with SDK handoffs
- `Weather Agent`: owns the live weather tool
- `Math Agent`: translates word problems to formal arithmetic, then calls a deterministic math tool
- `Exchange Rate Agent`: owns the live FX tool
- `General Chat Agent`: cynical but helpful research assistant persona with short responses and safety boundaries

## Tools

- `get_weather_tool`: live weather via `wttr.in`
- `calculate_math_tool`: deterministic AST-based arithmetic evaluator
- `get_exchange_rate_tool`: live exchange rate lookup via `frankfurter.app`

Each tool is implemented as plain deterministic Python first, then exposed to the Agents SDK with `@function_tool`. Weather and FX tools also use tool guardrails to validate arguments and avoid leaking raw upstream errors.

## Handoffs

The main application uses SDK handoffs rather than manual `if/else` branching between specialists. The router is configured with four explicit handoff options, one per specialist agent. Handoff history is filtered with `remove_all_tools` so downstream specialists see cleaner context without low-signal tool call clutter.

## Guardrails

### Input guardrails

- `non_empty_input_guardrail`: blocks empty or invalid input
- `blocked_request_input_guardrail`: blocks political requests and malicious-code requests

These run in blocking mode on the top-level router so bad requests are rejected before model or tool execution.

### Output guardrails

- `router_structured_output_guardrail`: validates the router structured output beyond typing, including required parameter slots and ISO currency-code constraints
- `final_output_safety_guardrail`: blocks unsafe final outputs and internal error leakage

## Memory

Conversation memory is implemented with `SQLiteSession` from the Agents SDK. The app loads prior history from a persistent SQLite file, automatically stores every new turn, supports `reset` through `clear_session()`, and limits retrieved history per run with `SessionSettings(limit=40)`.
