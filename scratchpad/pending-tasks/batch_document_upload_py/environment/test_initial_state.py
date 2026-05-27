import importlib
import os
import sys


def test_workspace_dir_exists():
    assert os.path.isdir("/workspace"), "Working directory /workspace does not exist."


def test_python_version():
    assert sys.version_info >= (3, 11), (
        f"Python 3.11+ required, found {sys.version_info.major}.{sys.version_info.minor}."
    )


def test_alchemystai_sdk_importable():
    module = importlib.import_module("alchemyst_ai")
    assert hasattr(module, "AlchemystAI"), (
        "Expected `AlchemystAI` class to be available from the `alchemyst_ai` package."
    )


def test_api_key_env_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."
    )


def test_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set in the task environment."


def test_result_json_not_yet_present():
    assert not os.path.exists("/workspace/result.json"), (
        "/workspace/result.json must not exist before the task starts."
    )
