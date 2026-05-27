"""Final-state verification for the conflict_409_handling_py task.

Validates:
  1. `/home/user/myproject/status.json` exists and has the required structure /
     values (conflict_detected, initial_add_status_code, delete_status, re_added,
     file_name, source, run_id).
  2. The NEW v2 content is retrievable from Alchemyst (a search returns a result
     containing the marker substring `POLICY_V2_MARKER`).
  3. The OLD v1 marker `POLICY_V1_MARKER` is no longer the dominant result for a
     v1-style query (best-effort negative check).
  4. Cleanup attempt at the end (best-effort, errors swallowed).
"""

from __future__ import annotations

import json
import os
import time

import pytest


PROJECT_DIR = "/home/user/myproject"
STATUS_PATH = os.path.join(PROJECT_DIR, "status.json")


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID must be set for the verifier."
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
# status.json checks
# ---------------------------------------------------------------------------


def _load_status() -> dict:
    assert os.path.isfile(STATUS_PATH), (
        f"Expected status report at {STATUS_PATH}, but it was not created. "
        "The solution must write a JSON status report after handling the 409 conflict."
    )
    with open(STATUS_PATH, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as e:
            pytest.fail(f"{STATUS_PATH} is not valid JSON: {e}")
            return {}  # pragma: no cover


def test_status_report_conflict_detected():
    data = _load_status()
    assert data.get("conflict_detected") is True, (
        "Expected status.json field 'conflict_detected' to be true (a 409 must have "
        f"been observed and handled). Got: {data.get('conflict_detected')!r}."
    )


def test_status_report_initial_status_code_is_409():
    data = _load_status()
    assert data.get("initial_add_status_code") == 409, (
        "Expected status.json field 'initial_add_status_code' to be 409. "
        f"Got: {data.get('initial_add_status_code')!r}."
    )


def test_status_report_delete_was_successful():
    data = _load_status()
    assert data.get("delete_status") == "success", (
        "Expected status.json field 'delete_status' to be 'success' "
        f"after removing the conflicting document. Got: {data.get('delete_status')!r}."
    )


def test_status_report_re_added_true():
    data = _load_status()
    assert data.get("re_added") is True, (
        "Expected status.json field 're_added' to be true after the recovery add succeeded. "
        f"Got: {data.get('re_added')!r}."
    )


def test_status_report_echo_env_values():
    data = _load_status()
    ids = _identifiers()
    assert data.get("file_name") == ids["file_name"], (
        f"status.json 'file_name' must equal {ids['file_name']!r}; "
        f"got {data.get('file_name')!r}."
    )
    assert data.get("source") == ids["source"], (
        f"status.json 'source' must equal {ids['source']!r}; "
        f"got {data.get('source')!r}."
    )
    assert data.get("run_id") == ids["run_id"], (
        f"status.json 'run_id' must equal {ids['run_id']!r}; "
        f"got {data.get('run_id')!r}."
    )


# ---------------------------------------------------------------------------
# Alchemyst API checks
# ---------------------------------------------------------------------------


def _alchemyst_client():
    pytest.importorskip("alchemyst_ai")
    from alchemyst_ai import AlchemystAI

    return AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])


def _ctx_content(ctx) -> str:
    if isinstance(ctx, dict):
        content = ctx.get("content")
    else:
        content = getattr(ctx, "content", None)
    return content if isinstance(content, str) else ""


def _search_contents(query: str, similarity_threshold: float, min_threshold: float):
    client = _alchemyst_client()
    resp = client.v1.context.search(
        query=query,
        similarity_threshold=similarity_threshold,
        minimum_similarity_threshold=min_threshold,
        scope="internal",
    )
    contexts = getattr(resp, "contexts", None) or []
    return [_ctx_content(c) for c in contexts]


def test_v2_content_retrievable_via_search():
    """The new (re-added) document with POLICY_V2_MARKER must be findable."""
    ids = _identifiers()
    query = (
        f"Refund policy version 2 fourteen days paid shipping "
        f"{ids['file_name']} POLICY_V2_MARKER"
    )
    last_err: Exception | None = None
    for attempt in range(6):
        try:
            contents = _search_contents(query, 0.95, 0.3)
            if any("POLICY_V2_MARKER" in c for c in contents):
                return
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(5)
    if last_err is not None:
        pytest.fail(
            "Search for v2 content kept failing with exception: " + repr(last_err)
        )
    pytest.fail(
        "Search did not return any document containing 'POLICY_V2_MARKER'. "
        "The recovery `add` must store new content carrying this marker."
    )


def test_v1_content_replaced():
    """Best-effort: the old POLICY_V1_MARKER chunk should no longer be retrievable."""
    ids = _identifiers()
    query = (
        f"Refund policy version 1 thirty days free shipping "
        f"{ids['file_name']} POLICY_V1_MARKER"
    )
    saw_v1 = True
    for attempt in range(6):
        try:
            contents = _search_contents(query, 0.95, 0.7)
        except Exception:
            contents = []
        saw_v1 = any("POLICY_V1_MARKER" in c for c in contents)
        if not saw_v1:
            break
        time.sleep(5)
    assert not saw_v1, (
        "The previous v1 document (POLICY_V1_MARKER) is still indexed by Alchemyst. "
        "The solution must delete the conflicting document before re-adding."
    )


@pytest.fixture(scope="session", autouse=True)
def _cleanup_alchemyst_session():
    """Best-effort cleanup after the verifier finishes."""
    yield
    try:
        from alchemyst_ai import AlchemystAI

        client = AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])
        client.v1.context.delete(
            source=_identifiers()["source"],
            organization_id=os.environ.get("ALCHEMYST_ORG_ID", ""),
            by_doc=True,
        )
    except Exception:
        # Cleanup is best-effort; do not affect the verifier outcome.
        pass
