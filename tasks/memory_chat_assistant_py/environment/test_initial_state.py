import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_alchemyst_ai_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except ImportError as e:
        pytest.fail(
            f"The 'alchemyst_ai' Python SDK is not importable: {e}. "
            "Ensure 'alchemystai==0.10.0' is installed in the environment."
        )


def test_openai_sdk_importable():
    try:
        importlib.import_module("openai")
    except ImportError as e:
        pytest.fail(f"The 'openai' Python SDK is not importable: {e}.")


def test_alchemyst_api_key_env_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable is not set."
    )


def test_openai_api_key_env_present():
    assert os.environ.get("OPENAI_API_KEY"), (
        "OPENAI_API_KEY environment variable is not set."
    )


def test_zealt_run_id_env_present():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "ZEALT_RUN_ID environment variable is not set; "
        "required for namespacing concurrent runs."
    )
