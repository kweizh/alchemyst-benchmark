import json
import os
import time

import pytest
import requests

SUMMARY_FILE = "/workspace/summary.txt"
RUN_LOG_FILE = "/workspace/run.log"
ALCHEMYST_BASE_URL = "https://platform-backend.getalchemystai.com"


@pytest.fixture(scope="module")
def summary_text():
    assert os.path.isfile(SUMMARY_FILE), (
        f"Expected day-3 summary file at {SUMMARY_FILE}, but it was not found."
    )
    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    assert text.strip(), f"{SUMMARY_FILE} is empty."
    return text


@pytest.fixture(scope="module")
def run_log():
    assert os.path.isfile(RUN_LOG_FILE), (
        f"Expected run log file at {RUN_LOG_FILE}, but it was not found."
    )
    with open(RUN_LOG_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"{RUN_LOG_FILE} is not valid JSON: {exc}. Raw content: {raw[:500]!r}"
        )
    assert isinstance(data, dict), (
        f"Expected {RUN_LOG_FILE} to contain a JSON object, "
        f"got {type(data).__name__}."
    )
    return data


def test_summary_contains_order_number(summary_text):
    assert "12345" in summary_text, (
        "Expected the day-3 summary to mention the order number '12345', "
        f"but it did not. Got: {summary_text!r}"
    )


def test_summary_contains_shipping_carrier(summary_text):
    assert "shipping carrier" in summary_text, (
        "Expected the day-3 summary to mention 'shipping carrier' "
        f"(case-sensitive), but it did not. Got: {summary_text!r}"
    )


def test_run_log_has_required_fields(run_log):
    for key in (
        "runId",
        "userId",
        "sessionId",
        "day1Stored",
        "day2Stored",
        "memoriesFound",
        "summaryPath",
    ):
        assert key in run_log, (
            f"run.log is missing required top-level field {key!r}. "
            f"Found keys: {sorted(run_log.keys())}"
        )
    assert isinstance(run_log["runId"], str) and run_log["runId"], (
        "runId must be a non-empty string."
    )
    assert isinstance(run_log["userId"], str) and run_log["userId"], (
        "userId must be a non-empty string."
    )
    assert isinstance(run_log["sessionId"], str) and run_log["sessionId"], (
        "sessionId must be a non-empty string."
    )
    assert isinstance(run_log["summaryPath"], str) and run_log["summaryPath"], (
        "summaryPath must be a non-empty string."
    )
    assert bool(run_log["day1Stored"]), "day1Stored must be truthy."
    assert bool(run_log["day2Stored"]), "day2Stored must be truthy."
    assert isinstance(run_log["memoriesFound"], int), (
        f"memoriesFound must be an integer, got "
        f"{type(run_log['memoriesFound']).__name__}."
    )


def test_ids_include_zealt_run_id(run_log):
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for verification."
    assert run_id in run_log["userId"], (
        f"Expected userId={run_log['userId']!r} to include the ZEALT_RUN_ID "
        f"{run_id!r} as a substring for parallel-run isolation."
    )
    assert run_id in run_log["sessionId"], (
        f"Expected sessionId={run_log['sessionId']!r} to include the ZEALT_RUN_ID "
        f"{run_id!r} as a substring for parallel-run isolation."
    )


def test_session_id_uses_ticket_prefix(run_log):
    assert run_log["sessionId"].startswith("ticket-"), (
        f"Expected sessionId to start with 'ticket-', got {run_log['sessionId']!r}."
    )


def test_memories_found_at_least_two(run_log):
    assert run_log["memoriesFound"] >= 2, (
        "Expected the day-3 memory search to find at least 2 entries "
        "(day-1 customer message and day-2 support update). "
        f"Got memoriesFound={run_log['memoriesFound']!r}."
    )


def _post_with_retries(url, headers, payload, retries=3, delay=2):
    last = None
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            last = response
            if response.status_code == 200:
                return response
        except requests.RequestException as exc:
            last = exc
        time.sleep(delay)
    return last


def test_alchemyst_api_confirms_stored_memories(run_log):
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, (
        "ALCHEMYST_AI_API_KEY must be set to verify against the live Alchemyst API."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    found_order = False
    found_carrier = False

    for _ in range(3):
        response = requests.post(
            f"{ALCHEMYST_BASE_URL}/api/v1/context/search",
            json={
                "query": "order 12345 shipping carrier delay",
                "similarity_threshold": 0.5,
                "minimum_similarity_threshold": 0.3,
                "scope": "internal",
            },
            headers=headers,
            timeout=60,
        )
        assert response.status_code == 200, (
            "Alchemyst context search returned status "
            f"{response.status_code}: {response.text!r}"
        )
        body = response.json()
        contexts = body.get("contexts") or []
        for ctx in contexts:
            content = ctx.get("content") if isinstance(ctx, dict) else None
            if not isinstance(content, str):
                continue
            if "order #12345" in content:
                found_order = True
            if "shipping carrier delay" in content:
                found_carrier = True

        if found_order and found_carrier:
            return

        time.sleep(2)

    assert found_order, (
        "Live Alchemyst search did not return any context containing "
        "'order #12345' after 3 attempts."
    )
    assert found_carrier, (
        "Live Alchemyst search did not return any context containing "
        "'shipping carrier delay' after 3 attempts."
    )
