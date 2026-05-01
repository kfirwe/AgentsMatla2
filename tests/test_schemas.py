from __future__ import annotations

import pytest

from schemas import (
    RouterDecision,
    RouterParameters,
    RouterValidationError,
    validate_router_decision,
)


def test_validate_router_decision_accepts_valid_weather_route() -> None:
    decision = RouterDecision(
        intent="getWeather",
        parameters=RouterParameters(city="London"),
        confidence=0.91,
    )

    validated = validate_router_decision(decision)

    assert validated.intent == "getWeather"
    assert validated.parameters.city == "London"


def test_validate_router_decision_rejects_missing_required_slot() -> None:
    decision = RouterDecision(
        intent="getExchangeRate",
        parameters=RouterParameters(),
        confidence=0.8,
    )

    with pytest.raises(RouterValidationError):
        validate_router_decision(decision)


def test_validate_router_decision_rejects_unexpected_parameter_slot() -> None:
    decision = RouterDecision(
        intent="generalChat",
        parameters=RouterParameters(message="Hello", city="Paris"),
        confidence=0.7,
    )

    with pytest.raises(RouterValidationError):
        validate_router_decision(decision)


def test_validate_router_decision_rejects_non_iso_currency_code() -> None:
    decision = RouterDecision(
        intent="getExchangeRate",
        parameters=RouterParameters(currency_code="usd1"),
        confidence=0.84,
    )

    with pytest.raises(RouterValidationError):
        validate_router_decision(decision)
