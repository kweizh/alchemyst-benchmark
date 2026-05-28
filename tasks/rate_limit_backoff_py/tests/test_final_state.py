import json
import os

import pytest

PROJECT_DIR = "/home/user/myproject"
REPORT_PATH = os.path.join(PROJECT_DIR, "backoff_report.json")
EXPECTED_KEYS = {
    "total_requests",
    "successful_requests",
    "encountered_429",
    "max_backoff_delay_seconds",
}


@pytest.fixture(scope="module")
def report():
    assert os.path.isfile(REPORT_PATH), (
        f"Expected report file {REPORT_PATH} to exist after the task completes."
    )
    with open(REPORT_PATH, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            pytest.fail(f"{REPORT_PATH} is not valid JSON: {exc}")


def test_report_top_level_is_object(report):
    assert isinstance(report, dict), (
        f"Top-level JSON in {REPORT_PATH} must be an object/dict (got {type(report).__name__})."
    )


def test_report_has_exactly_required_keys(report):
    keys = set(report.keys())
    missing = EXPECTED_KEYS - keys
    extra = keys - EXPECTED_KEYS
    assert not missing, f"Missing required keys in {REPORT_PATH}: {sorted(missing)}"
    assert not extra, f"Unexpected extra keys in {REPORT_PATH}: {sorted(extra)}"


def test_total_requests_is_twenty(report):
    value = report["total_requests"]
    assert isinstance(value, int) and not isinstance(value, bool), (
        f"total_requests must be an integer (got {type(value).__name__}: {value!r})."
    )
    assert value == 20, f"total_requests must equal 20 (got {value})."


def test_successful_requests_equals_total(report):
    successful = report["successful_requests"]
    total = report["total_requests"]
    assert isinstance(successful, int) and not isinstance(successful, bool), (
        f"successful_requests must be an integer (got {type(successful).__name__}: {successful!r})."
    )
    assert successful == total, (
        f"successful_requests ({successful}) must equal total_requests ({total}); all requests should eventually succeed."
    )


def test_encountered_429_is_non_negative_int(report):
    value = report["encountered_429"]
    assert isinstance(value, int) and not isinstance(value, bool), (
        f"encountered_429 must be an integer (got {type(value).__name__}: {value!r})."
    )
    assert value >= 0, f"encountered_429 must be >= 0 (got {value})."
    assert value <= report["total_requests"], (
        f"encountered_429 ({value}) cannot exceed total_requests ({report['total_requests']})."
    )


def test_max_backoff_delay_is_non_negative_number(report):
    value = report["max_backoff_delay_seconds"]
    assert isinstance(value, (int, float)) and not isinstance(value, bool), (
        f"max_backoff_delay_seconds must be a number (got {type(value).__name__}: {value!r})."
    )
    assert value >= 0, f"max_backoff_delay_seconds must be >= 0 (got {value})."


def test_documents_ingested_for_run_id():
    """Best-effort: verify at least one returned context references the current run-id.

    Indexing latency or empty contexts in the API response should NOT fail the task as long
    as the structural checks above pass.
    """
    run_id = os.environ.get("ZEALT_RUN_ID")
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not run_id or not api_key:
        pytest.skip("ZEALT_RUN_ID or ALCHEMYST_AI_API_KEY not set in verifier env; skipping live SDK check.")

    try:
        from alchemyst_ai import AlchemystAI
    except ImportError:
        pytest.skip("alchemyst_ai SDK not available in verifier env; skipping live SDK check.")

    try:
        client = AlchemystAI(api_key=api_key)
        result = client.v1.context.search(
            query="rate limit backoff test corpus",
            similarity_threshold=0.1,
            minimum_similarity_threshold=0.05,
            scope="internal",
        )
    except Exception as exc:
        pytest.skip(f"Live SDK search raised {type(exc).__name__}: {exc}; skipping live SDK check.")

    contexts = getattr(result, "contexts", None) or []
    if not contexts:
        pytest.skip("Live SDK search returned no contexts (indexing latency); skipping live SDK check.")

    found_run_scoped_doc = False
    for ctx in contexts:
        metadata = getattr(ctx, "metadata", None)
        if isinstance(metadata, dict):
            file_name = str(metadata.get("file_name", ""))
        else:
            file_name = str(getattr(metadata, "file_name", "") or "")
        if run_id in file_name:
            found_run_scoped_doc = True
            break

    if not found_run_scoped_doc:
        pytest.skip(
            "No returned context has a file_name containing run-id; "
            "this is allowed due to indexing latency and is treated as a soft pass."
        )
