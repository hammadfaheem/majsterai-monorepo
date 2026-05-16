"""Smoke tests for core API behaviour.

These tests run without a real database or external services by patching the
database ping so they pass in CI with no infrastructure available.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Return an AsyncClient wired to the FastAPI app.

    Settings are loaded from apps/api/.env (or environment). JWT_SECRET must
    be set to a valid value; in CI this is injected as an env var.
    """
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "MajsterAI API"


async def test_health_healthy(client: AsyncClient):
    with patch("src.main.ping_db", new_callable=AsyncMock, return_value=True):
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


async def test_health_unhealthy(client: AsyncClient):
    with patch("src.main.ping_db", new_callable=AsyncMock, return_value=False):
        response = await client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"
