import os
import shutil
import time

import pytest


PROJECT_DIR = "/home/user/myproject"
ORIGINAL_CONTENT = (
    "Refund Policy v1: We offer a 7-day refund window. "
    "To request a refund, contact refunds@example.com."
)


def _client():
    from alchemyst_ai import AlchemystAI

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    return AlchemystAI(api_key=api_key)


def _source():
    run_id = os.environ.get("ZEALT_RUN_ID", "local")
    return f"policy-docs-{run_id}"


@pytest.fixture(scope="session", autouse=True)
def preload_initial_document():
    """Pre-load the original (v1) policy document into Alchemyst AI.

    This fixture runs before any test in this module. It removes any
    pre-existing document under the run-scoped ``source`` (for retry
    safety), then ingests the original policy content. The content is
    intentionally distinct from the updated (v2) content that the agent
    is expected to ingest, so the final-state test can tell them apart.
    """
    client = _client()
    source = _source()

    # Best-effort cleanup of any prior state for this run-id, so the
    # initial-state setup is idempotent across retries.
    try:
        client.v1.context.delete(
            organization_id="",
            source=source,
            by_doc=True,
            by_id=False,
        )
    except Exception:
        pass
    time.sleep(2)

    client.v1.context.add(
        documents=[
            {
                "content": ORIGINAL_CONTENT,
                "metadata": {"file_name": "policy_v1.md"},
            }
        ],
        source=source,
        context_type="resource",
        scope="internal",
        metadata={"file_name": "policy_v1.md"},
    )
    # Give the backend a moment to finish indexing the document.
    time.sleep(5)
    yield


def test_alchemyst_ai_sdk_importable():
    import alchemyst_ai  # noqa: F401


def test_python_version():
    import sys

    assert sys.version_info >= (3, 11), (
        f"Python 3.11+ is required, got {sys.version_info}"
    )


def test_pip_available():
    assert shutil.which("pip") is not None or shutil.which("pip3") is not None, (
        "pip must be available in PATH for installing additional dependencies."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_required_env_vars_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."
    )
    assert os.environ.get("ZEALT_RUN_ID"), (
        "ZEALT_RUN_ID environment variable must be set in the task environment."
    )


def test_original_document_indexed():
    """The original (v1) document must be retrievable via semantic search."""
    client = _client()
    last_contents = []
    for _ in range(6):
        result = client.v1.context.search(
            query="What is the refund policy?",
            similarity_threshold=0.7,
            minimum_similarity_threshold=0.3,
            scope="internal",
        )
        contexts = getattr(result, "contexts", None) or []
        last_contents = [getattr(c, "content", "") or "" for c in contexts]
        if any("7-day" in c for c in last_contents):
            return
        time.sleep(3)
    raise AssertionError(
        "Expected to find the original v1 policy document (containing '7-day') "
        f"after pre-loading, but search returned: {last_contents!r}"
    )
