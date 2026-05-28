import json
import os
import re


WORKSPACE_DIR = "/workspace"
MEMORY_LIST_FILE = os.path.join(WORKSPACE_DIR, "memory_list.json")
LOG_FILE = os.path.join(WORKSPACE_DIR, "output.log")

REQUIRED_MARKERS = ("MEM_ONE", "MEM_TWO", "MEM_THREE")


def _load_memory_list():
    assert os.path.isfile(MEMORY_LIST_FILE), (
        f"Expected the memory list file to exist at {MEMORY_LIST_FILE} after the task completes."
    )
    with open(MEMORY_LIST_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"Expected {MEMORY_LIST_FILE} to contain a valid JSON object; "
                f"got JSON decode error: {exc}"
            )


def test_memory_list_file_exists_and_is_object():
    data = _load_memory_list()
    assert isinstance(data, dict), (
        f"Expected the contents of {MEMORY_LIST_FILE} to be a JSON object (dict), "
        f"got type {type(data).__name__}."
    )


def test_memory_list_has_required_keys():
    data = _load_memory_list()
    for key in ("user_id", "session_ids", "count", "contents"):
        assert key in data, (
            f"Expected {MEMORY_LIST_FILE} JSON object to contain key '{key}'. "
            f"Got keys: {sorted(data.keys())!r}"
        )


def test_memory_list_user_id_includes_run_id():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set in the verifier environment "
        "to validate per-run identifiers."
    )
    data = _load_memory_list()
    user_id = data.get("user_id")
    assert isinstance(user_id, str) and user_id, (
        f"Expected 'user_id' to be a non-empty string in {MEMORY_LIST_FILE}; got {user_id!r}."
    )
    assert run_id in user_id, (
        f"Expected 'user_id' ({user_id!r}) to embed the ZEALT_RUN_ID ({run_id!r}) "
        "so that concurrent task runs do not collide."
    )


def test_memory_list_session_ids_are_two_distinct_strings():
    data = _load_memory_list()
    session_ids = data.get("session_ids")
    assert isinstance(session_ids, list), (
        f"Expected 'session_ids' to be a list in {MEMORY_LIST_FILE}; got type "
        f"{type(session_ids).__name__}."
    )
    assert len(session_ids) == 2, (
        f"Expected 'session_ids' to contain exactly 2 entries; got {len(session_ids)}: {session_ids!r}."
    )
    for sid in session_ids:
        assert isinstance(sid, str) and sid, (
            f"Expected every session id to be a non-empty string; got {sid!r} in {session_ids!r}."
        )
    assert len(set(session_ids)) == 2, (
        f"Expected the two session ids to be distinct; got duplicates: {session_ids!r}."
    )


def test_memory_list_count_is_consistent_and_at_least_three():
    data = _load_memory_list()
    count = data.get("count")
    contents = data.get("contents")
    assert isinstance(count, int) and not isinstance(count, bool), (
        f"Expected 'count' to be an integer in {MEMORY_LIST_FILE}; got type "
        f"{type(count).__name__} value {count!r}."
    )
    assert count >= 3, (
        f"Expected 'count' to be at least 3 (three memory items were stored); got {count}."
    )
    assert isinstance(contents, list), (
        f"Expected 'contents' to be a list in {MEMORY_LIST_FILE}; got type "
        f"{type(contents).__name__}."
    )
    assert len(contents) == count, (
        f"Expected 'count' ({count}) to equal len(contents) ({len(contents)}) in {MEMORY_LIST_FILE}."
    )
    for entry in contents:
        assert isinstance(entry, str), (
            f"Expected every entry of 'contents' to be a string; got {entry!r} "
            f"(type {type(entry).__name__})."
        )


def test_memory_list_contents_include_all_markers():
    data = _load_memory_list()
    contents = data.get("contents") or []
    combined = "\n".join(contents)
    missing = [m for m in REQUIRED_MARKERS if m not in combined]
    assert not missing, (
        f"Expected combined 'contents' from {MEMORY_LIST_FILE} to contain each of "
        f"{list(REQUIRED_MARKERS)!r}; missing markers: {missing!r}. "
        f"Combined contents: {combined!r}"
    )


def test_output_log_records_memory_list_ok_with_run_id():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set in the verifier environment "
        "to validate per-run identifiers."
    )
    assert os.path.isfile(LOG_FILE), (
        f"Expected the task log file to exist at {LOG_FILE} after the task completes."
    )
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(r"^Memory list OK: count=(\d+) user_id=(\S+)$", re.MULTILINE)
    match = pattern.search(log_content)
    assert match, (
        f"Expected {LOG_FILE} to contain a line matching "
        f"'Memory list OK: count=<count> user_id=<user_id>'. "
        f"Got log contents:\n{log_content!r}"
    )
    logged_count = int(match.group(1))
    logged_user_id = match.group(2)
    assert run_id in logged_user_id, (
        f"Expected the logged user_id ({logged_user_id!r}) to embed the ZEALT_RUN_ID "
        f"({run_id!r}) so that concurrent task runs do not collide."
    )
    data = _load_memory_list()
    assert logged_count == data.get("count"), (
        f"Expected logged count ({logged_count}) to match 'count' in {MEMORY_LIST_FILE} "
        f"({data.get('count')!r})."
    )
