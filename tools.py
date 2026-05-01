"""
Deterministic tools and tool guardrails for Homework 2.
"""

from __future__ import annotations

import ast
import json
import operator
from typing import Any

import requests
from agents import (
    ToolGuardrailFunctionOutput,
    function_tool,
    tool_input_guardrail,
    tool_output_guardrail,
)


_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_RAW_TOOL_ERROR_MARKERS = (
    "Error fetching weather data:",
    "Error fetching exchange rate:",
)


def _parse_tool_arguments(raw_arguments: str | None) -> dict[str, Any]:
    try:
        return json.loads(raw_arguments or "{}")
    except json.JSONDecodeError:
        return {}


@tool_output_guardrail(name="sanitize_raw_tool_errors")
def sanitize_raw_tool_errors(data) -> ToolGuardrailFunctionOutput:
    text = str(data.output or "")
    if any(marker in text for marker in _RAW_TOOL_ERROR_MARKERS) or "Traceback" in text:
        return ToolGuardrailFunctionOutput.reject_content(
            "The upstream service failed, so I returned a safe fallback instead."
        )
    return ToolGuardrailFunctionOutput.allow()


@tool_input_guardrail(name="weather_city_input_guardrail")
def weather_city_input_guardrail(data) -> ToolGuardrailFunctionOutput:
    args = _parse_tool_arguments(data.context.tool_arguments)
    city = str(args.get("city", "")).strip()
    if not city or len(city) > 80:
        return ToolGuardrailFunctionOutput.reject_content(
            "Please provide a valid city name."
        )
    return ToolGuardrailFunctionOutput.allow()


@tool_input_guardrail(name="math_expression_input_guardrail")
def math_expression_input_guardrail(data) -> ToolGuardrailFunctionOutput:
    args = _parse_tool_arguments(data.context.tool_arguments)
    expression = str(args.get("expression", "")).strip()
    if not expression or len(expression) > 300:
        return ToolGuardrailFunctionOutput.reject_content(
            "Please provide a valid arithmetic expression."
        )
    return ToolGuardrailFunctionOutput.allow()


@tool_input_guardrail(name="currency_code_input_guardrail")
def currency_code_input_guardrail(data) -> ToolGuardrailFunctionOutput:
    args = _parse_tool_arguments(data.context.tool_arguments)
    code = str(args.get("currency_code", "")).strip()
    if len(code) != 3 or not code.isalpha():
        return ToolGuardrailFunctionOutput.reject_content(
            "Please provide a valid 3-letter ISO currency code."
        )
    return ToolGuardrailFunctionOutput.allow()


def fetch_weather(city: str) -> str:
    """Return the current weather for a city as `condition, +temp`."""

    normalized_city = city.strip()
    try:
        url = f"https://wttr.in/{requests.utils.quote(normalized_city)}?format=%C,+%t"
        response = requests.get(url, timeout=6)
        if response.status_code == 200 and response.text.strip():
            return f"Weather in {normalized_city}: {response.text.strip()}"
        return f"Could not retrieve weather data for {normalized_city}."
    except Exception as exc:  # pragma: no cover - exercised via mocking in tests
        return f"Error fetching weather data: {exc}"


def _eval_node(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)
        if operator_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported operator: {operator_type.__name__}")
        return _SAFE_OPS[operator_type](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)
        if operator_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported operator: {operator_type.__name__}")
        return _SAFE_OPS[operator_type](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression type: {type(node).__name__}")


def evaluate_expression(expression: str) -> str:
    """Evaluate a clean arithmetic expression deterministically."""

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"The result of {expression} is: {result}"
    except Exception as exc:
        return f"Could not evaluate expression '{expression}': {exc}"


def fetch_exchange_rate(currency_code: str) -> str:
    """Return the current exchange rate of `currency_code` against ILS."""

    code = currency_code.upper().strip()
    try:
        url = f"https://api.frankfurter.app/latest?from={code}&to=ILS"
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            rate = response.json()["rates"]["ILS"]
            return f"Exchange rate for {code}: {rate} ILS"
        return f"Could not retrieve exchange rate for '{code}' (HTTP {response.status_code})."
    except Exception as exc:  # pragma: no cover - exercised via mocking in tests
        return f"Error fetching exchange rate: {exc}"


@function_tool(
    tool_input_guardrails=[weather_city_input_guardrail],
    tool_output_guardrails=[sanitize_raw_tool_errors],
)
def get_weather_tool(city: str) -> str:
    """Return live weather data for a city."""

    return fetch_weather(city)


@function_tool(
    tool_input_guardrails=[math_expression_input_guardrail],
)
def calculate_math_tool(expression: str) -> str:
    """Evaluate a clean arithmetic expression using deterministic Python code."""

    return evaluate_expression(expression)


@function_tool(
    tool_input_guardrails=[currency_code_input_guardrail],
    tool_output_guardrails=[sanitize_raw_tool_errors],
)
def get_exchange_rate_tool(currency_code: str) -> str:
    """Return the current exchange rate of a currency against ILS."""

    return fetch_exchange_rate(currency_code)
