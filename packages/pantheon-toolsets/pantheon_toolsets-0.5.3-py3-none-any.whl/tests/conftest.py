"""
pytest configuration for remote backend tests
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean up environment variables before each test"""
    # Save original values
    original_values = {}
    env_vars_to_clean = [
        "PANTHEON_REMOTE_BACKEND",
        "NATS_SERVERS",
        "NATS_STREAM_NAME",
        "NATS_CONSUMER_GROUP"
    ]
    
    for var in env_vars_to_clean:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


# Pytest async settings
pytest_plugins = ['pytest_asyncio']