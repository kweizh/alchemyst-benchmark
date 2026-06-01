import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_alchemyst_ai_sdk_importable():
    pytest.importorskip(
        "alchemyst_ai",
        reason="alchemystai Python SDK (import name 'alchemyst_ai') must be installed in the environment.",
    )


def test_alchemyst_ai_api_key_env_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set for the CLI to authenticate "
        "against the real Alchemyst AI API."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set so the CLI can namespace resources."
    assert run_id.startswith("zr-"), (
        f"ZEALT_RUN_ID is expected to match the pattern 'zr-[a-z0-9]+'; got {run_id!r}."
    )
