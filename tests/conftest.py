import pytest
from unittest.mock import AsyncMock

@pytest.fixture(scope="session")
def mock_redis():
    # Replace with aioredis mock or similar
    return AsyncMock()

@pytest.fixture(scope="session")
def mock_qdrant():
    # Replace with Qdrant client mock
    return AsyncMock()

@pytest.fixture(scope="session")
def mock_llm():
    # Replace with LLM service mock
    return AsyncMock()
