import os
import re

import pytest
from alchemyst_ai import AlchemystAI

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
EXPECTED_CONTENT_SUBSTRING = "30-day money back guarantee"
SEARCH_QUERY = "What is the refund policy?"


def _get_run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set for verification; cannot "
        "compute the expected metadata.file_name without it."
    )
    return run_id


def _get_api_key() -> str:
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, (
        "ALCHEMYST_AI_API_KEY environment variable must be set so the verifier "
        "can query the Alchemyst context engine."
    )
    return api_key


def test_log_file_exists():
    assert os.path.isfile(LOG_FILE), (
        f"Expected the agent's script to write the top-match log to {LOG_FILE}, "
        "but the file does not exist."
    )


def test_log_file_contains_top_match_with_expected_excerpt():
    with open(LOG_FILE, "r", encoding="utf-8") as fh:
        log_text = fh.read()

    top_match_lines = [
        line for line in log_text.splitlines() if line.strip().startswith("Top Match:")
    ]
    assert top_match_lines, (
        f"Expected {LOG_FILE} to contain a line starting with 'Top Match:' that "
        f"includes the search result content, but no such line was found. "
        f"File contents:\n{log_text!r}"
    )

    has_expected_substring = any(
        EXPECTED_CONTENT_SUBSTRING in line for line in top_match_lines
    )
    assert has_expected_substring, (
        f"Expected at least one 'Top Match:' line in {LOG_FILE} to include the "
        f"substring {EXPECTED_CONTENT_SUBSTRING!r}, but none did. "
        f"Lines found: {top_match_lines!r}"
    )


def test_document_retrievable_via_context_search():
    run_id = _get_run_id()
    api_key = _get_api_key()
    expected_file_name = f"refund-policy-{run_id}.md"

    client = AlchemystAI(api_key=api_key)
    result = client.v1.context.search(
        query=SEARCH_QUERY,
        similarity_threshold=0.7,
        minimum_similarity_threshold=0.5,
        scope="internal",
        metadata=True,
    )

    contexts = getattr(result, "contexts", None) or []
    assert contexts, (
        "Expected `v1.context.search` to return at least one context after the "
        f"agent ingested the refund policy document, but `contexts` was empty. "
        f"Query: {SEARCH_QUERY!r}"
    )

    def _content_of(ctx):
        if hasattr(ctx, "content"):
            return ctx.content
        if isinstance(ctx, dict):
            return ctx.get("content", "")
        return ""

    def _metadata_of(ctx):
        if hasattr(ctx, "metadata"):
            return ctx.metadata
        if isinstance(ctx, dict):
            return ctx.get("metadata", {})
        return {}

    def _get_meta_field(meta, *keys):
        if meta is None:
            return None
        for key in keys:
            value = None
            if isinstance(meta, dict):
                value = meta.get(key)
            else:
                value = getattr(meta, key, None)
            if value:
                return value
        return None

    content_match_found = any(
        EXPECTED_CONTENT_SUBSTRING in _content_of(ctx) for ctx in contexts
    )
    assert content_match_found, (
        "Expected at least one search result to contain the substring "
        f"{EXPECTED_CONTENT_SUBSTRING!r} in its `content`, but none did. "
        "This indicates the refund policy document was not ingested into the "
        "Alchemyst context engine."
    )

    matching_filename_found = False
    for ctx in contexts:
        meta = _metadata_of(ctx)
        file_name = _get_meta_field(meta, "file_name", "fileName")
        if file_name == expected_file_name:
            matching_filename_found = True
            break

    assert matching_filename_found, (
        "Expected at least one search result to have "
        f"`metadata.file_name == {expected_file_name!r}` (i.e. the unique, "
        "run-id-suffixed file name the agent was instructed to use), but none "
        "matched. This indicates the agent either did not append ZEALT_RUN_ID "
        "to the metadata.file_name or did not ingest the document."
    )
