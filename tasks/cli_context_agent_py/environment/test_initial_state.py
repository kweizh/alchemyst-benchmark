import importlib
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
NOTES_DIR = os.path.join(PROJECT_DIR, "notes")
SEED_NOTE = os.path.join(NOTES_DIR, "refunds.md")


def test_alchemyst_sdk_importable():
    """The Alchemyst Python SDK must be installed and importable."""
    mod = importlib.import_module("alchemyst_ai")
    assert mod is not None, "Failed to import the `alchemyst_ai` Python SDK."


def test_openai_sdk_importable():
    """The OpenAI Python SDK must be installed and importable."""
    mod = importlib.import_module("openai")
    assert mod is not None, "Failed to import the `openai` Python SDK."


def test_project_directory_exists():
    """The project working directory must exist before the task starts."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_notes_directory_exists():
    """The notes directory must exist so the executor can ingest from it."""
    assert os.path.isdir(NOTES_DIR), (
        f"Expected notes directory {NOTES_DIR} to exist before the task starts."
    )


def test_seed_note_file_exists():
    """A seeded markdown note must be present for the ingest+ask flow."""
    assert os.path.isfile(SEED_NOTE), (
        f"Expected seeded note file {SEED_NOTE} to exist before the task starts."
    )


def test_seed_note_contains_policy_phrase():
    """The seeded note must contain the canonical refund-policy phrase used by the verifier."""
    with open(SEED_NOTE, "r", encoding="utf-8") as fh:
        content = fh.read().lower()
    assert "30-day" in content or "30 day" in content, (
        "Expected the seeded notes/refunds.md to mention a '30-day' refund period "
        "so the OpenAI answer can be grounded on it."
    )


def test_alchemyst_api_key_env_present():
    """The ALCHEMYST_AI_API_KEY environment variable must be available to the task."""
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, (
        "ALCHEMYST_AI_API_KEY must be set in the environment for the task to run."
    )


def test_openai_api_key_env_present():
    """The OPENAI_API_KEY environment variable must be available to the task."""
    api_key = os.environ.get("OPENAI_API_KEY")
    assert api_key, (
        "OPENAI_API_KEY must be set in the environment for the task to run."
    )


def test_zealt_run_id_env_present():
    """The ZEALT_RUN_ID environment variable must be available so the task can scope resources."""
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID must be set so the task can produce a unique file_name."
    )
