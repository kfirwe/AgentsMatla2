"""
Shared Pydantic schemas and business validation.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


Intent = Literal["getWeather", "calculateMath", "getExchangeRate", "generalChat"]


class RouterParameters(BaseModel):
    """All possible parameter slots. Only the one matching `intent` is filled."""

    city: Optional[str] = Field(default=None, description="City name for weather requests.")
    expression: Optional[str] = Field(
        default=None,
        description="Math expression or the raw word-problem text.",
    )
    currency_code: Optional[str] = Field(
        default=None,
        description="3-letter ISO source currency code such as USD or EUR.",
    )
    message: Optional[str] = Field(
        default=None,
        description="Passthrough general-chat message.",
    )


class RouterDecision(BaseModel):
    intent: Intent
    parameters: RouterParameters
    confidence: float = Field(ge=0.0, le=1.0)


class RouterValidationError(ValueError):
    """Raised when a structured router output is well-typed but business-invalid."""


REQUIRED_SLOT_BY_INTENT = {
    "getWeather": "city",
    "calculateMath": "expression",
    "getExchangeRate": "currency_code",
    "generalChat": "message",
}


def validate_router_decision(decision: RouterDecision) -> RouterDecision:
    """Validate the structured router output beyond Pydantic typing."""

    required_slot = REQUIRED_SLOT_BY_INTENT[decision.intent]
    required_value = getattr(decision.parameters, required_slot)

    if not required_value or not str(required_value).strip():
        raise RouterValidationError(
            f"Intent '{decision.intent}' requires parameters.{required_slot}."
        )

    for slot_name in REQUIRED_SLOT_BY_INTENT.values():
        slot_value = getattr(decision.parameters, slot_name)
        if slot_name == required_slot:
            continue
        if slot_value not in (None, ""):
            raise RouterValidationError(
                f"Intent '{decision.intent}' must not populate parameters.{slot_name}."
            )

    if decision.intent == "getExchangeRate":
        code = str(decision.parameters.currency_code).strip()
        if len(code) != 3 or not code.isalpha() or code != code.upper():
            raise RouterValidationError(
                "Exchange-rate routing requires a 3-letter uppercase ISO currency code."
            )

    return decision
