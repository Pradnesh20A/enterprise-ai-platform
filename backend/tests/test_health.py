"""Tests for the health check endpoint."""

from httpx import AsyncClient


async def test_health_returns_200(client: AsyncClient):
    """GET /health should return 200 with status, version, and timestamp."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data


async def test_health_response_schema(client: AsyncClient):
    """Health response should contain exactly the expected fields."""
    response = await client.get("/health")
    data = response.json()

    expected_keys = {"status", "version", "timestamp"}
    assert set(data.keys()) == expected_keys
