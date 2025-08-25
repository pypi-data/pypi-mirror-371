"""
Pytest configuration and fixtures for project-conf tests.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
import pytest

import project_conf.core


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Create some project markers
        (project_path / '.git').mkdir()
        (project_path / 'pyproject.toml').touch()

        yield project_path
        # Cleanup happens automatically with TemporaryDirectory context manager


@pytest.fixture
def sample_defaults() -> Dict[str, Any]:
    """Sample configuration defaults for testing."""
    return {
        'database_url': 'sqlite:///test.db',
        'debug': False,
        'max_workers': 4,
        'timeout': 30.0,
        'api_key': '',
        'features': ['auth', 'cache'],
        'nested': {
            'setting': 'value'
        }
    }


@pytest.fixture
def env_file_content() -> str:
    """Sample .env file content for testing."""
    return """
# Database configuration
DATABASE_URL=postgresql://localhost/prod
DEBUG=true

# Worker configuration
MAX_WORKERS=8
TIMEOUT=60.0

# API configuration
API_KEY=secret-key-123

# Features (JSON array)
FEATURES=["auth", "cache", "admin"]

# Comments and empty lines should be ignored

EMPTY_VALUE=
QUOTED_VALUE="quoted string"
SINGLE_QUOTED='single quoted'
"""


@pytest.fixture
def create_env_file(temp_project_dir: Path, env_file_content: str):
    """Create a .env file in the temporary project directory."""
    env_file = temp_project_dir / '.env'
    env_file.write_text(env_file_content)
    return env_file


@pytest.fixture(autouse=True)
def reset_global_config():
    """Reset global configuration before each test."""
    original_config = project_conf.core._global_config
    project_conf.core._global_config = None

    yield

    # Restore original config after test
    project_conf.core._global_config = original_config


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    def _mock_env_vars(env_vars: Dict[str, str]):
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
    
    return _mock_env_vars
