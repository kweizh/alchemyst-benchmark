import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task runs."
    )


def test_alchemyst_sdk_importable():
    try:
        module = importlib.import_module("alchemyst_ai")
    except ImportError as exc:  # pragma: no cover - the assertion below explains the failure
        pytest.fail(
            "The Alchemyst AI Python SDK (`alchemystai` package, importable as "
            f"`alchemyst_ai`) is not installed in the environment: {exc}"
        )
    assert hasattr(module, "AlchemystAI"), (
        "Expected `alchemyst_ai.AlchemystAI` to be available from the installed SDK."
    )


def test_alchemyst_api_key_env_var_present():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."
    )


def test_zealt_run_id_env_var_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set so the task can produce a "
        "unique metadata.file_name and avoid 409 Conflict errors."
    )
