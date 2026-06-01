import json
import os
import re
import subprocess

import pytest
import requests


PROJECT_DIR = "/home/user/myproject"
DIST_ENTRY = os.path.join(PROJECT_DIR, "dist", "main.js")
API_BASE = "https://platform-backend.getalchemystai.com"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _api_key() -> str:
    key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert key, "ALCHEMYST_AI_API_KEY environment variable is not set."
    return key


def _user_id() -> str:
    return f"user-{_run_id()}"


def _session_a() -> str:
    return f"session_A-{_run_id()}"


def _session_b() -> str:
    return f"session_B-{_run_id()}"


def _run_cli(query: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", DIST_ENTRY, "--query", query],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=180,
        env=os.environ.copy(),
    )


def _contains_vegan_and_peanut(text: str) -> bool:
    lower = text.lower()
    return "vegan" in lower and "peanut" in lower


def _memory_search(user_id: str, session_id: str) -> dict:
    """Search Alchemyst memory directly via REST API.

    Tries a few common request shapes because the Alchemyst SDK normalizes
    payloads; we want to be resilient when calling the raw HTTP endpoint.
    """
    url = f"{API_BASE}/api/v1/context/memory/search"
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    last_error = None
    for payload in (
        {"userId": user_id, "sessionId": session_id},
        {"user_id": user_id, "session_id": session_id},
    ):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                try:
                    return resp.json()
                except ValueError:
                    last_error = f"Non-JSON response: {resp.text[:200]}"
                    continue
            last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except requests.RequestException as exc:
            last_error = str(exc)
    raise AssertionError(
        f"Failed to call Alchemyst memory search API for user={user_id}, "
        f"session={session_id}: {last_error}"
    )


def _extract_memory_contents(payload: dict) -> list:
    """Walk the response payload and collect every string that looks like memory content."""
    contents = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("content", "text", "message") and isinstance(value, str):
                    contents.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return contents


def test_dist_entry_exists():
    assert os.path.isfile(DIST_ENTRY), (
        f"Compiled CLI entry point {DIST_ENTRY} does not exist. "
        "Ensure the TypeScript sources were compiled to dist/ before verification."
    )


def test_first_run_recalls_preference():
    """First invocation: stores preference under session_A and recalls it under session_B."""
    result = _run_cli("What can I eat for dinner?")
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    assert result.returncode == 0, (
        f"CLI exited with non-zero status {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert _contains_vegan_and_peanut(result.stdout), (
        "Expected stdout from the first run to recall the stored preference and "
        "include both 'vegan' and 'peanut' (case-insensitive).\n"
        f"STDOUT was:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_second_run_is_idempotent_and_still_recalls():
    """Second invocation: CLI must still recall the preference, proving rerunnability."""
    result = _run_cli("Suggest a snack")
    assert result.returncode == 0, (
        f"Second CLI invocation exited with non-zero status {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert _contains_vegan_and_peanut(result.stdout), (
        "Expected stdout from the second run to still recall the stored preference and "
        "include both 'vegan' and 'peanut' (case-insensitive), proving idempotent recall.\n"
        f"STDOUT was:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_preference_stored_under_session_a():
    """Directly query the Alchemyst memory API to confirm session_A holds the preference."""
    payload = _memory_search(_user_id(), _session_a())
    contents = _extract_memory_contents(payload)
    assert contents, (
        f"Expected at least one memory entry under userId={_user_id()} "
        f"sessionId={_session_a()}, but got none. Raw payload: "
        f"{json.dumps(payload)[:500]}"
    )
    assert any(_contains_vegan_and_peanut(c) for c in contents), (
        "Expected at least one memory entry under session_A to mention both "
        "'vegan' and 'peanut'. Found contents: " + json.dumps(contents)[:1000]
    )


def test_cross_session_recall_for_same_user():
    """Confirm cross-session memory recall: same userId, different sessionId still recalls."""
    payload = _memory_search(_user_id(), _session_b())
    contents = _extract_memory_contents(payload)
    assert contents, (
        f"Expected at least one memory entry to be recalled under userId={_user_id()} "
        f"sessionId={_session_b()} (cross-session recall), but got none. "
        f"Raw payload: {json.dumps(payload)[:500]}"
    )
    assert any(_contains_vegan_and_peanut(c) for c in contents), (
        "Expected cross-session recall under session_B to surface a memory entry "
        "containing both 'vegan' and 'peanut'. Found contents: "
        + json.dumps(contents)[:1000]
    )
