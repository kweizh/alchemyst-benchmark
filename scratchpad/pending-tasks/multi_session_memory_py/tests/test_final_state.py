import os
import re


WORKSPACE_DIR = "/workspace"
RECALLED_FILE = os.path.join(WORKSPACE_DIR, "recalled.txt")
LOG_FILE = os.path.join(WORKSPACE_DIR, "output.log")


def test_recalled_file_exists():
    assert os.path.isfile(RECALLED_FILE), (
        f"Expected the recalled-memory file to exist at {RECALLED_FILE} after the task completes."
    )


def test_recalled_file_non_empty():
    assert os.path.getsize(RECALLED_FILE) > 0, (
        f"Expected {RECALLED_FILE} to contain the recalled memory text, but the file is empty."
    )


def test_recalled_file_contains_vegan_preference():
    with open(RECALLED_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "vegan" in content.lower(), (
        f"Expected {RECALLED_FILE} to contain the cross-session preference 'vegan' "
        f"(case-insensitive); got contents:\n{content!r}"
    )


def test_output_log_exists():
    assert os.path.isfile(LOG_FILE), (
        f"Expected the task log file to exist at {LOG_FILE} after the task completes."
    )


def test_output_log_records_recall_ok_with_run_id():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set in the verifier environment "
        "to validate per-run identifiers."
    )
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log_content = f.read()
    pattern = re.compile(r"^Recall OK: user_id=(\S+)$", re.MULTILINE)
    match = pattern.search(log_content)
    assert match, (
        f"Expected {LOG_FILE} to contain a line matching 'Recall OK: user_id=<user_id>'. "
        f"Got log contents:\n{log_content!r}"
    )
    user_id = match.group(1)
    assert run_id in user_id, (
        f"Expected the logged user_id ({user_id!r}) to embed the ZEALT_RUN_ID ({run_id!r}) "
        "so that concurrent task runs do not collide."
    )
