import importlib
import os

import pytest

PROJECT_DIR = "/home/user/syllabai"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_alchemystai_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except Exception as exc:  # pragma: no cover - diagnostic
        pytest.fail(
            "Expected the Alchemyst AI Python SDK ('alchemyst_ai' from the "
            f"'alchemystai' package) to be importable, but got: {exc!r}"
        )


def test_openai_sdk_importable():
    try:
        importlib.import_module("openai")
    except Exception as exc:  # pragma: no cover - diagnostic
        pytest.fail(
            f"Expected the OpenAI Python SDK to be importable, but got: {exc!r}"
        )


def test_alchemyst_api_key_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."
    )


def test_openai_api_key_present():
    assert os.environ.get("OPENAI_API_KEY"), (
        "OPENAI_API_KEY environment variable must be set in the task environment."
    )


def test_zealt_run_id_present():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable must be set to namespace resources."
