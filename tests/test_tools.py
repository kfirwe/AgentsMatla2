from __future__ import annotations

import responses

from tools import evaluate_expression, fetch_exchange_rate, fetch_weather


def test_evaluate_expression_returns_deterministic_result() -> None:
    result = evaluate_expression("5 - 2 + 10")

    assert result == "The result of 5 - 2 + 10 is: 13"


def test_evaluate_expression_rejects_unsupported_syntax() -> None:
    result = evaluate_expression("x + 1")

    assert result.startswith("Could not evaluate expression")


@responses.activate
def test_fetch_weather_formats_live_response() -> None:
    responses.add(
        responses.GET,
        "https://wttr.in/London?format=%C,+%t",
        body="Sunny, +17°C",
        status=200,
    )

    result = fetch_weather("London")

    assert result == "Weather in London: Sunny, +17°C"


@responses.activate
def test_fetch_exchange_rate_formats_live_response() -> None:
    responses.add(
        responses.GET,
        "https://api.frankfurter.app/latest?from=USD&to=ILS",
        json={"amount": 1.0, "base": "USD", "date": "2026-04-30", "rates": {"ILS": 3.71}},
        status=200,
    )

    result = fetch_exchange_rate("usd")

    assert result == "Exchange rate for USD: 3.71 ILS"
