import importlib
import os


WORKSPACE_DIR = "/workspace"


def test_workspace_dir_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Expected workspace directory {WORKSPACE_DIR} to exist before the task runs."
    )


def test_alchemystai_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except ImportError as exc:
        raise AssertionError(
            "alchemyst_ai Python SDK is not importable. Install it with `pip install alchemystai`."
        ) from exc


def test_alchemyst_api_key_env_present():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, (
        "ALCHEMYST_AI_API_KEY environment variable is not set; the SDK cannot authenticate."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable is not set; the task requires it to scope documents."
    )
