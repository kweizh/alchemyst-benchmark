import os
import importlib
import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_alchemystai_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except ImportError as exc:
        pytest.fail(
            "The Alchemyst AI Python SDK (`alchemyst_ai`) is not importable: "
            f"{exc}"
        )


def test_alchemyst_api_key_env_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable is not set in the task "
        "environment."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."


def test_python3_available():
    import shutil
    assert shutil.which("python3") is not None, (
        "python3 binary not found in PATH."
    )
