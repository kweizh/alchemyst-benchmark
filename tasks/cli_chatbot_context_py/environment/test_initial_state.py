import os
import shutil
import subprocess
import sys


PROJECT_DIR = "/home/user/cli-chatbot"


def test_python_available():
    assert shutil.which("python") is not None or shutil.which("python3") is not None, (
        "python interpreter not found in PATH."
    )


def test_python_version_at_least_3_11():
    info = sys.version_info
    assert (info.major, info.minor) >= (3, 11), (
        f"Python 3.11+ is required, found {info.major}.{info.minor}."
    )


def test_alchemystai_sdk_importable():
    # The pip package is `alchemystai`, but the importable module name is `alchemyst_ai`.
    result = subprocess.run(
        [sys.executable, "-c", "import alchemyst_ai"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "The Alchemyst AI Python SDK (pip package `alchemystai`, import name "
        "`alchemyst_ai`) must be importable in the task environment. "
        f"stderr: {result.stderr}"
    )


def test_openai_sdk_importable():
    result = subprocess.run(
        [sys.executable, "-c", "import openai"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "The `openai` Python SDK must be importable in the task environment. "
        f"stderr: {result.stderr}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist as the working directory for the CLI task."
    )


def test_workspace_directory_exists():
    assert os.path.isdir("/workspace"), (
        "Expected /workspace directory to exist for capturing the CLI reply file."
    )


def test_alchemyst_api_key_env_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."
    )


def test_openai_api_key_env_present():
    assert os.environ.get("OPENAI_API_KEY"), (
        "OPENAI_API_KEY environment variable must be set in the task environment."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set in the task environment."
