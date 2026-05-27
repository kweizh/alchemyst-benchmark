"""Initial-state setup + verification for the conflict_409_handling_py task.

This file does two things in order:
  1. Seeds a v1 document into Alchemyst using identifiers derived from `ZEALT_RUN_ID`
     (source = `conflict409-{run_id}`, file_name = `policy-{run_id}.md`,
     group = `conflict-eval-{run_id}`). The seed is performed by an autouse,
     session-scoped fixture so it runs before any verification test in this file.
  2. Validates that:
       a. The Alchemyst Python SDK (`alchemyst_ai`) is importable.
       b. The project directory `/home/user/myproject` exists and is writable.
       c. The required env vars (`ALCHEMYST_AI_API_KEY`, `ZEALT_RUN_ID`) are present.
       d. The pre-seeded v1 document (containing `POLICY_V1_MARKER`) is retrievable.

The seeding step tolerates an existing v1 document (idempotent on re-runs against
the same Alchemyst account) and does NOT delete any v2 document — that is the job
under test.
"""

from __future__ import annotations

import importlib.util
import os
import time

import pytest


PROJECT_DIR = "/home/user/myproject"

V1_CONTENT_TEMPLATE = (
    "Refund policy version 1 for file {file_name}: customers may request a "
    "refund within 30 days of purchase. Free standard shipping is included. "
    "Run id: {run_id}. POLICY_V1_MARKER."
)


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID must be set in the task environment."
    return run_id


def _identifiers():
    run_id = _run_id()
    return {
        "run_id": run_id,
        "source": f"conflict409-{run_id}",
        "file_name": f"policy-{run_id}.md",
        "group": f"conflict-eval-{run_id}",
    }


# ---------------------------------------------------------------------------
# Seeding fixture (runs once before any test in this file).
# ---------------------------------------------------------------------------


def _seed_v1_document() -> None:
    from alchemyst_ai import AlchemystAI

    client = AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])
    ids = _identifiers()
    content = V1_CONTENT_TEMPLATE.format(file_name=ids["file_name"], run_id=ids["run_id"])
    documents = [
        {
            "content": content,
            "metadata": {
                "file_name": ids["file_name"],
                "file_type": "text/markdown",
                "group_name": [ids["group"]],
            },
        }
    ]
    try:
        client.with_options(max_retries=0).v1.context.add(
            documents=documents,
            context_type="resource",
            scope="internal",
            source=ids["source"],
            metadata={
                "file_name": ids["file_name"],
                "file_type": "text/markdown",
                "group_name": [ids["group"]],
            },
        )
    except Exception as e:  # noqa: BLE001
        # If the v1 doc already exists (e.g., retry), treat that as success: the
        # collision target is satisfied.
        status_code = getattr(e, "status_code", None)
        if status_code != 409:
            raise


@pytest.fixture(scope="session", autouse=True)
def _seed_initial_state():
    if importlib.util.find_spec("alchemyst_ai") is None:
        pytest.fail("alchemyst_ai SDK is not installed; cannot seed initial state.")
    if not os.environ.get("ALCHEMYST_AI_API_KEY"):
        pytest.fail("ALCHEMYST_AI_API_KEY must be set to seed the initial state.")
    if not os.environ.get("ZEALT_RUN_ID"):
        pytest.fail("ZEALT_RUN_ID must be set to seed the initial state.")
    _seed_v1_document()
    # Allow Alchemyst a brief moment to index before validation queries it.
    time.sleep(3)
    yield


# ---------------------------------------------------------------------------
# Validation tests.
# ---------------------------------------------------------------------------


def test_alchemyst_sdk_importable():
    assert importlib.util.find_spec("alchemyst_ai") is not None, (
        "Alchemyst Python SDK package `alchemyst_ai` is not importable. "
        "It must be installed in the task environment."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist; the task setup must create it."
    )
    assert os.access(PROJECT_DIR, os.W_OK), (
        f"Project directory {PROJECT_DIR} is not writable for the executor."
    )


def test_required_env_vars_present():
    required = ["ALCHEMYST_AI_API_KEY", "ZEALT_RUN_ID"]
    missing = [k for k in required if not os.environ.get(k)]
    assert not missing, (
        f"Required environment variables are missing or empty: {missing}. "
        "These must be exported by the task environment."
    )


def _ctx_content(ctx) -> str:
    if isinstance(ctx, dict):
        content = ctx.get("content")
    else:
        content = getattr(ctx, "content", None)
    return content if isinstance(content, str) else ""


def test_pre_seeded_v1_document_is_indexed():
    from alchemyst_ai import AlchemystAI

    client = AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])
    ids = _identifiers()
    query = (
        f"Refund policy version 1 thirty days free shipping "
        f"{ids['file_name']} POLICY_V1_MARKER"
    )

    last_err: Exception | None = None
    for attempt in range(8):
        try:
            resp = client.v1.context.search(
                query=query,
                similarity_threshold=0.95,
                minimum_similarity_threshold=0.3,
                scope="internal",
            )
            contexts = getattr(resp, "contexts", None) or []
            if any("POLICY_V1_MARKER" in _ctx_content(c) for c in contexts):
                return
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(5)
    if last_err is not None:
        pytest.fail(
            "Search for pre-seeded v1 document kept failing: " + repr(last_err)
        )
    pytest.fail(
        "Pre-seeded v1 document (POLICY_V1_MARKER) was not retrievable from "
        "Alchemyst after seeding. The seeding fixture may not have run successfully."
    )
