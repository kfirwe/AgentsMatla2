"""
agents_def.py — central definition of every Task Agent in Homework 2.

Per the assignment (Part D), each capability lives in its OWN Agent, each of
which owns a deterministic tool. The Router (defined in Part B) hands off to
one of these. This file is imported by Parts E, F, G, H, I and the final bot.

  - weather_agent       : owns get_weather_tool
  - math_agent          : owns calculate_math_tool      (re-exported from Part C)
  - exchange_agent      : owns get_exchange_rate_tool
  - general_chat_agent  : the conversational fallback (persona finalized in Part H)
"""

from agents import Agent

from prompts import (
    WEATHER_AGENT_INSTRUCTIONS,
    EXCHANGE_AGENT_INSTRUCTIONS,
    MATH_AGENT_INSTRUCTIONS,
    GENERAL_CHAT_INSTRUCTIONS_PLACEHOLDER,
)
from tools import (
    get_weather_tool,
    calculate_math_tool,
    get_exchange_rate_tool,
)


# ── Weather ─────────────────────────────────────────────────────────────────
weather_agent = Agent(
    name="Weather Agent",
    instructions=WEATHER_AGENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[get_weather_tool],
    handoff_description="Use for any question about current weather, temperature, or what to wear in a city.",
)


# ── Math (translator + tool, from Part C) ────────────────────────────────────
math_agent = Agent(
    name="Math Agent",
    instructions=MATH_AGENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[calculate_math_tool],
    handoff_description="Use for any arithmetic, math expression, or word problem with numbers.",
)


# ── Exchange rate ───────────────────────────────────────────────────────────
exchange_agent = Agent(
    name="Exchange Rate Agent",
    instructions=EXCHANGE_AGENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[get_exchange_rate_tool],
    handoff_description="Use for any question about currency exchange rates or money conversion.",
)


# ── General chat (persona arrives in Part H) ─────────────────────────────────
general_chat_agent = Agent(
    name="General Chat Agent",
    instructions=GENERAL_CHAT_INSTRUCTIONS_PLACEHOLDER,
    model="gpt-4o-mini",
    handoff_description="Use for opinions, jokes, identity questions, or anything not covered by the other agents.",
)


TASK_AGENTS = [weather_agent, math_agent, exchange_agent, general_chat_agent]
