"""Shared fixtures for the test suite."""

import pytest

from fraudfirstaid.llm.gateway import FakeLLM


class FakeUsage:
    """Fake usage repository for API tests."""

    async def by_day(self, days: int = 7) -> list[dict]:
        return [
            {
                "day": "2026-11-25",
                "calls": 3,
                "errors": 1,
                "fallbacks": 1,
                "tokens_in": 300,
                "tokens_out": 120,
                "cost_inr": 0.0642,
            }
        ]


@pytest.fixture
def llm() -> FakeLLM:
    """The fake model behind /v1/chat in unit tests."""
    return FakeLLM()
