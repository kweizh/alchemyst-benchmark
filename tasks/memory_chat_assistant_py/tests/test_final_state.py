import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
MAIN_PY = os.path.join(PROJECT_DIR, "main.py")
TURNS_FILE = os.path.join(PROJECT_DIR, "turns.json")
TRANSCRIPT_FILE = os.path.join(PROJECT_DIR, "transcript.json")

TURNS = [
    "Hi! My name is Maya and I'm a software engineer in Berlin.",
    "By the way, I'm vegan and I have a serious peanut allergy.",
    "Cool — what hobbies do you think I might enjoy on weekends?",
    "Now, can you suggest a quick weeknight dinner I could cook tonight? "
    "Please address me by name and make sure the dish fits my dietary situation.",
]


@pytest.fixture(scope="session")
def run_id():
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID environment variable must be set for verification."
    return rid


@pytest.fixture(scope="session")
def ids(run_id):
    return {
        "user_id": f"harbor-user-{run_id}",
        "session_id": f"harbor-session-{run_id}",
    }


@pytest.fixture(scope="session", autouse=True)
def setup_and_run(ids):
    """Setup turns.json, clean prior transcript, and run the CLI once for the session."""
    assert os.path.isfile(MAIN_PY), f"Expected entrypoint not found at {MAIN_PY}"

    # Clean prior transcript per the Setup section in truth.
    if os.path.exists(TRANSCRIPT_FILE):
        os.remove(TRANSCRIPT_FILE)

    # Write turns.json from the verification plan.
    with open(TURNS_FILE, "w") as f:
        json.dump(TURNS, f)

    # Run the CLI end-to-end. Capture stdout for later assertions.
    result = subprocess.run(
        [
            "python3",
            "main.py",
            "--turns",
            "turns.json",
            "--user-id",
            ids["user_id"],
            "--session-id",
            ids["session_id"],
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    yield result


# ---------------------------------------------------------------------------
# Verification Step 1 — Static source check on main.py
# ---------------------------------------------------------------------------


def test_main_py_uses_correct_alchemyst_apis():
    with open(MAIN_PY, "r") as f:
        src = f.read()

    assert re.search(r"\balchemyst_ai\b", src), (
        "main.py does not appear to import the alchemyst_ai Python SDK."
    )
    assert "client.v1.context.search(" in src or re.search(
        r"\.v1\.context\.search\(", src
    ), (
        "main.py must use client.v1.context.search(...) for memory retrieval "
        "(the v0.10.0 Python SDK does NOT expose memory.search)."
    )
    assert "client.v1.context.memory.add(" in src or re.search(
        r"\.v1\.context\.memory\.add\(", src
    ), "main.py must use client.v1.context.memory.add(...) to persist memories."
    assert "memory.search(" not in src, (
        "main.py must NOT call memory.search(...) — this API does not exist in "
        "alchemystai v0.10.0 and would raise AttributeError at runtime."
    )


# ---------------------------------------------------------------------------
# Verification Step 2 — End-to-end CLI run
# ---------------------------------------------------------------------------


def test_cli_exit_code(setup_and_run):
    result = setup_and_run
    assert result.returncode == 0, (
        f"CLI exited with non-zero code {result.returncode}. "
        f"stdout=\n{result.stdout}\nstderr=\n{result.stderr}"
    )


def test_cli_stdout_has_one_assistant_line_per_turn(setup_and_run):
    result = setup_and_run
    pattern = re.compile(r"^ASSISTANT\[(\d+)\]: .+$", re.MULTILINE)
    matches = pattern.findall(result.stdout)
    assert len(matches) >= len(TURNS), (
        f"Expected at least {len(TURNS)} ASSISTANT[i] lines in stdout, "
        f"got {len(matches)}. stdout=\n{result.stdout}"
    )
    indices = sorted({int(m) for m in matches})
    for i in range(len(TURNS)):
        assert i in indices, (
            f"Missing ASSISTANT[{i}] line in stdout. stdout=\n{result.stdout}"
        )


# ---------------------------------------------------------------------------
# Verification Step 3 — transcript.json
# ---------------------------------------------------------------------------


def test_transcript_file_exists():
    assert os.path.isfile(TRANSCRIPT_FILE), (
        f"Expected transcript file at {TRANSCRIPT_FILE}; was it written by the CLI?"
    )


def test_transcript_structure():
    with open(TRANSCRIPT_FILE, "r") as f:
        transcript = json.load(f)

    assert isinstance(transcript, list), "transcript.json must be a JSON array."
    assert len(transcript) == len(TURNS), (
        f"transcript.json should have {len(TURNS)} entries, got {len(transcript)}."
    )
    for i, entry in enumerate(transcript):
        assert isinstance(entry, dict), f"Entry {i} is not a JSON object."
        assert entry.get("turn") == i, (
            f"Entry {i} has wrong/missing 'turn' field: {entry.get('turn')!r}"
        )
        assert entry.get("user") == TURNS[i], (
            f"Entry {i} user field does not match input turn. "
            f"got={entry.get('user')!r}, expected={TURNS[i]!r}"
        )
        assistant_text = entry.get("assistant")
        assert isinstance(assistant_text, str) and assistant_text.strip(), (
            f"Entry {i} 'assistant' must be a non-empty string."
        )


# ---------------------------------------------------------------------------
# Verification Step 4 — Memory recall behavior on the final turn
# ---------------------------------------------------------------------------


def test_final_assistant_reply_references_earlier_facts():
    with open(TRANSCRIPT_FILE, "r") as f:
        transcript = json.load(f)
    final_reply = transcript[-1]["assistant"].lower()

    assert "maya" in final_reply, (
        "Final assistant reply does not reference the user's name 'Maya'. "
        "This indicates the assistant did not retrieve the memory stored in "
        f"turn 0. Final reply was: {transcript[-1]['assistant']!r}"
    )

    references_diet = ("vegan" in final_reply) or ("peanut" in final_reply)
    assert references_diet, (
        "Final assistant reply does not reference the user's dietary situation "
        "(expected 'vegan' or 'peanut'). The assistant likely failed to retrieve "
        "the memory stored in turn 1. Final reply was: "
        f"{transcript[-1]['assistant']!r}"
    )


# ---------------------------------------------------------------------------
# Verification Step 5 — Memory was actually written to the real Alchemyst backend
# ---------------------------------------------------------------------------


def test_memory_persisted_to_alchemyst_backend(ids):
    """Independently confirm memory.add really wrote to the live Alchemyst service
    by performing a server-side semantic search and looking for 'Maya'.
    """
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set for backend verification."

    try:
        from alchemyst_ai import AlchemystAI
    except ImportError as e:
        pytest.fail(f"Cannot import alchemyst_ai SDK in verifier env: {e}")

    client = AlchemystAI(api_key=api_key)

    # v0.10.0 has NO memory.search — verify via context.search.
    response = client.v1.context.search(
        query="Maya vegan peanut",
        scope="internal",
        similarity_threshold=0.1,
    )

    # Be tolerant of either attribute access or dict access return shapes.
    contexts = getattr(response, "contexts", None)
    if contexts is None and isinstance(response, dict):
        contexts = response.get("contexts")

    assert contexts, (
        "client.v1.context.search returned no contexts. The CLI's memory.add "
        "calls do not appear to have actually persisted data to Alchemyst."
    )

    joined = ""
    for ctx in contexts:
        content = (
            getattr(ctx, "content", None)
            or (ctx.get("content") if isinstance(ctx, dict) else None)
            or ""
        )
        joined += "\n" + str(content)

    assert "maya" in joined.lower(), (
        "Searched Alchemyst memory does not contain the name 'Maya'. "
        "Either memory.add was not called with the conversation content, or "
        "it was called without the run-id-scoped user/session ids. "
        f"Joined contexts: {joined[:500]!r}"
    )
