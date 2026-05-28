import os
import re

import pytest
import requests


LOG_FILE = "/home/user/rag_task/output.log"
ALCHEMYST_BASE_URL = "https://platform-backend.getalchemystai.com"


@pytest.fixture(scope="module")
def run_id():
    rid = os.environ.get("ZEALT_RUN_ID", "")
    assert rid, "ZEALT_RUN_ID environment variable must be set for verification."
    return rid


@pytest.fixture(scope="module")
def api_key():
    key = os.environ.get("ALCHEMYST_AI_API_KEY", "")
    assert key, "ALCHEMYST_AI_API_KEY environment variable must be set for verification."
    return key


@pytest.fixture(scope="module")
def log_contents():
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}, but it does not exist."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()


def test_log_file_contains_stored_file_name(log_contents, run_id):
    pattern = re.compile(
        r"^Stored file_name:\s*(faq-" + re.escape(run_id) + r"-[0-9a-fA-F-]+\.md)\s*$",
        re.MULTILINE,
    )
    match = pattern.search(log_contents)
    assert match, (
        f"Expected a line matching 'Stored file_name: faq-{run_id}-<uuid>.md' "
        f"in {LOG_FILE}. Actual content:\n{log_contents}"
    )


def test_log_file_contains_search_matches(log_contents):
    pattern = re.compile(r"^Search matches:\s*(\d+)\s*$", re.MULTILINE)
    match = pattern.search(log_contents)
    assert match, (
        f"Expected a line matching 'Search matches: <N>' in {LOG_FILE}. "
        f"Actual content:\n{log_contents}"
    )
    count = int(match.group(1))
    assert count >= 1, (
        f"Expected 'Search matches' to be >= 1, got {count}. Log:\n{log_contents}"
    )


def test_log_file_contains_top_snippet(log_contents):
    pattern = re.compile(r"^Top snippet:\s*(.+)$", re.MULTILINE)
    match = pattern.search(log_contents)
    assert match, (
        f"Expected a line starting with 'Top snippet:' in {LOG_FILE}. "
        f"Actual content:\n{log_contents}"
    )
    snippet = match.group(1)
    assert "30-day money back guarantee" in snippet.lower() or (
        "30-day money back guarantee" in snippet
    ), (
        f"Expected the top snippet to contain '30-day money back guarantee'. "
        f"Got: {snippet}"
    )


def test_document_persisted_in_alchemyst(run_id, api_key):
    """
    Use the real Alchemyst API to verify the document is searchable in the
    context store within the run-id-scoped group. This confirms that the
    agent did NOT mock the SDK and actually ingested the document.
    """
    url = f"{ALCHEMYST_BASE_URL}/api/v1/context/search"
    payload = {
        "query": "refund policy",
        "similarity_threshold": 0.3,
        "scope": "internal",
        "metadata": {"groupName": [run_id]},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    assert response.status_code == 200, (
        f"Alchemyst search API returned status {response.status_code}: "
        f"{response.text}"
    )
    body = response.json()
    contexts = body.get("contexts") or []
    assert len(contexts) >= 1, (
        "Expected at least one context returned from Alchemyst search "
        f"scoped to group '{run_id}', got 0. Response: {body}"
    )
    combined = " ".join(
        (ctx.get("content") or "") for ctx in contexts if isinstance(ctx, dict)
    )
    assert "30-day money back guarantee" in combined, (
        "Expected at least one returned context to contain "
        f"'30-day money back guarantee'. Got contexts: {contexts}"
    )
