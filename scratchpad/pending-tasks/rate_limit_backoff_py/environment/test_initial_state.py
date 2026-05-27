import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_alchemyst_ai_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except ImportError as exc:  # pragma: no cover - reported via assertion
        pytest.fail(f"alchemyst_ai SDK is not importable: {exc}")


def test_alchemyst_api_key_env_set():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."


def test_zealt_run_id_env_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set in the task environment."
    assert run_id.startswith("zr-"), (
        f"ZEALT_RUN_ID must start with 'zr-' (got: {run_id!r})."
    )


def test_report_file_does_not_exist_yet():
    report_path = os.path.join(PROJECT_DIR, "backoff_report.json")
    assert not os.path.exists(report_path), (
        f"Expected {report_path} to not yet exist before the executor runs the task."
    )
