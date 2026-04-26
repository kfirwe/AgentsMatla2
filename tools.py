"""
tools.py — deterministic tools shared by all Homework 2 agents.

Per the assignment ("יש לממש את יכולות המערכת באמצעות tools דטרמיניסטיים"),
each tool here is a pure Python function with NO LLM in the loop. The LLM
only decides WHEN to call them and WITH WHAT arguments.

Tools:
  - get_weather_tool       : live weather via wttr.in (no API key)
  - calculate_math_tool    : safe AST-based math evaluator (no eval)
  - get_exchange_rate_tool : live FX vs ILS via frankfurter.app (no API key)

All tools are wrapped with @function_tool from the OpenAI Agents SDK so they
can be attached to any Agent.
"""

import ast
import operator
import requests
from agents import function_tool


# ─────────────────────────────────────────────────────────────────────────────
# 1. Weather  (wttr.in — free, no key)
# ─────────────────────────────────────────────────────────────────────────────

@function_tool
def get_weather_tool(city: str) -> str:
    """Return the current weather for a city as 'condition, +temp'.

    Args:
        city: A city name in any language (e.g. "Tel Aviv", "תל אביב", "London").
    """
    try:
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=%C,+%t"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200 and resp.text.strip():
            return f"Weather in {city}: {resp.text.strip()}"
        return f"Could not retrieve weather data for {city}."
    except Exception as e:
        return f"Error fetching weather data: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Math  (AST evaluator — no eval(), no LLM)
# ─────────────────────────────────────────────────────────────────────────────

_SAFE_OPS = {
    ast.Add:      operator.add,
    ast.Sub:      operator.sub,
    ast.Mult:     operator.mul,
    ast.Div:      operator.truediv,
    ast.Pow:      operator.pow,
    ast.Mod:      operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub:     operator.neg,
    ast.UAdd:     operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in _SAFE_OPS:
            raise ValueError(f"Unsupported operator: {op.__name__}")
        return _SAFE_OPS[op](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in _SAFE_OPS:
            raise ValueError(f"Unsupported operator: {op.__name__}")
        return _SAFE_OPS[op](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression type: {type(node).__name__}")


@function_tool
def calculate_math_tool(expression: str) -> str:
    """Evaluate a clean arithmetic expression deterministically.

    The expression must contain only digits, parentheses, and the operators
    +, -, *, /, **, %. NO words, units, or variables. The Math Agent is
    responsible for translating word problems into expressions BEFORE calling
    this tool.

    Args:
        expression: e.g. "5 - 2 + 10", "60 / (45/60)", "25 * 4".
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        formatted = int(result) if isinstance(result, float) and result.is_integer() else result
        return f"The result of {expression} is: {formatted}"
    except Exception as e:
        return f"Could not evaluate expression '{expression}': {e}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Exchange rate  (frankfurter.app — free, no key) → ILS
# ─────────────────────────────────────────────────────────────────────────────

@function_tool
def get_exchange_rate_tool(currency_code: str) -> str:
    """Return the current exchange rate of `currency_code` against ILS.

    Args:
        currency_code: A 3-letter ISO currency code (e.g. "USD", "EUR", "GBP").
    """
    code = currency_code.upper().strip()
    try:
        url = f"https://api.frankfurter.app/latest?from={code}&to=ILS"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            rate = resp.json()["rates"]["ILS"]
            return f"Exchange rate for {code}: {rate} ILS"
        return f"Could not retrieve exchange rate for '{code}' (HTTP {resp.status_code})."
    except Exception as e:
        return f"Error fetching exchange rate: {e}"
