import json
import os
import time

import pytest
from alchemyst_ai import AlchemystAI

RESULT_PATH = "/workspace/result.json"

TOPIC_QUERIES = {
    "refund": "What is your refund policy?",
    "shipping": "How long does shipping take?",
    "account": "How do I create an account?",
    "password": "How do I reset my password?",
    "support": "How can I contact customer support?",
}


@pytest.fixture(scope="module")
def run_id():
    value = os.environ.get("ZEALT_RUN_ID")
    assert value, "ZEALT_RUN_ID environment variable is not set."
    return value


@pytest.fixture(scope="module")
def result_data():
    assert os.path.isfile(RESULT_PATH), f"Expected result file at {RESULT_PATH} but it was not found."
    with open(RESULT_PATH, "r") as f:
        text = f.read()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        pytest.fail(f"{RESULT_PATH} is not valid JSON: {exc}")
    return data


@pytest.fixture(scope="module")
def alchemyst_client():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable is required for verification."
    return AlchemystAI(api_key=api_key)


def test_result_uploaded_count(result_data):
    assert result_data.get("uploaded") == 5, (
        f"Expected 'uploaded' to be 5, got {result_data.get('uploaded')!r}."
    )


def test_result_retrievable_count(result_data):
    assert result_data.get("retrievable") == 5, (
        f"Expected 'retrievable' to be 5, got {result_data.get('retrievable')!r}."
    )


def test_result_run_id_matches(result_data, run_id):
    assert result_data.get("run_id") == run_id, (
        f"Expected 'run_id' to be {run_id!r}, got {result_data.get('run_id')!r}."
    )


def test_result_file_names_shape(result_data, run_id):
    file_names = result_data.get("file_names")
    assert isinstance(file_names, list), "'file_names' must be a list."
    assert len(file_names) == 5, f"Expected 5 file_names, got {len(file_names)}."
    assert len(set(file_names)) == 5, f"Expected 5 unique file_names, got duplicates in {file_names!r}."
    for name in file_names:
        assert isinstance(name, str) and name, f"Each file_name must be a non-empty string, got {name!r}."
        assert run_id in name, (
            f"Expected ZEALT_RUN_ID ({run_id!r}) to be embedded in file_name {name!r}."
        )


def _search_with_retry(client, query, max_attempts=5, delay_seconds=3):
    last_error = None
    for attempt in range(max_attempts):
        try:
            return client.v1.context.search(
                query=query,
                similarity_threshold=0.5,
                scope="internal",
            )
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(delay_seconds)
    raise AssertionError(f"context.search failed after {max_attempts} attempts: {last_error}")


def _file_name_from_context(ctx):
    metadata = getattr(ctx, "metadata", None)
    if metadata is None and isinstance(ctx, dict):
        metadata = ctx.get("metadata")
    if metadata is None:
        return None
    if isinstance(metadata, dict):
        return metadata.get("file_name")
    return getattr(metadata, "file_name", None)


def test_all_documents_retrievable_via_search(result_data, alchemyst_client):
    file_names = result_data.get("file_names") or []
    assert len(file_names) == 5, "Expected 5 file_names to verify retrievability against."

    # Match each declared file_name to a known topic so we can issue a topic-specific query.
    unmatched = []
    for fname in file_names:
        topic = next((t for t in TOPIC_QUERIES if t in fname.lower()), None)
        if topic is None:
            unmatched.append(fname)
    assert not unmatched, (
        "Each file_name must contain one of the recognized topic keywords "
        f"({sorted(TOPIC_QUERIES)}). Unmatched: {unmatched!r}"
    )

    # Give the backend a moment to finish indexing in case the task just completed.
    time.sleep(5)

    not_retrievable = []
    for fname in file_names:
        topic = next(t for t in TOPIC_QUERIES if t in fname.lower())
        query = TOPIC_QUERIES[topic]

        response = _search_with_retry(alchemyst_client, query)
        contexts = getattr(response, "contexts", None)
        if contexts is None and isinstance(response, dict):
            contexts = response.get("contexts")
        contexts = contexts or []

        found = any(_file_name_from_context(ctx) == fname for ctx in contexts)
        if not found:
            not_retrievable.append(fname)

    assert not not_retrievable, (
        f"The following uploaded documents were not retrievable via context.search: {not_retrievable!r}"
    )
