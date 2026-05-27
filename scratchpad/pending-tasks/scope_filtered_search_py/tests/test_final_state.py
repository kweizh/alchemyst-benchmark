import json
import os

import pytest


RESULT_FILE = "/workspace/scope_report.json"


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


def test_top_level_fields_shape(result_payload, run_id):
    assert isinstance(result_payload, dict), "scope_report.json root must be a JSON object."

    query = result_payload.get("query")
    assert isinstance(query, str) and query.strip(), (
        f"'query' must be a non-empty string, got {query!r}."
    )

    assert result_payload.get("run_id") == run_id, (
        f"Expected run_id to equal ZEALT_RUN_ID {run_id!r}, "
        f"got {result_payload.get('run_id')!r}."
    )

    for scope_name in ("internal", "external"):
        section = result_payload.get(scope_name)
        assert isinstance(section, dict), (
            f"'{scope_name}' must be a JSON object with 'count' and 'results'."
        )
        assert "count" in section, f"'{scope_name}.count' is required."
        assert "results" in section, f"'{scope_name}.results' is required."
        assert isinstance(section["count"], int), (
            f"'{scope_name}.count' must be an integer, got {type(section['count']).__name__}."
        )
        assert isinstance(section["results"], list), (
            f"'{scope_name}.results' must be a list."
        )


def test_counts_match_results_length(result_payload):
    for scope_name in ("internal", "external"):
        section = result_payload[scope_name]
        assert section["count"] == len(section["results"]), (
            f"'{scope_name}.count' ({section['count']}) must equal "
            f"len({scope_name}.results) ({len(section['results'])})."
        )


def test_results_are_non_empty(result_payload):
    for scope_name in ("internal", "external"):
        section = result_payload[scope_name]
        assert len(section["results"]) > 0, (
            f"'{scope_name}.results' must be non-empty (the {scope_name}-scope "
            f"documents should match the query)."
        )


def test_each_result_has_id_and_content(result_payload):
    for scope_name in ("internal", "external"):
        for idx, item in enumerate(result_payload[scope_name]["results"]):
            assert isinstance(item, dict), (
                f"{scope_name}.results[{idx}] must be a JSON object."
            )
            rid = item.get("id")
            content = item.get("content")
            assert isinstance(rid, str) and rid, (
                f"{scope_name}.results[{idx}].id must be a non-empty string."
            )
            assert isinstance(content, str), (
                f"{scope_name}.results[{idx}].content must be a string."
            )


def test_internal_results_only_contain_internal_marker(result_payload, run_id):
    internal_marker = f"MARKER_INTERNAL_{run_id}"
    external_marker = f"MARKER_EXTERNAL_{run_id}"

    for idx, item in enumerate(result_payload["internal"]["results"]):
        content = item.get("content", "")
        assert internal_marker in content, (
            f"internal.results[{idx}].content must contain marker {internal_marker!r}; "
            f"got: {content!r}"
        )
        assert external_marker not in content, (
            f"internal.results[{idx}].content must NOT contain marker {external_marker!r}; "
            f"got: {content!r}"
        )


def test_external_results_only_contain_external_marker(result_payload, run_id):
    internal_marker = f"MARKER_INTERNAL_{run_id}"
    external_marker = f"MARKER_EXTERNAL_{run_id}"

    for idx, item in enumerate(result_payload["external"]["results"]):
        content = item.get("content", "")
        assert external_marker in content, (
            f"external.results[{idx}].content must contain marker {external_marker!r}; "
            f"got: {content!r}"
        )
        assert internal_marker not in content, (
            f"external.results[{idx}].content must NOT contain marker {internal_marker!r}; "
            f"got: {content!r}"
        )


def test_backend_internal_scope_search(alchemyst_client, result_payload, run_id):
    query = result_payload["query"]
    response = alchemyst_client.v1.context.search(
        query=query,
        scope="internal",
        similarity_threshold=0.3,
    )
    text = _collect_search_text(response)
    internal_marker = f"MARKER_INTERNAL_{run_id}"
    external_marker = f"MARKER_EXTERNAL_{run_id}"
    assert internal_marker in text, (
        f"Backend internal-scope search must return content with {internal_marker!r}; "
        f"got: {text!r}"
    )
    assert external_marker not in text, (
        f"Backend internal-scope search must NOT return content with {external_marker!r}; "
        f"got: {text!r}"
    )


def test_backend_external_scope_search(alchemyst_client, result_payload, run_id):
    query = result_payload["query"]
    response = alchemyst_client.v1.context.search(
        query=query,
        scope="external",
        similarity_threshold=0.3,
    )
    text = _collect_search_text(response)
    internal_marker = f"MARKER_INTERNAL_{run_id}"
    external_marker = f"MARKER_EXTERNAL_{run_id}"
    assert external_marker in text, (
        f"Backend external-scope search must return content with {external_marker!r}; "
        f"got: {text!r}"
    )
    assert internal_marker not in text, (
        f"Backend external-scope search must NOT return content with {internal_marker!r}; "
        f"got: {text!r}"
    )
