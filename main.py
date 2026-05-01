"""
Interactive entrypoint for the Homework 2 multi-agent bot.
"""

from __future__ import annotations

import argparse
import asyncio
import os

from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunConfig,
    Runner,
    SQLiteSession,
    SessionSettings,
)
from dotenv import load_dotenv

from agents_def import router_with_handoffs
from config import (
    DATA_DIR,
    DEFAULT_SESSION_ID,
    RECENT_HISTORY_LIMIT,
    SAFETY_REFUSAL_MESSAGE,
    SESSION_DB_PATH,
)
from guardrails import get_guardrail_user_message


load_dotenv(override=False)


def build_session(session_id: str) -> SQLiteSession:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return SQLiteSession(session_id=session_id, db_path=SESSION_DB_PATH)


def build_run_config() -> RunConfig:
    return RunConfig(session_settings=SessionSettings(limit=RECENT_HISTORY_LIMIT))


async def run_user_turn(message: str, session: SQLiteSession) -> str:
    try:
        result = await Runner.run(
            router_with_handoffs,
            message,
            session=session,
            run_config=build_run_config(),
        )
        return str(result.final_output)
    except InputGuardrailTripwireTriggered as exc:
        return get_guardrail_user_message(
            exc.guardrail_result.output.output_info,
            SAFETY_REFUSAL_MESSAGE,
        )
    except OutputGuardrailTripwireTriggered as exc:
        return get_guardrail_user_message(
            exc.guardrail_result.output.output_info,
            "I could not produce a safe response. Please try again.",
        )


async def run_repl(session_id: str) -> None:
    session = build_session(session_id)
    print("Homework 2 agent is ready.")
    print("Commands: reset, exit, quit")

    while True:
        try:
            message = input("You: ").strip()
        except EOFError:
            print()
            break

        if not message:
            print("Bot: Please enter a non-empty request.")
            continue
        if message.lower() in {"exit", "quit"}:
            break
        if message.lower() == "reset":
            await session.clear_session()
            print("Bot: Conversation memory cleared.")
            continue

        reply = await run_user_turn(message, session)
        print(f"Bot: {reply}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Homework 2 multi-agent bot.")
    parser.add_argument(
        "--session-id",
        default=DEFAULT_SESSION_ID,
        help="Persistent session id for SDK memory.",
    )
    parser.add_argument(
        "--message",
        help="Run a single turn and exit.",
    )
    parser.add_argument(
        "--reset-session",
        action="store_true",
        help="Clear the stored session before running.",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to the environment or a local .env file."
        )

    session = build_session(args.session_id)
    if args.reset_session:
        await session.clear_session()
        if not args.message:
            print("Session cleared.")
            return

    if args.message:
        print(await run_user_turn(args.message, session))
        return

    await run_repl(args.session_id)


if __name__ == "__main__":
    asyncio.run(main())
