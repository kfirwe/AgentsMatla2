"""Configure the OpenAI client used by the Agents SDK (call once after load_dotenv)."""

from __future__ import annotations

import os

from agents import set_default_openai_client
from openai import AsyncOpenAI


def configure_openai_client() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return

    client_kwargs: dict[str, str] = {"api_key": api_key}

    org = os.getenv("OPENAI_ORG_ID")
    if org:
        client_kwargs["organization"] = org

    project = os.getenv("OPENAI_PROJECT_ID")
    if project:
        client_kwargs["project"] = project

    set_default_openai_client(AsyncOpenAI(**client_kwargs))
