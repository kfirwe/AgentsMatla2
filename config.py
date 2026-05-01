"""
Project-wide configuration for Homework 2.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SESSION_DB_PATH = DATA_DIR / "chat_history.db"

# Best-practice default for the course project: keep the main agents affordable
# while still strong enough for routing, handoffs, and tool use.
DEFAULT_AGENT_MODEL = os.getenv("OPENAI_AGENT_MODEL", "gpt-5.4-mini")

DEFAULT_SESSION_ID = os.getenv("OPENAI_SESSION_ID", "aviv-kfir-homework2")
SAFETY_REFUSAL_MESSAGE = "I cannot process this request due to safety protocols."

RECENT_HISTORY_LIMIT = 40
