import json
import os

import pytest

REPORT_PATH = "/workspace/threshold_report.json"
EXPECTED_QUERY = "What is the refund policy?"


@pytest.fixture(scope="module")
def report():
    assert os.path.isfile(REPORT_PATH), (
        f"Expected output report at {REPORT_PATH}, but it does not exist."
    )
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            pytest.fail(f"{REPORT_PATH} is not valid JSON: {exc}")
    assert isinstance(data, dict), f"{REPORT_PATH} must be a JSON object."
    return data


@pytest.fixture(scope="module")
def run_id():
    value = os.environ.get("ZEALT_RUN_ID")
    assert value, "ZEALT_RUN_ID environment variable must be set for verification."
    return value


def test_report_has_required_keys(report):
    for key in ("query", "threshold_0_5_count", "threshold_0_9_count", "run_id"):
        assert key in report, (
            f"Missing required key {key!r} in {REPORT_PATH}; found keys: {sorted(report.keys())}"
        )


def test_report_query_matches(report):
    assert report["query"] == EXPECTED_QUERY, (
        f"Expected 'query' to be {EXPECTED_QUERY!r}, got {report['query']!r}."
    )


def test_report_run_id_matches_env(report, run_id):
    assert report["run_id"] == run_id, (
        f"Expected 'run_id' in report to equal ZEALT_RUN_ID={run_id!r}, got {report['run_id']!r}."
    )


def test_report_counts_are_non_negative_integers(report):
    for key in ("threshold_0_5_count", "threshold_0_9_count"):
        value = report[key]
        assert isinstance(value, int) and not isinstance(value, bool), (
            f"Expected {key!r} to be an integer, got {type(value).__name__}: {value!r}."
        )
        assert value >= 0, f"Expected {key!r} to be >= 0, got {value!r}."


def test_threshold_05_recall_at_least_threshold_09(report):
    low = report["threshold_0_5_count"]
    high = report["threshold_0_9_count"]
    assert low >= high, (
        "Expected threshold_0_5_count >= threshold_0_9_count to demonstrate that "
        f"a lower similarity_threshold does not reduce recall, got 0.5={low} < 0.9={high}."
    )


def test_documents_were_actually_ingested_into_alchemyst(run_id):
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set to verify against the real Alchemyst API."

    from alchemyst_ai import AlchemystAI

    client = AlchemystAI(api_key=api_key)
    result = client.v1.context.search(
        query="refund policy money-back guarantee",
        similarity_threshold=0.3,
        scope="internal",
    )
    contexts = getattr(result, "contexts", None) or []
    assert len(contexts) > 0, (
        "Expected the real Alchemyst context store to contain ingested documents related "
        f"to the refund policy for run_id={run_id!r}, but the search returned no contexts. "
        "This indicates the task did not actually call the Alchemyst API."
    )
