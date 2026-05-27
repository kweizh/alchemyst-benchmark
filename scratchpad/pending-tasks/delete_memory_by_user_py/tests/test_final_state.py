import json
import os
import re
import time

import pytest

LOG_FILE = "/home/user/myproject/output.log"
POST_DELETE_SEARCH_JSON = "/workspace/post_delete_search.json"


def _read_log():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()


def test_log_file_exists():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."


def test_log_contains_status_success():
    content = _read_log()
    assert re.search(r"^Status:\s*success\s*$", content, re.MULTILINE), (
        f"Log file {LOG_FILE} must contain a line matching 'Status: success'. "
        f"Got:\n{content}"
    )


def test_log_contains_run_id_scoped_user_and_session():
    content = _read_log()
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID env var must be set in the verifier environment."

    user_match = re.search(r"^UserId:\s*(\S+)\s*$", content, re.MULTILINE)
    session_match = re.search(r"^SessionId:\s*(\S+)\s*$", content, re.MULTILINE)

    assert user_match, f"Log file must contain a 'UserId: <userId>' line. Got:\n{content}"
    assert session_match, f"Log file must contain a 'SessionId: <sessionId>' line. Got:\n{content}"

    user_id = user_match.group(1)
    session_id = session_match.group(1)

    assert run_id in user_id, (
        f"userId '{user_id}' must contain the run-id '{run_id}' for parallel-run isolation."
    )
    assert run_id in session_id, (
        f"sessionId '{session_id}' must contain the run-id '{run_id}' for parallel-run isolation."
    )


def test_post_delete_search_json_exists_and_is_valid_json():
    assert os.path.isfile(POST_DELETE_SEARCH_JSON), (
        f"{POST_DELETE_SEARCH_JSON} does not exist; the task must write the post-deletion "
        f"search result there."
    )
    with open(POST_DELETE_SEARCH_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)  # Will raise if not valid JSON.
    assert data is not None, f"{POST_DELETE_SEARCH_JSON} is empty."


def test_post_delete_search_json_does_not_mention_bumble():
    with open(POST_DELETE_SEARCH_JSON, "r", encoding="utf-8") as f:
        raw = f.read()
    assert "bumble" not in raw.lower(), (
        f"{POST_DELETE_SEARCH_JSON} still contains 'Bumble' (case-insensitive); "
        f"the memory was not actually deleted. Content:\n{raw}"
    )


def test_live_search_no_longer_returns_bumble():
    """Re-run a search against the live Alchemyst AI platform to confirm deletion propagated."""
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set in the verifier environment."

    content = _read_log()
    user_match = re.search(r"^UserId:\s*(\S+)\s*$", content, re.MULTILINE)
    assert user_match, "Log file must contain a 'UserId: <userId>' line."
    user_id = user_match.group(1)

    try:
        from alchemyst_ai import AlchemystAI
    except ImportError as e:  # pragma: no cover
        pytest.fail(f"`alchemyst_ai` SDK is not importable in the verifier env: {e}")

    client = AlchemystAI(api_key=api_key)

    # Give the platform a few seconds to fully propagate the deletion before re-checking.
    last_text = ""
    for _ in range(6):
        try:
            response = client.v1.context.search(
                query="Bumble",
                similarity_threshold=0.5,
                minimum_similarity_threshold=0.3,
                user_id=user_id,
            )
        except Exception as e:  # pragma: no cover
            pytest.fail(f"Live context.search call failed: {e}")

        # Serialize response to a string for substring inspection.
        try:
            payload = response.to_dict()
        except AttributeError:
            try:
                payload = response.model_dump()
            except AttributeError:
                payload = str(response)
        last_text = json.dumps(payload, default=str)
        if "bumble" not in last_text.lower():
            return
        time.sleep(5)

    pytest.fail(
        f"Live Alchemyst search for user_id='{user_id}' still references 'Bumble' after "
        f"deletion. Latest response:\n{last_text}"
    )
