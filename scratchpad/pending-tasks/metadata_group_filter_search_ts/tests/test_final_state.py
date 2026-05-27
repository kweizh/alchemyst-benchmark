import json
import os
import subprocess
import time

import pytest
import requests

RESULT_PATH = "/workspace/group_result.json"
ALCHEMYST_API_BASE = "https://platform-backend.getalchemystai.com/api/v1"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _alpha_group() -> str:
    return f"alpha-{_run_id()}"


def _beta_group() -> str:
    return f"beta-{_run_id()}"


def _api_key() -> str:
    key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert key, "ALCHEMYST_AI_API_KEY environment variable is not set."
    return key


@pytest.fixture(scope="module")
def result_data():
    assert os.path.isfile(RESULT_PATH), (
        f"Expected output file {RESULT_PATH} was not created by the task."
    )
    with open(RESULT_PATH, "r") as f:
        return json.load(f)


def test_result_file_is_valid_json(result_data):
    assert isinstance(result_data, dict), (
        f"Expected {RESULT_PATH} to contain a JSON object, got {type(result_data).__name__}."
    )


def test_result_has_required_keys(result_data):
    expected_keys = {"count", "groups"}
    actual_keys = set(result_data.keys())
    assert actual_keys == expected_keys, (
        f"Expected top-level keys {expected_keys} in {RESULT_PATH}, got {actual_keys}."
    )


def test_count_is_int(result_data):
    assert isinstance(result_data["count"], int) and not isinstance(
        result_data["count"], bool
    ), f"'count' must be an integer, got {type(result_data['count']).__name__}."


def test_groups_is_list_of_strings(result_data):
    groups = result_data["groups"]
    assert isinstance(groups, list), (
        f"'groups' must be a list, got {type(groups).__name__}."
    )
    assert all(isinstance(g, str) for g in groups), (
        f"All entries in 'groups' must be strings, got {groups}."
    )


def test_count_at_least_three(result_data):
    assert result_data["count"] >= 3, (
        f"Expected count >= 3 (the three alpha-group documents), got {result_data['count']}."
    )


def test_groups_sorted_and_unique(result_data):
    groups = result_data["groups"]
    assert groups == sorted(set(groups)), (
        f"'groups' must be sorted and de-duplicated, got {groups}."
    )


def test_only_alpha_group_present(result_data):
    alpha = _alpha_group()
    beta = _beta_group()
    groups = result_data["groups"]
    assert beta not in groups, (
        f"Beta group '{beta}' should NOT appear in filtered results, got {groups}."
    )
    assert groups == [alpha], (
        f"Expected groups == ['{alpha}'], got {groups}."
    )


def test_beta_group_was_actually_ingested():
    """Cross-check by calling the Alchemyst search API directly with the beta filter.

    This proves that both groups were ingested and the alpha-only output was the
    result of the camelCase `groupName` filter being applied correctly, not
    missing data.
    """
    beta = _beta_group()
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": "alchemyst test document",
        "similarity_threshold": 0.3,
        "scope": "internal",
        "metadata": {"groupName": [beta]},
    }

    # Try a few times in case indexing is still settling.
    last_resp = None
    contexts = []
    for _ in range(5):
        resp = requests.post(
            f"{ALCHEMYST_API_BASE}/context/search",
            headers=headers,
            json=payload,
            timeout=60,
        )
        last_resp = resp
        if resp.status_code == 200:
            body = resp.json()
            contexts = body.get("contexts") or []
            if contexts:
                break
        time.sleep(5)

    assert last_resp is not None and last_resp.status_code == 200, (
        f"Cross-check beta search failed: HTTP "
        f"{getattr(last_resp, 'status_code', 'no-response')}: "
        f"{getattr(last_resp, 'text', '')}"
    )
    assert len(contexts) >= 1, (
        f"Expected at least one beta-group context to be ingested, got {len(contexts)}."
    )
