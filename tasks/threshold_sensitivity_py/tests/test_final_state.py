import json
import os
import subprocess
import sys
import time

import pytest

PROJECT_DIR = "/home/user/myproject"
QUERY = "What is our company refund policy?"


def _run_cli(thresholds):
    """Run the CLI with the given thresholds and return the parsed JSON stdout."""
    cmd = [sys.executable, "main.py", "--thresholds", *[str(t) for t in thresholds]]
    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
        env=os.environ.copy(),
    )
    assert result.returncode == 0, (
        f"`{' '.join(cmd)}` exited with code {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    stdout = result.stdout.strip()
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as e:
        pytest.fail(
            "CLI stdout is not valid JSON. The CLI must print a single JSON object "
            f"mapping threshold strings to recall counts.\nstdout was:\n{stdout}\n"
            f"stderr was:\n{result.stderr}\nJSON error: {e}"
        )
    assert isinstance(payload, dict), (
        f"CLI stdout must be a JSON object (dict), got {type(payload).__name__}: {payload}"
    )
    return payload


def _format_threshold(t):
    return f"{float(t):.1f}"


def test_single_threshold_sanity():
    """The CLI must return a JSON object with one numeric entry for one threshold."""
    payload = _run_cli([0.5])
    key = _format_threshold(0.5)
    assert key in payload, (
        f"Expected key {key!r} in CLI output, got keys: {sorted(payload.keys())}"
    )
    value = payload[key]
    assert isinstance(value, int) and value >= 0, (
        f"Recall count for {key!r} must be a non-negative integer, got: {value!r}"
    )
    assert value >= 1, (
        f"With a relaxed threshold of 0.5 and an on-topic corpus about refund policies, "
        f"the CLI should return at least 1 recalled chunk, got: {value}"
    )


def test_monotonic_three_threshold_sweep():
    """The canonical probe: recall must be monotonically non-increasing with threshold."""
    payload = _run_cli([0.5, 0.7, 0.9])
    expected_keys = {_format_threshold(t) for t in (0.5, 0.7, 0.9)}
    assert expected_keys.issubset(payload.keys()), (
        f"Expected keys {sorted(expected_keys)} in CLI output, got: {sorted(payload.keys())}"
    )
    n_low = payload[_format_threshold(0.5)]
    n_mid = payload[_format_threshold(0.7)]
    n_high = payload[_format_threshold(0.9)]
    for label, n in (("0.5", n_low), ("0.7", n_mid), ("0.9", n_high)):
        assert isinstance(n, int) and n >= 0, (
            f"Recall count for threshold {label!r} must be a non-negative integer, got: {n!r}"
        )
    assert n_low >= n_mid >= n_high, (
        "Recall must be monotonically non-increasing as similarity_threshold increases. "
        f"Got counts: 0.5={n_low}, 0.7={n_mid}, 0.9={n_high}."
    )


def test_out_of_order_thresholds_still_monotonic():
    """Order of --thresholds should not change the monotonic invariant when sorted."""
    payload = _run_cli([0.9, 0.5, 0.7])
    expected_keys = {_format_threshold(t) for t in (0.9, 0.5, 0.7)}
    assert expected_keys.issubset(payload.keys()), (
        f"Expected keys {sorted(expected_keys)} in CLI output, got: {sorted(payload.keys())}"
    )
    n_low = payload[_format_threshold(0.5)]
    n_mid = payload[_format_threshold(0.7)]
    n_high = payload[_format_threshold(0.9)]
    for label, n in (("0.5", n_low), ("0.7", n_mid), ("0.9", n_high)):
        assert isinstance(n, int) and n >= 0, (
            f"Recall count for threshold {label!r} must be a non-negative integer, got: {n!r}"
        )
    assert n_low >= n_mid >= n_high, (
        "Even when thresholds are passed out of order, after sorting ascending the "
        "recall counts must satisfy count(0.5) >= count(0.7) >= count(0.9). "
        f"Got: 0.5={n_low}, 0.7={n_mid}, 0.9={n_high}."
    )


def test_real_ingestion_isolated_by_run_id():
    """Verify the CLI actually ingested documents into Alchemyst under the run-scoped namespace."""
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID must be set in the verifier environment."
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set in the verifier environment."

    # Make sure the CLI has been run at least once so documents exist for this run id.
    _run_cli([0.5, 0.7, 0.9])

    # Allow a brief moment for any final indexing to settle before querying.
    time.sleep(2)

    from alchemyst_ai import AlchemystAI

    client = AlchemystAI(api_key=api_key)
    result = client.v1.context.search(
        query=QUERY,
        similarity_threshold=0.3,
        scope="internal",
    )
    contexts = getattr(result, "contexts", None) or []
    assert len(contexts) >= 1, (
        "Direct SDK search at a low threshold should return at least one chunk after the "
        f"CLI runs. Got 0 results. run_id={run_id!r}."
    )

    def _stringify(value):
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError):
            return str(value)

    haystacks = []
    for chunk in contexts:
        # Each chunk may be a pydantic model or a plain dict; serialize defensively.
        if hasattr(chunk, "model_dump"):
            haystacks.append(_stringify(chunk.model_dump()))
        elif isinstance(chunk, dict):
            haystacks.append(_stringify(chunk))
        else:
            haystacks.append(str(chunk))

    assert any(run_id in h for h in haystacks), (
        f"None of the {len(contexts)} returned chunks reference ZEALT_RUN_ID={run_id!r}. "
        "The CLI must scope ingested documents (e.g., metadata.file_name or group_name) "
        "with the run id so concurrent runs do not collide."
    )
