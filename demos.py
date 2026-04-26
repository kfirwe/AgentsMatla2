"""
demos.py — single launcher for every Homework 2 demo (Parts A–E so far).

Usage from the project root:
    uv run python 2_openai/homework2/demos.py --part a
    uv run python 2_openai/homework2/demos.py --part b
    uv run python 2_openai/homework2/demos.py --part c
    uv run python 2_openai/homework2/demos.py --part d
    uv run python 2_openai/homework2/demos.py --part e
    uv run python 2_openai/homework2/demos.py --part all

Each Part is a self-contained demo (own banner, own trace name, own cases).
Shared logic stays in prompts.py / tools.py / agents_def.py — those are
imported, never duplicated.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agents import Agent, Runner, trace

sys.path.insert(0, str(Path(__file__).parent))
from prompts import (
    ROUTER_INSTRUCTIONS,
    ROUTER_STRUCTURED_INSTRUCTIONS,
    ROUTER_HANDOFF_INSTRUCTIONS,
)
from agents_def import (
    weather_agent,
    math_agent,
    exchange_agent,
    general_chat_agent,
    TASK_AGENTS,
)

load_dotenv(override=True)


# ═════════════════════════════════════════════════════════════════════════════
# Part A — Router with Few-Shot Prompting
# ═════════════════════════════════════════════════════════════════════════════

router_agent_a = Agent(
    name="Router Agent (few-shot)",
    instructions=ROUTER_INSTRUCTIONS,
    model="gpt-4o-mini",
)

PART_A_CASES: list[tuple[str, str]] = [
    ("מה מזג האוויר בתל אביב?",                      "getWeather"),
    ("What's the temperature in Paris right now?",  "getWeather"),
    ("כמה זה 25 כפול 4?",                            "calculateMath"),
    ("What is 100 + 250?",                          "calculateMath"),
    ("כמה זה דולר בשקלים?",                          "getExchangeRate"),
    ("Hello!",                                      "generalChat"),
    ("ספר לי בדיחה",                                  "generalChat"),
    # edge cases
    ("אני טס ללונדון, צריך לקחת מעיל?",               "getWeather"),
    ("יוסי קנה 10 תפוחים, אכל 3, כמה נשארו?",          "calculateMath"),
    ("100 דולר זה כמה שקלים?",                       "getExchangeRate"),
    ("פי כמה דובאי חמה משטוקהולם?",                   "getWeather"),
    ("כמה Euro אפשר לקנות ב־100 דולר?",              "getExchangeRate"),
    ("מה דעתך על בינה מלאכותית?",                    "generalChat"),
    ("מה השעה?",                                      "generalChat"),
]


async def run_part_a() -> None:
    print("=" * 72)
    print("Part A — Few-Shot Router Agent")
    print("=" * 72)
    correct = 0
    misses: list[tuple[str, str, str]] = []
    with trace("Part A — Router benchmark"):
        for text, expected in PART_A_CASES:
            result = await Runner.run(router_agent_a, text)
            got = result.final_output.strip()
            ok = got == expected
            correct += int(ok)
            mark = "OK " if ok else "WRG"
            print(f"[{mark}] {text[:48]:<48} -> {got:<18} (expected {expected})")
            if not ok:
                misses.append((text, expected, got))
    print("-" * 72)
    print(f"Score: {correct}/{len(PART_A_CASES)}")
    if misses:
        print("\nMisclassifications:")
        for txt, exp, got in misses:
            print(f"  '{txt}'  expected={exp}  got={got}")


# ═════════════════════════════════════════════════════════════════════════════
# Part B — Router with Structured Output (Pydantic)
# ═════════════════════════════════════════════════════════════════════════════

Intent = Literal["getWeather", "calculateMath", "getExchangeRate", "generalChat"]


class RouterParameters(BaseModel):
    """All possible parameter slots. Only the one matching `intent` is filled."""
    city:           Optional[str] = Field(default=None, description="City name (getWeather)")
    expression:     Optional[str] = Field(default=None, description="Math expression OR word-problem text (calculateMath)")
    currency_code:  Optional[str] = Field(default=None, description="3-letter ISO source currency code (getExchangeRate)")
    message:        Optional[str] = Field(default=None, description="Passthrough user text (generalChat)")


class RouterDecision(BaseModel):
    intent:     Intent
    parameters: RouterParameters
    confidence: float = Field(ge=0.0, le=1.0)


router_agent_b = Agent(
    name="Router Agent (structured)",
    instructions=ROUTER_STRUCTURED_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=RouterDecision,
)


class RouterValidationError(ValueError):
    """Well-typed but business-invalid (parameter slot missing for the intent)."""


_REQUIRED_SLOT = {
    "getWeather":      "city",
    "calculateMath":   "expression",
    "getExchangeRate": "currency_code",
    "generalChat":     "message",
}


def validate_decision(decision: RouterDecision) -> RouterDecision:
    slot = _REQUIRED_SLOT[decision.intent]
    value = getattr(decision.parameters, slot)
    if not value or not str(value).strip():
        raise RouterValidationError(
            f"Intent '{decision.intent}' requires parameters.{slot} (got: {value!r})."
        )
    return decision


PART_B_INPUTS = [
    "מה מזג האוויר בתל אביב?",
    "אני טס ללונדון, צריך לקחת מעיל?",
    "What is 25 * 4?",
    "ליוסי יש 5 תפוחים, אכל 2 וקנה עוד 10. כמה יש לו?",
    "100 דולר זה כמה שקלים?",
    "What's the EUR rate?",
    "ספר לי בדיחה",
    "Hello, who are you?",
]


async def run_part_b() -> None:
    print("=" * 72)
    print("Part B — Router with Structured Output (Pydantic)")
    print("=" * 72)
    with trace("Part B — Router structured"):
        for text in PART_B_INPUTS:
            result = await Runner.run(router_agent_b, text)
            try:
                decision = validate_decision(result.final_output)
            except RouterValidationError as e:
                print(f"[INVALID] {text!r} -> {e}")
                continue
            slot = _REQUIRED_SLOT[decision.intent]
            print(f"\nInput : {text}")
            print(f"  intent     : {decision.intent}")
            print(f"  parameters : {{ {slot}: {getattr(decision.parameters, slot)!r} }}")
            print(f"  confidence : {decision.confidence:.2f}")
            print(f"  raw json   : {decision.model_dump_json()}")


# ═════════════════════════════════════════════════════════════════════════════
# Part C — Word-Problem Math Agent (LLM translates → tool computes)
# ═════════════════════════════════════════════════════════════════════════════

PART_C_PROBLEMS = [
    "What is 25 * 4?",
    "כמה זה 150 ועוד 20?",
    "ליוסי יש 5 תפוחים, אכל 2 וקנה עוד 10. כמה יש לו?",
    "A shop sold 12 items at 7 shekels each, then 3 more at 9. Total revenue?",
    "If a train travels 60 km in 45 minutes, what's its speed in km/h?",
    "Tell me a joke about engineers.",   # not math — agent should refuse
]


async def run_part_c() -> None:
    print("=" * 72)
    print("Part C — Word-Problem Math Agent")
    print("=" * 72)
    with trace("Part C — Word problem solver"):
        for problem in PART_C_PROBLEMS:
            print(f"\nProblem : {problem}")
            result = await Runner.run(math_agent, problem)
            print(f"Answer  : {result.final_output}")


# ═════════════════════════════════════════════════════════════════════════════
# Part D — Each Task Agent in isolation
# ═════════════════════════════════════════════════════════════════════════════

PART_D_CASES = [
    (weather_agent,      "מה מזג האוויר בתל אביב?"),
    (weather_agent,      "Compare the weather in Dubai and Stockholm right now."),
    (math_agent,         "ליוסי יש 5 תפוחים, אכל 2 וקנה עוד 10. כמה יש לו?"),
    (exchange_agent,     "What's the rate of USD?"),
    (exchange_agent,     "100 דולר זה כמה שקלים?"),
    (general_chat_agent, "Tell me a joke about agents."),
]


async def run_part_d() -> None:
    print("=" * 72)
    print("Part D — Task Agents (direct calls)")
    print("=" * 72)
    with trace("Part D — Task agents direct calls"):
        for agent, msg in PART_D_CASES:
            print(f"\n[{agent.name}]  ->  {msg}")
            result = await Runner.run(agent, msg)
            print(f"  {result.final_output}")


# ═════════════════════════════════════════════════════════════════════════════
# Part E — Router with real Handoffs to all Task Agents
# ═════════════════════════════════════════════════════════════════════════════

router_with_handoffs = Agent(
    name="Router (with handoffs)",
    instructions=ROUTER_HANDOFF_INSTRUCTIONS,
    model="gpt-4o-mini",
    handoffs=TASK_AGENTS,
)

PART_E_CASES = [
    "מה מזג האוויר בתל אביב?",                     # → Weather Agent
    "אני טס ללונדון, צריך לקחת מעיל?",             # → Weather Agent (implicit)
    "ליוסי יש 5 תפוחים, אכל 2 וקנה עוד 10. כמה יש לו?",   # → Math Agent
    "What is 25 * 4?",                              # → Math Agent
    "100 דולר זה כמה שקלים?",                      # → Exchange Rate Agent
    "What's the EUR rate?",                        # → Exchange Rate Agent
    "ספר לי בדיחה על מהנדסים",                      # → General Chat Agent
    "מה דעתך על בינה מלאכותית?",                   # → General Chat Agent
]


async def run_part_e() -> None:
    print("=" * 72)
    print("Part E — Router with Handoffs")
    print("=" * 72)
    with trace("Part E — Router handoffs"):
        for msg in PART_E_CASES:
            print(f"\nUser : {msg}")
            result = await Runner.run(router_with_handoffs, msg)
            print(f"Bot  : {result.final_output}")


# ═════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════

PARTS = {
    "a":   run_part_a,
    "b":   run_part_b,
    "c":   run_part_c,
    "d":   run_part_d,
    "e":   run_part_e,
}


async def main() -> None:
    parser = argparse.ArgumentParser(description="Homework 2 demos launcher.")
    parser.add_argument(
        "--part",
        required=True,
        choices=[*PARTS.keys(), "all"],
        help="Which Part to run (a, b, c, d, e, or all).",
    )
    args = parser.parse_args()

    if args.part == "all":
        for key in PARTS:
            await PARTS[key]()
            print()
    else:
        await PARTS[args.part]()


if __name__ == "__main__":
    asyncio.run(main())
