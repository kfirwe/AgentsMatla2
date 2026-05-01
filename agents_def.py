"""
Central definitions for the Homework 2 agents.
"""

from __future__ import annotations

from agents import Agent, handoff
from agents.extensions import handoff_filters

from config import DEFAULT_AGENT_MODEL
from guardrails import (
    blocked_request_input_guardrail,
    final_output_safety_guardrail,
    non_empty_input_guardrail,
    router_structured_output_guardrail,
)
from prompts import (
    EXCHANGE_AGENT_INSTRUCTIONS,
    GENERAL_CHAT_INSTRUCTIONS,
    MATH_AGENT_INSTRUCTIONS,
    ROUTER_HANDOFF_INSTRUCTIONS,
    ROUTER_INSTRUCTIONS,
    ROUTER_STRUCTURED_INSTRUCTIONS,
    WEATHER_AGENT_INSTRUCTIONS,
)
from schemas import RouterDecision
from tools import (
    calculate_math_tool,
    get_exchange_rate_tool,
    get_weather_tool,
)


COMMON_INPUT_GUARDRAILS = [
    non_empty_input_guardrail,
    blocked_request_input_guardrail,
]

COMMON_FINAL_OUTPUT_GUARDRAILS = [final_output_safety_guardrail]


weather_agent = Agent(
    name="Weather Agent",
    instructions=WEATHER_AGENT_INSTRUCTIONS,
    model=DEFAULT_AGENT_MODEL,
    tools=[get_weather_tool],
    output_guardrails=COMMON_FINAL_OUTPUT_GUARDRAILS,
    handoff_description="Use for current weather, temperature, or clothing questions for a city.",
)


math_agent = Agent(
    name="Math Agent",
    instructions=MATH_AGENT_INSTRUCTIONS,
    model=DEFAULT_AGENT_MODEL,
    tools=[calculate_math_tool],
    output_guardrails=COMMON_FINAL_OUTPUT_GUARDRAILS,
    handoff_description="Use for arithmetic, math expressions, and word problems with numbers.",
)


exchange_agent = Agent(
    name="Exchange Rate Agent",
    instructions=EXCHANGE_AGENT_INSTRUCTIONS,
    model=DEFAULT_AGENT_MODEL,
    tools=[get_exchange_rate_tool],
    output_guardrails=COMMON_FINAL_OUTPUT_GUARDRAILS,
    handoff_description="Use for currency exchange rates and money conversion questions.",
)


general_chat_agent = Agent(
    name="General Chat Agent",
    instructions=GENERAL_CHAT_INSTRUCTIONS,
    model=DEFAULT_AGENT_MODEL,
    output_guardrails=COMMON_FINAL_OUTPUT_GUARDRAILS,
    handoff_description="Use for jokes, opinions, identity questions, and general conversation.",
)


TASK_AGENTS = [weather_agent, math_agent, exchange_agent, general_chat_agent]

TASK_HANDOFFS = [
    handoff(
        weather_agent,
        tool_name_override="transfer_to_weather_agent",
        input_filter=handoff_filters.remove_all_tools,
    ),
    handoff(
        math_agent,
        tool_name_override="transfer_to_math_agent",
        input_filter=handoff_filters.remove_all_tools,
    ),
    handoff(
        exchange_agent,
        tool_name_override="transfer_to_exchange_rate_agent",
        input_filter=handoff_filters.remove_all_tools,
    ),
    handoff(
        general_chat_agent,
        tool_name_override="transfer_to_general_chat_agent",
        input_filter=handoff_filters.remove_all_tools,
    ),
]


router_agent_a = Agent(
    name="Router Agent (few-shot)",
    instructions=ROUTER_INSTRUCTIONS,
    model=DEFAULT_AGENT_MODEL,
    input_guardrails=COMMON_INPUT_GUARDRAILS,
)


router_agent_b = Agent(
    name="Router Agent (structured)",
    instructions=ROUTER_STRUCTURED_INSTRUCTIONS,
    model=DEFAULT_AGENT_MODEL,
    input_guardrails=COMMON_INPUT_GUARDRAILS,
    output_type=RouterDecision,
    output_guardrails=[router_structured_output_guardrail],
)


router_with_handoffs = Agent(
    name="Router Agent (handoffs)",
    instructions=ROUTER_HANDOFF_INSTRUCTIONS,
    model=DEFAULT_AGENT_MODEL,
    input_guardrails=COMMON_INPUT_GUARDRAILS,
    handoffs=TASK_HANDOFFS,
)
