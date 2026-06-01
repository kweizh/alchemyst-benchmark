import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. "
        "The initial environment must provision an empty project directory at this path."
    )


def test_alchemystai_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except ImportError as e:
        pytest.fail(
            "The Python package `alchemystai` (import name `alchemyst_ai`) must be installed "
            f"in the initial environment. Import failed with: {e}"
        )


def test_alchemyst_api_key_env_var_set():
    value = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert value, (
        "The ALCHEMYST_AI_API_KEY environment variable must be set in the initial environment "
        "so the task can talk to the real Alchemyst AI service."
    )


def test_zealt_run_id_env_var_set():
    value = os.environ.get("ZEALT_RUN_ID")
    assert value, (
        "The ZEALT_RUN_ID environment variable must be set in the initial environment "
        "so the task can namespace its ingested documents for parallel-safe runs."
    )
