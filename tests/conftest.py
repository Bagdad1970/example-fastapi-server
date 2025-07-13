import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from website.database import AsyncSessionLocal, init_db as create_tables
from website.main import app


@pytest_asyncio.fixture(scope="session")
async def init_db() -> None:
    await create_tables()


@pytest_asyncio.fixture
async def session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.close()


@pytest_asyncio.fixture(autouse=True)
async def test_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client