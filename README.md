# AgentsMatla2

Homework 2 for the AI Systems Architecture and Engineering course.

This project implements a modular multi-agent assistant with the OpenAI Agents SDK and explicitly uses:

- `Agents`
- `Tools`
- `Handoffs`
- `Input Guardrails`
- `Output Guardrails`

For a full setup and execution walkthrough, see [RUN_HOMEWORK_GUIDE.md](RUN_HOMEWORK_GUIDE.md).

## Project structure

- [main.py](main.py): interactive app with persistent SDK session memory
- [agents_def.py](agents_def.py): task agents and router agents
- [prompts.py](prompts.py): centralized prompts for all agents
- [tools.py](tools.py): deterministic tools and tool guardrails
- [guardrails.py](guardrails.py): SDK-native input and output guardrails
- [schemas.py](schemas.py): structured router output schemas and validation
- [demos.py](demos.py): assignment demos for parts A-I

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

3. Add an OpenAI API key in a local `.env` file:

```env
OPENAI_API_KEY=sk-...
```

Optional overrides:

```env
OPENAI_AGENT_MODEL=gpt-5.4-mini
OPENAI_SESSION_ID=aviv-kfir-homework2
```

## Run the app

Single turn:

```powershell
.\.venv\Scripts\python main.py --message "I am flying to London, should I take a coat?"
```

Interactive mode:

```powershell
.\.venv\Scripts\python main.py
```

Commands inside the app:

- `reset`
- `exit`
- `quit`

## Run demos

Run one part:

```powershell
.\.venv\Scripts\python demos.py --part f
```

Run the full assignment demo flow:

```powershell
.\.venv\Scripts\python demos.py --part all
```

## Run tests

```powershell
.\.venv\Scripts\python -m pytest
```
