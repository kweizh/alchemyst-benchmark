import json
import os

import requests

RECALL_PATH = "/workspace/team_recall.json"
LOG_PATH = "/workspace/output.log"
MEMORY_SEARCH_URL = "https://platform-backend.getalchemystai.com/api/v1/context/memory/search"


def _load_recall():
    assert os.path.isfile(RECALL_PATH), f"Recall report not found at {RECALL_PATH}."
    with open(RECALL_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Recall report at {RECALL_PATH} is not valid JSON: {exc}")


def test_recall_report_shape():
    data = _load_recall()
    assert isinstance(data, dict), "Recall report must be a JSON object."
    for key in ("userA", "userB", "sessionId", "recalled"):
        assert key in data, f"Recall report is missing required field: {key}"
    assert isinstance(data["userA"], str) and data["userA"], "userA must be a non-empty string."
    assert isinstance(data["userB"], str) and data["userB"], "userB must be a non-empty string."
    assert data["userA"] != data["userB"], "userA and userB must be different strings."
    assert isinstance(data["sessionId"], str) and data["sessionId"], (
        "sessionId must be a non-empty string."
    )
    assert isinstance(data["recalled"], list) and len(data["recalled"]) >= 1, (
        "recalled must be a non-empty list of memory entries."
    )


def test_recall_ids_contain_run_id_suffix():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set during verification."
    data = _load_recall()
    assert data["userA"].endswith(run_id), (
        f"userA ({data['userA']}) must end with ZEALT_RUN_ID ({run_id})."
    )
    assert data["userB"].endswith(run_id), (
        f"userB ({data['userB']}) must end with ZEALT_RUN_ID ({run_id})."
    )
    assert data["sessionId"].endswith(run_id), (
        f"sessionId ({data['sessionId']}) must end with ZEALT_RUN_ID ({run_id})."
    )


def test_recalled_memories_contain_falcon():
    data = _load_recall()
    joined = "\n".join(
        item if isinstance(item, str) else json.dumps(item) for item in data["recalled"]
    )
    assert "Falcon" in joined, (
        "Expected at least one recalled memory entry to contain the codename 'Falcon'. "
        f"Recalled content: {joined!r}"
    )


def test_output_log_contains_session_id():
    assert os.path.isfile(LOG_PATH), f"Log file not found at {LOG_PATH}."
    data = _load_recall()
    with open(LOG_PATH, "r") as f:
        log = f.read()
    expected_line = f"Recall complete: {data['sessionId']}"
    assert expected_line in log, (
        f"Expected log line {expected_line!r} not found in {LOG_PATH}.\n"
        f"Log contents:\n{log}"
    )


def test_memory_visible_via_api_for_user_b():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set during verification."
    data = _load_recall()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"userId": data["userB"], "sessionId": data["sessionId"]}
    resp = requests.post(MEMORY_SEARCH_URL, headers=headers, json=payload, timeout=30)
    assert resp.status_code == 200, (
        f"Alchemyst memory search returned HTTP {resp.status_code}: {resp.text}"
    )
    body_text = resp.text
    assert "Falcon" in body_text, (
        "Expected the live Alchemyst memory search response to contain 'Falcon' "
        f"for shared sessionId={data['sessionId']}. Response: {body_text[:1000]}"
    )
