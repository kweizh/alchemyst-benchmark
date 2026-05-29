import os
import pytest

PROJECT_DIR = "/home/user/alchemyst-memory"

def test_alchemystai_sdk_available():
    try:
        import alchemystai
    except ImportError:
        pytest.fail("alchemystai SDK is not installed or importable.")

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_api_key_environment_variable_exists():
    assert "ALCHEMYST_AI_API_KEY" in os.environ, "ALCHEMYST_AI_API_KEY environment variable is not set."
