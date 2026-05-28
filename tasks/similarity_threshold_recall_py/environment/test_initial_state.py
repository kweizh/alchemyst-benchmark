import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_DIR = "/workspace"


def test_alchemyst_ai_sdk_importable():
    try:
        module = importlib.import_module("alchemyst_ai")
    except ImportError as exc:  # pragma: no cover - failure surfaces via assert
        pytest.fail(f"alchemyst_ai SDK is not importable: {exc}")
    assert module is not None, "alchemyst_ai SDK could not be imported."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_workspace_directory_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Expected output workspace directory {WORKSPACE_DIR} to exist before the task starts."
    )


def test_alchemyst_api_key_env_var_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "Expected ALCHEMYST_AI_API_KEY environment variable to be set before the task starts."
    )


def test_zealt_run_id_env_var_present():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "Expected ZEALT_RUN_ID environment variable to be set before the task starts."
    )


def test_threshold_report_not_yet_created():
    report_path = os.path.join(WORKSPACE_DIR, "threshold_report.json")
    assert not os.path.exists(report_path), (
        f"Expected {report_path} to NOT exist before the task starts; it is the artifact the executor must create."
    )
