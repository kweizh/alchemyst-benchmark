import json
import os

import pytest


RESULT_FILE = "/workspace/result.json"
EXPECTED_QUERY = "What does the v1 engineering service do?"


@pytest.fixture(scope="module")
def run_id():
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID environment variable is required for verification."
    return rid


@pytest.fixture(scope="module")
def api_key():
    key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert key, "ALCHEMYST_AI_API_KEY environment variable is required for verification."
    return key


@pytest.fixture(scope="module")
def alchemyst_client(api_key):
    from alchemyst_ai import AlchemystAI

    return AlchemystAI(api_key=api_key)


@pytest.fixture(scope="module")
def result_payload():
    assert os.path.isfile(RESULT_FILE), f"Expected result file {RESULT_FILE} to exist."
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        try:
            payload = json.load(f)
        except json.JSONDecodeError as exc:
            pytest.fail(f"{RESULT_FILE} is not valid JSON: {exc}")
    return payload


def test_result_file_has_expected_top_level_fields(result_payload, run_id):
    assert isinstance(result_payload, dict), "result.json root must be a JSON object."

    assert result_payload.get("query") == EXPECTED_QUERY, (
        f"Expected 'query' to be {EXPECTED_QUERY!r}, got {result_payload.get('query')!r}."
    )

    intersection_filter = result_payload.get("intersection_filter")
    assert isinstance(intersection_filter, list), (
        "intersection_filter must be a JSON array."
    )
    assert sorted(intersection_filter) == ["eng", "v1"], (
        f"Expected intersection_filter to be ['eng','v1'] (any order), "
        f"got {intersection_filter!r}."
    )

    assert result_payload.get("run_id") == run_id, (
        f"Expected run_id to equal ZEALT_RUN_ID {run_id!r}, "
        f"got {result_payload.get('run_id')!r}."
    )


def test_results_field_is_non_empty_list(result_payload):
    results = result_payload.get("results")
    assert isinstance(results, list), "'results' must be a list."
    assert len(results) > 0, "'results' must be non-empty (the intersection doc should match)."


def test_each_result_has_id_and_content(result_payload):
    for idx, item in enumerate(result_payload.get("results", [])):
        assert isinstance(item, dict), f"results[{idx}] must be a JSON object."
        rid = item.get("id")
        content = item.get("content")
        assert isinstance(rid, str) and rid, (
            f"results[{idx}].id must be a non-empty string."
        )
        assert isinstance(content, str), f"results[{idx}].content must be a string."


def test_results_only_contain_intersection_marker(result_payload, run_id):
    eng_v1_marker = f"MARKER_ENG_V1_{run_id}"
    eng_v2_marker = f"MARKER_ENG_V2_{run_id}"
    docs_v1_marker = f"MARKER_DOCS_V1_{run_id}"

    results = result_payload.get("results", [])
    combined = "\n".join(item.get("content", "") for item in results)

    assert eng_v1_marker in combined, (
        f"Expected at least one result to contain marker {eng_v1_marker!r}; "
        f"got contents: {combined!r}"
    )
    assert eng_v2_marker not in combined, (
        f"Result contents must NOT include the eng/v2 marker {eng_v2_marker!r}; "
        f"got: {combined!r}"
    )
    assert docs_v1_marker not in combined, (
        f"Result contents must NOT include the docs/v1 marker {docs_v1_marker!r}; "
        f"got: {combined!r}"
    )


def _collect_search_text(response):
    """Concatenate content from an Alchemyst search response."""
    contexts = getattr(response, "contexts", None)
    if contexts is None and hasattr(response, "to_dict"):
        contexts = response.to_dict().get("contexts") or []
    if contexts is None and hasattr(response, "model_dump"):
        contexts = response.model_dump().get("contexts") or []
    if contexts is None:
        contexts = []
    parts = []
    for ctx in contexts:
        if isinstance(ctx, dict):
            parts.append(ctx.get("content") or "")
        else:
            parts.append(getattr(ctx, "content", "") or "")
    return "\n".join(parts)


def test_backend_has_eng_v2_document(alchemyst_client, run_id):
    response = alchemyst_client.v1.context.search(
        query="What does the v2 engineering service do?",
        scope="internal",
        similarity_threshold=0.3,
        metadata={"group_name": ["eng", "v2"]},
    )
    text = _collect_search_text(response)
    eng_v2_marker = f"MARKER_ENG_V2_{run_id}"
    eng_v1_marker = f"MARKER_ENG_V1_{run_id}"
    assert eng_v2_marker in text, (
        f"Backend search for groups ['eng','v2'] should return content with {eng_v2_marker!r}; "
        f"got: {text!r}"
    )
    assert eng_v1_marker not in text, (
        f"Backend search for groups ['eng','v2'] must NOT return content with {eng_v1_marker!r}; "
        f"got: {text!r}"
    )


def test_backend_has_docs_v1_document(alchemyst_client, run_id):
    response = alchemyst_client.v1.context.search(
        query="documentation release notes v1",
        scope="internal",
        similarity_threshold=0.3,
        metadata={"group_name": ["docs", "v1"]},
    )
    text = _collect_search_text(response)
    docs_v1_marker = f"MARKER_DOCS_V1_{run_id}"
    eng_v1_marker = f"MARKER_ENG_V1_{run_id}"
    assert docs_v1_marker in text, (
        f"Backend search for groups ['docs','v1'] should return content with {docs_v1_marker!r}; "
        f"got: {text!r}"
    )
    assert eng_v1_marker not in text, (
        f"Backend search for groups ['docs','v1'] must NOT return content with {eng_v1_marker!r}; "
        f"got: {text!r}"
    )


def test_backend_intersection_search_returns_only_eng_v1(alchemyst_client, run_id):
    response = alchemyst_client.v1.context.search(
        query=EXPECTED_QUERY,
        scope="internal",
        similarity_threshold=0.3,
        metadata={"group_name": ["eng", "v1"]},
    )
    text = _collect_search_text(response)
    eng_v1_marker = f"MARKER_ENG_V1_{run_id}"
    eng_v2_marker = f"MARKER_ENG_V2_{run_id}"
    docs_v1_marker = f"MARKER_DOCS_V1_{run_id}"

    assert eng_v1_marker in text, (
        f"Backend intersection search must return content with {eng_v1_marker!r}; got: {text!r}"
    )
    assert eng_v2_marker not in text, (
        f"Backend intersection search must NOT return content with {eng_v2_marker!r}; got: {text!r}"
    )
    assert docs_v1_marker not in text, (
        f"Backend intersection search must NOT return content with {docs_v1_marker!r}; got: {text!r}"
    )
