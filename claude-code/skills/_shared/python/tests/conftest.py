"""
Pytest configuration and shared fixtures.

This module provides common fixtures used across all test files,
including temporary directory setup and sys.path configuration.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to sys.path to import layer modules
SHARED_PYTHON_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SHARED_PYTHON_DIR))


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files.

    Args:
        tmp_path: pytest built-in temporary directory fixture.

    Returns:
        Path object pointing to a temporary directory.
    """
    return tmp_path


@pytest.fixture
def sample_json_data():
    """Provide sample JSON data for testing.

    Returns:
        Dictionary with sample structured data.
    """
    return {
        "name": "test",
        "version": "1.0.0",
        "items": [1, 2, 3],
        "metadata": {"created": "2026-01-30", "author": "test"},
    }


@pytest.fixture
def sample_task_id():
    """Provide sample task ID for testing.

    Returns:
        Valid task ID string.
    """
    return "2.3.1"
