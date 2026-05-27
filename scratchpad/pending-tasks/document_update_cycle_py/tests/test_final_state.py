import os
import re
import time

import pytest


LOG_PATH = "/home/user/myproject/output.log"


def _client():
    from alchemyst_ai import AlchemystAI

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    return AlchemystAI(api_key=api_key)


def _search_contents():
    """Run a relevant semantic search and return the list of returned content strings."""
    client = _client()
    result = client.v1.context.search(
        query="What is the refund policy?",
        similarity_threshold=0.7,
        minimum_similarity_threshold=0.3,
        scope="internal",
    )
    contexts = getattr(result, "contexts", None) or []
    return [getattr(c, "content", "") or "" for c in contexts]


def test_log_file_records_success():
    """The agent must have written `Update status: success` to the log file."""
    assert os.path.isfile(LOG_PATH), (
        f"Expected log file {LOG_PATH} to exist after the task is completed."
    )
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert re.search(r"^\s*Update status:\s*success\s*$", content, re.MULTILINE), (
        f"Expected a line matching 'Update status: success' in {LOG_PATH}, "
        f"got:\n{content!r}"
    )


def test_new_policy_is_retrievable_and_old_is_gone():
    """After the agent runs, the v2 document must be retrievable and v1 must be gone."""
    last_contents = []
    found_new = False
    for _ in range(5):
        last_contents = _search_contents()
        if any("90-day" in c for c in last_contents):
            found_new = True
            break
        time.sleep(3)

    assert found_new, (
        "Expected at least one returned context to contain the new policy phrase "
        f"'90-day' after the agent's update, but search returned: {last_contents!r}"
    )

    # The old policy content (7-day) must no longer be present in any returned chunk.
    stale_chunks = [c for c in last_contents if "7-day" in c]
    assert not stale_chunks, (
        "Expected no returned context to contain the old policy phrase '7-day' "
        f"after the agent's update, but found: {stale_chunks!r}"
    )
