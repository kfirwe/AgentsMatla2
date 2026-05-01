# Homework Run Guide

This guide explains how to set up, run, test, and demonstrate the Homework 2 project end to end.

## What this project implements

The system is built with the OpenAI Agents SDK and includes all required assignment features:

- `Agents`
- `Tools`
- `Handoffs`
- `Input Guardrails`
- `Output Guardrails`
- conversation memory with persistent sessions

Main files:

- [main.py](main.py): interactive multi-agent app
- [demos.py](demos.py): demo runner for parts A-I
- [agents_def.py](agents_def.py): router and task agents
- [prompts.py](prompts.py): all prompts and persona instructions
- [tools.py](tools.py): deterministic tools and tool guardrails
- [guardrails.py](guardrails.py): input and output guardrails
- [schemas.py](schemas.py): structured router schemas and validation
- [ARCHITECTURE.md](ARCHITECTURE.md): short architecture explanation

## Prerequisites

- Windows PowerShell
- Python `3.12+`
- internet access
- an OpenAI API key

## Initial setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## API key setup

Preferred approach: create a local `.env` file:

```env
OPENAI_API_KEY=sk-...
OPENAI_AGENT_MODEL=gpt-5.4-mini
OPENAI_SESSION_ID=aviv-kfir-homework2
```

Alternative PowerShell session-only setup:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

If you have a local `api-key.txt` file that contains only the raw key, you can load it for the current shell:

```powershell
$env:OPENAI_API_KEY = (Get-Content -Raw api-key.txt).Trim()
```

Do not commit `.env` or `api-key.txt`.

## Run the interactive app

Start the chat app:

```powershell
.\.venv\Scripts\python main.py
```

Supported interactive commands:

- `reset`
- `exit`
- `quit`

Example interaction flow:

1. Ask for weather:
   `I am flying to London, should I take a coat?`
2. Ask for exchange rate:
   `100 USD is how many ILS?`
3. Ask a word problem:
   `Yossi has 5 apples, ate 2, bought 10 more. How many does he have?`
4. Test memory:
   `My name is Aviv and my partner is Kfir. Remember that.`
   then
   `Who is my partner?`
5. Test reset:
   `reset`
   then
   `Who is my partner?`

## Run a single one-off message

Useful for quick checks:

```powershell
.\.venv\Scripts\python main.py --message "Hello, who are you?"
```

Use a custom persistent session id:

```powershell
.\.venv\Scripts\python main.py --session-id my-demo --message "My name is Aviv."
.\.venv\Scripts\python main.py --session-id my-demo --message "What is my name?"
```

Reset a session before sending a one-off message:

```powershell
.\.venv\Scripts\python main.py --session-id my-demo --reset-session --message "Start fresh."
```

## Run the assignment demos

Each assignment part has a dedicated demo:

```powershell
.\.venv\Scripts\python demos.py --part a
.\.venv\Scripts\python demos.py --part b
.\.venv\Scripts\python demos.py --part c
.\.venv\Scripts\python demos.py --part d
.\.venv\Scripts\python demos.py --part e
.\.venv\Scripts\python demos.py --part f
.\.venv\Scripts\python demos.py --part g
.\.venv\Scripts\python demos.py --part h
.\.venv\Scripts\python demos.py --part i
```

Run the full demo flow:

```powershell
.\.venv\Scripts\python demos.py --part all
```

## What each demo proves

- Part A: few-shot router classification benchmark
- Part B: structured router output with `intent`, `parameters`, and `confidence`
- Part C: word problem translated to a formal expression, then solved by the deterministic math tool
- Part D: each task agent works in isolation
- Part E: real handoffs from the router to specialist agents
- Part F: input guardrails block empty, malicious, and political requests
- Part G: output guardrails validate router output and block unsafe final output
- Part H: general-chat persona and exact refusal message
- Part I: persisted memory across sessions

## Run tests

Run the automated test suite:

```powershell
.\.venv\Scripts\python -m pytest -q
```

What the tests cover:

- structured router validation
- input guardrail logic
- output guardrail logic
- deterministic math evaluation
- weather and exchange-rate tool formatting with mocked HTTP calls
- `SQLiteSession` persistence and clearing

## Submission-proof logs

The repository includes a [logs](logs) folder for execution proof.

Important proof files:

- [logs/demos-all.log](logs/demos-all.log): full A-I demo run
- [logs/main-interactive-reset.log](logs/main-interactive-reset.log): interactive session showing memory and `reset`
- [logs/memory-restart-proof.log](logs/memory-restart-proof.log): restart-style memory proof across separate CLI invocations

## Expected behaviors

### Few-shot router

- travel clothing questions should route to weather
- word problems should route to math
- currency conversion questions should route to exchange rate
- everything else should route to general chat

### Safety behavior

The system should refuse political or malicious requests with exactly:

```text
I cannot process this request due to safety protocols.
```

### Memory behavior

- information should persist between turns when the same session id is reused
- `reset` should clear that memory
- a new session object with the same session id should still load prior history from the SQLite database

## Troubleshooting

### `OPENAI_API_KEY is not set`

Set the key in `.env` or in the current PowerShell session:

```powershell
$env:OPENAI_API_KEY = (Get-Content -Raw api-key.txt).Trim()
```

### `ModuleNotFoundError`

Use the virtual environment Python:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

### Weather or FX failures

The app uses live external services:

- `wttr.in`
- `frankfurter.app`

If one of them is temporarily unavailable, rerun the request or use the test suite for deterministic validation.

### Tracing `504` retry message

You may occasionally see a non-fatal tracing retry. That does not invalidate the agent result if the final answer still returns successfully.

## Recommended grading/demo order

For the cleanest manual walkthrough:

1. Run `pytest`
2. Run `demos.py --part all`
3. Run `main.py`
4. Show one weather request
5. Show one word-problem request
6. Show one blocked malicious or political request
7. Show memory across turns
8. Show `reset`

## Final deliverables in this repo

- full code
- centralized prompts file
- proof logs
- architecture summary
- automated tests
- persistent memory implementation
