"""Pytest configuration and shared fixtures.

Uses SQLite (aiosqlite) as the test database to avoid requiring
a running PostgreSQL instance for unit tests.
"""

import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.database import Base, get_db
from app.main import app

# ---------------------------------------------------------------------------
# Test database — SQLite in-memory (no Docker required)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override that uses the test database."""
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Override the database dependency for all tests
app.dependency_overrides[get_db] = _override_get_db


# ---------------------------------------------------------------------------
# Database lifecycle — create/drop tables per test
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Upload directory for tests
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def _test_upload_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Redirect file uploads to a temporary directory for tests."""
    monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(tmp_path))


# ---------------------------------------------------------------------------
# Sample file fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal PDF-like bytes for upload tests."""
    return b"%PDF-1.4 test content for unit testing"


@pytest.fixture
def sample_txt_bytes() -> bytes:
    """Simple text file content for upload tests."""
    return b"This is a sample text document for testing purposes."
