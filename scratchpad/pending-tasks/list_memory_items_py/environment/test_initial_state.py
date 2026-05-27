import importlib
import os


WORKSPACE_DIR = "/workspace"


def test_workspace_dir_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Expected project directory {WORKSPACE_DIR} to exist before the task starts."
    )


def test_alchemystai_sdk_importable():
    try:
        importlib.import_module("alchemyst_ai")
    except ImportError as exc:
        raise AssertionError(
            "The `alchemyst_ai` Python SDK must be importable in the task environment "
            f"(install via `pip install alchemystai`). Import error: {exc}"
        )


def test_alchemyst_api_key_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."
    )


def test_zealt_run_id_present():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "ZEALT_RUN_ID environment variable must be set so the task can isolate per-run state."
    )


def test_no_pre_existing_memory_list_file():
    memory_list_path = os.path.join(WORKSPACE_DIR, "memory_list.json")
    assert not os.path.exists(memory_list_path), (
        f"{memory_list_path} must not exist before the task starts; the executor is expected to create it."
    )


def test_no_pre_existing_output_log_file():
    log_path = os.path.join(WORKSPACE_DIR, "output.log")
    assert not os.path.exists(log_path), (
        f"{log_path} must not exist before the task starts; the executor is expected to create it."
    )
