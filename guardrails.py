"""
SDK-native guardrails plus pure helper functions for unit testing.
"""

from __future__ import annotations

import re
from typing import Any

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
)

from config import SAFETY_REFUSAL_MESSAGE
from schemas import RouterDecision, RouterValidationError, validate_router_decision


POLITICAL_PATTERNS = (
    r"\belection\b",
    r"\bvote\b",
    r"\bvoting\b",
    r"\bpolitic(?:s|al)\b",
    r"\bprime minister\b",
    r"\bpresident\b",
    r"\bgovernment\b",
    r"\bcampaign\b",
    r"\bparliament\b",
)

HARMFUL_CODE_PATTERNS = (
    r"\bmalware\b",
    r"\bransomware\b",
    r"\bvirus\b",
    r"\bkeylogger\b",
    r"\bphishing\b",
    r"\bcredential(?:s)? theft\b",
    r"\bsteal passwords?\b",
    r"\bbackdoor\b",
    r"\bpersistence\b",
    r"\bpayload\b",
    r"\bexploit\b",
    r"powershell\s+-enc",
    r"\brm\s+-rf\b",
)

INTERNAL_ERROR_MARKERS = (
    "Traceback (most recent call last):",
    "Error fetching weather data:",
    "Error fetching exchange rate:",
    "Could not evaluate expression",
)


def extract_text_from_input(user_input: str | list[TResponseInputItem]) -> str:
    """Best-effort text extraction for guardrails."""

    if isinstance(user_input, str):
        return user_input.strip()

    parts: list[str] = []
    for item in user_input:
        if isinstance(item, dict):
            content = item.get("content")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                for entry in content:
                    if not isinstance(entry, dict):
                        continue
                    text = entry.get("text") or entry.get("content")
                    if isinstance(text, str):
                        parts.append(text)
        else:
            parts.append(str(item))

    return "\n".join(part for part in parts if part).strip()


def detect_empty_input(text: str) -> dict[str, str] | None:
    if text.strip():
        return None
    return {
        "code": "empty_input",
        "user_message": "Please enter a non-empty request.",
    }


def detect_blocked_input(text: str) -> dict[str, str] | None:
    normalized = text.strip()
    if not normalized:
        return None

    for pattern in HARMFUL_CODE_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return {
                "code": "harmful_request",
                "user_message": SAFETY_REFUSAL_MESSAGE,
            }

    for pattern in POLITICAL_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return {
                "code": "political_request",
                "user_message": SAFETY_REFUSAL_MESSAGE,
            }

    return None


def detect_unsafe_output(text: str) -> dict[str, str] | None:
    normalized = text.strip()
    if not normalized:
        return {
            "code": "empty_output",
            "user_message": "I could not produce a safe response. Please try again.",
        }

    if normalized == SAFETY_REFUSAL_MESSAGE:
        return None

    for marker in INTERNAL_ERROR_MARKERS:
        if marker in normalized:
            return {
                "code": "internal_error_leak",
                "user_message": "I could not produce a safe response. Please try again.",
            }

    for pattern in HARMFUL_CODE_PATTERNS + POLITICAL_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return {
                "code": "unsafe_output",
                "user_message": SAFETY_REFUSAL_MESSAGE,
            }

    return None


def get_guardrail_user_message(output_info: Any, fallback: str) -> str:
    if isinstance(output_info, dict):
        user_message = output_info.get("user_message")
        if isinstance(user_message, str) and user_message.strip():
            return user_message
    return fallback


@input_guardrail(name="non_empty_input_guardrail", run_in_parallel=False)
async def non_empty_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    user_input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    del ctx, agent
    info = detect_empty_input(extract_text_from_input(user_input))
    return GuardrailFunctionOutput(
        output_info=info,
        tripwire_triggered=info is not None,
    )


@input_guardrail(name="blocked_request_input_guardrail", run_in_parallel=False)
async def blocked_request_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    user_input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    del ctx, agent
    info = detect_blocked_input(extract_text_from_input(user_input))
    return GuardrailFunctionOutput(
        output_info=info,
        tripwire_triggered=info is not None,
    )


@output_guardrail(name="router_structured_output_guardrail")
async def router_structured_output_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: RouterDecision,
) -> GuardrailFunctionOutput:
    del ctx, agent
    try:
        validate_router_decision(output)
        info = {
            "code": "router_output_valid",
            "user_message": "",
        }
        tripped = False
    except RouterValidationError as exc:
        info = {
            "code": "invalid_router_output",
            "details": str(exc),
            "user_message": "I could not safely route that request.",
        }
        tripped = True

    return GuardrailFunctionOutput(output_info=info, tripwire_triggered=tripped)


@output_guardrail(name="final_output_safety_guardrail")
async def final_output_safety_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    del ctx, agent
    info = detect_unsafe_output(output)
    return GuardrailFunctionOutput(
        output_info=info,
        tripwire_triggered=info is not None,
    )
