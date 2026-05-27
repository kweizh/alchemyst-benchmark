import os
import re
import time

import pytest
import requests


LOG_FILE = "/home/user/update_task/output.log"
ALCHEMYST_BASE_URL = "https://platform-backend.getalchemystai.com"
NEW_PHRASE = "Effective date: 2025-05-01"
OLD_PHRASE = "Effective date: 2024-01-01"


@pytest.fixture(scope="module")
def run_id():
    rid = os.environ.get("ZEALT_RUN_ID", "")
    assert rid, "ZEALT_RUN_ID environment variable must be set for verification."
    return rid


@pytest.fixture(scope="module")
def api_key():
    key = os.environ.get("ALCHEMYST_AI_API_KEY", "")
    assert key, (
        "ALCHEMYST_AI_API_KEY environment variable must be set for verification."
    )
    return key


@pytest.fixture(scope="module")
def log_contents():
    assert os.path.isfile(LOG_FILE), (
        f"Expected log file at {LOG_FILE}, but it does not exist."
    )
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()


def test_log_file_contains_updated_file_name(log_contents, run_id):
    pattern = re.compile(
        r"^\s*Updated file_name:\s*(onboarding_v1-"
        + re.escape(run_id)
        + r"\.md)\s*$",
        re.MULTILINE,
    )
    match = pattern.search(log_contents)
    assert match, (
        "Expected a line matching exactly "
        f"'Updated file_name: onboarding_v1-{run_id}.md' in {LOG_FILE}. "
        f"Actual content:\n{log_contents}"
    )


def test_log_file_contains_update_status_success(log_contents):
    pattern = re.compile(r"^\s*Update status:\s*success\s*$", re.MULTILINE)
    match = pattern.search(log_contents)
    assert match, (
        f"Expected a line matching 'Update status: success' in {LOG_FILE}. "
        f"Actual content:\n{log_contents}"
    )


def _search_contents(api_key: str, run_id: str) -> list[str]:
    """Run a relevant semantic search and return the list of returned content strings."""
    url = f"{ALCHEMYST_BASE_URL}/api/v1/context/search"
    payload = {
        "query": "What is the onboarding effective date?",
        "similarity_threshold": 0.3,
        "scope": "internal",
        "metadata": {"groupName": [run_id]},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    if response.status_code != 200:
        return []
    body = response.json() or {}
    contexts = body.get("contexts") or []
    return [
        (ctx.get("content") or "")
        for ctx in contexts
        if isinstance(ctx, dict)
    ]


def test_new_policy_retrievable_and_old_gone(api_key, run_id):
    """After the agent runs, the v2 document must be retrievable and v1 must be gone."""
    last_contents: list[str] = []
    found_new = False
    for _ in range(5):
        last_contents = _search_contents(api_key, run_id)
        if any(NEW_PHRASE in c for c in last_contents):
            found_new = True
            break
        time.sleep(3)

    assert found_new, (
        "Expected at least one returned context from the real Alchemyst search "
        f"scoped to group '{run_id}' to contain the new policy phrase "
        f"'{NEW_PHRASE}' after the agent's update, but got: {last_contents!r}"
    )

    # The old policy content must no longer be present in any returned chunk.
    stale_chunks = [c for c in last_contents if OLD_PHRASE in c]
    assert not stale_chunks, (
        "Expected no returned context to contain the old policy phrase "
        f"'{OLD_PHRASE}' after the agent's update, but found: {stale_chunks!r}"
    )
