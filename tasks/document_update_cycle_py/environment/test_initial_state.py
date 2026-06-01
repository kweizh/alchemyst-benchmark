import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_alchemystai_sdk_importable():
    # The Alchemyst AI Python SDK must be pre-installed in the environment.
    import importlib

    module = importlib.import_module("alchemyst_ai")
    assert module is not None, "alchemyst_ai Python SDK is not importable."


def test_alchemyst_api_key_env_present():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, (
        "ALCHEMYST_AI_API_KEY environment variable is not set in the task environment."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable is not set in the task environment."
    )
