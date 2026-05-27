import json
import os
import time

import pytest
import requests

RECALL_FILE = "/workspace/recall.json"
ALCHEMYST_BASE_URL = "https://platform-backend.getalchemystai.com"


@pytest.fixture(scope="module")
def recall_data():
    assert os.path.isfile(RECALL_FILE), (
        f"Expected recall output file at {RECALL_FILE}, but it was not found."
    )
    with open(RECALL_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"{RECALL_FILE} is not valid JSON: {exc}. Raw content: {raw[:500]!r}"
        )
    assert isinstance(data, dict), (
        f"Expected the recall file to contain a JSON object, "
        f"got {type(data).__name__}."
    )
    return data


def test_recall_json_has_required_top_level_fields(recall_data):
    for key in ("userId", "sessionA", "sessionB", "query", "contexts"):
        assert key in recall_data, (
            f"recall.json is missing required top-level field {key!r}. "
            f"Found keys: {sorted(recall_data.keys())}"
        )
    assert isinstance(recall_data["userId"], str) and recall_data["userId"], (
        "userId must be a non-empty string."
    )
    assert isinstance(recall_data["sessionA"], str) and recall_data["sessionA"], (
        "sessionA must be a non-empty string."
    )
    assert isinstance(recall_data["sessionB"], str) and recall_data["sessionB"], (
        "sessionB must be a non-empty string."
    )
    assert isinstance(recall_data["query"], str) and recall_data["query"], (
        "query must be a non-empty string."
    )
    assert isinstance(recall_data["contexts"], list), (
        f"contexts must be a list, got {type(recall_data['contexts']).__name__}."
    )


def test_sessions_are_distinct(recall_data):
    assert recall_data["sessionA"] != recall_data["sessionB"], (
        "sessionA and sessionB must differ to demonstrate cross-session recall."
    )


def test_ids_include_zealt_run_id(recall_data):
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for verification."
    for key in ("userId", "sessionA", "sessionB"):
        assert run_id in recall_data[key], (
            f"Expected {key}={recall_data[key]!r} to include the ZEALT_RUN_ID "
            f"{run_id!r} as a substring for parallel-run isolation."
        )


def test_recall_contains_rust(recall_data):
    contexts = recall_data["contexts"]
    assert len(contexts) > 0, (
        "Expected at least one element in contexts, got an empty list."
    )
    matching = [
        ctx
        for ctx in contexts
        if isinstance(ctx, dict)
        and isinstance(ctx.get("content"), str)
        and "Rust" in ctx["content"]
    ]
    assert matching, (
        "Expected at least one context whose 'content' contains the substring "
        f"'Rust'. Got contexts: {contexts!r}"
    )


def test_alchemyst_api_confirms_rust_memory():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set to verify against the live API."

    url = f"{ALCHEMYST_BASE_URL}/api/v1/context/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": "What is the user's preferred coding language?",
        "similarity_threshold": 0.8,
        "minimum_similarity_threshold": 0.5,
        "scope": "internal",
    }

    last_response_text = ""
    for attempt in range(3):
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        assert response.status_code == 200, (
            f"Alchemyst search returned status {response.status_code}: "
            f"{response.text!r}"
        )
        body = response.json()
        contexts = body.get("contexts") or []
        for ctx in contexts:
            content = ctx.get("content") if isinstance(ctx, dict) else None
            if isinstance(content, str) and "Rust" in content:
                return
        last_response_text = response.text
        time.sleep(2)

    pytest.fail(
        "Live Alchemyst search did not return a context containing 'Rust' after "
        f"3 attempts. Last response body: {last_response_text!r}"
    )
