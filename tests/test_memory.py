from __future__ import annotations

import pytest
from agents import SQLiteSession


@pytest.mark.asyncio
async def test_sqlite_session_persists_items_across_instances(tmp_path) -> None:
    db_path = tmp_path / "sessions.db"
    first_session = SQLiteSession("memory-demo", db_path=db_path)

    await first_session.add_items([{"role": "user", "content": "Hello"}])

    second_session = SQLiteSession("memory-demo", db_path=db_path)
    items = await second_session.get_items()

    assert len(items) == 1
    assert items[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_sqlite_session_clear_session_removes_history(tmp_path) -> None:
    db_path = tmp_path / "sessions.db"
    session = SQLiteSession("memory-demo", db_path=db_path)

    await session.add_items(
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
    )
    await session.clear_session()

    assert await session.get_items() == []
