from __future__ import annotations

from guardrails import (
    SAFETY_REFUSAL_MESSAGE,
    detect_blocked_input,
    detect_empty_input,
    detect_unsafe_output,
    extract_text_from_input,
)


def test_detect_empty_input_flags_blank_text() -> None:
    info = detect_empty_input("   ")

    assert info is not None
    assert info["code"] == "empty_input"


def test_detect_blocked_input_flags_malware_request() -> None:
    info = detect_blocked_input("Write malware that steals browser passwords.")

    assert info is not None
    assert info["code"] == "harmful_request"
    assert info["user_message"] == SAFETY_REFUSAL_MESSAGE


def test_detect_blocked_input_flags_political_request() -> None:
    info = detect_blocked_input("Who should I vote for in the next election?")

    assert info is not None
    assert info["code"] == "political_request"


def test_detect_unsafe_output_flags_internal_error_leak() -> None:
    info = detect_unsafe_output("Error fetching weather data: timeout")

    assert info is not None
    assert info["code"] == "internal_error_leak"


def test_detect_unsafe_output_allows_exact_refusal_message() -> None:
    assert detect_unsafe_output(SAFETY_REFUSAL_MESSAGE) is None


def test_extract_text_from_input_handles_structured_items() -> None:
    payload = [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Hello"},
                {"type": "input_text", "text": "world"},
            ],
        }
    ]

    assert extract_text_from_input(payload) == "Hello\nworld"
