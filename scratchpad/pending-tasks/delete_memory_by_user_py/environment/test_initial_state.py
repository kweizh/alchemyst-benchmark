import importlib
import os
import sys

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_python_version():
    assert sys.version_info >= (3, 11), (
        f"Python 3.11+ is required, found {sys.version_info.major}.{sys.version_info.minor}."
    )


def test_alchemyst_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except ImportError as e:
        pytest.fail(f"`alchemyst_ai` Python SDK is not importable: {e}")


def test_alchemyst_api_key_set():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable must be set."


def test_zealt_run_id_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_workspace_dir_exists():
    assert os.path.isdir("/workspace"), "/workspace directory does not exist."
