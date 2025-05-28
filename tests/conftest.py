"""Test configuration and fixtures."""

import asyncio
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from orion_vision_core.core.config import Config
from orion_vision_core.core.logging import setup_logging


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_config(temp_dir: Path) -> Config:
    """Create a test configuration."""
    config = Config(
        environment="test",
        debug=True,
        log_level="DEBUG",
        config_dir=temp_dir / "config",
        memory_dir=temp_dir / "memory",
    )
    
    # Create directories
    config.config_dir.mkdir(parents=True, exist_ok=True)
    config.memory_dir.mkdir(parents=True, exist_ok=True)
    
    return config


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Setup logging for tests."""
    setup_logging(level="DEBUG", enable_rich=False)


@pytest.fixture
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "test_memory_1": {
            "id": "test_memory_1",
            "content": "This is a test memory",
            "tags": ["test", "sample"],
            "importance": 5.0,
            "timestamp": 1640995200.0,  # 2022-01-01 00:00:00
        },
        "test_memory_2": {
            "id": "test_memory_2", 
            "content": "Another test memory",
            "tags": ["test"],
            "importance": 3.0,
            "timestamp": 1640995260.0,  # 2022-01-01 00:01:00
        }
    }


@pytest.fixture
def sample_persona_data():
    """Sample persona data for testing."""
    return {
        "ton": "test tone",
        "roller": "test roles",
        "language": "en",
        "response_style": "casual",
        "preferences": {"theme": "dark"},
        "context": {"current_task": "testing"}
    }
