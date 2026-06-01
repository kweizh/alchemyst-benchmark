import os
import re
import subprocess
import textwrap
import time

import pytest

PROJECT_DIR = "/home/user/syllabai"
SYLLABUS_PATH = os.path.join(PROJECT_DIR, "syllabus.md")
MAIN_PY = os.path.join(PROJECT_DIR, "main.py")


SYLLABUS_CONTENT = textwrap.dedent(
    """\
    # CS204 — Introduction to Distributed Systems (Fall 2025)

    ## Instructor
    Professor Ada Lovelace. Office hours: Tuesdays 3:00 PM in Babbage Hall room 207.

    ## Schedule
    - The midterm exam will be held on October 17, 2025 in Babbage Hall room 101.
    - The final exam will be held on December 12, 2025.

    ## Grading
    - Homework: 40%
    - Midterm: 25%
    - Final exam: 35%

    ## Textbook
    The required textbook is "Designing Data-Intensive Applications" by Martin Kleppmann.

    ## Late Policy
    Late homework loses 10 percentage points per day, up to a maximum of 3 days late.
    """
)


def _run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "").strip()
    assert rid, "ZEALT_RUN_ID environment variable must be set."
    return rid


def _course_id() -> str:
    return f"course-{_run_id()}"


def _unrelated_course_id() -> str:
    return f"unrelated-{_run_id()}"


def _run_main(args, timeout=180):
    cmd = ["python3", MAIN_PY, *args]
    return subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ.copy(),
    )


def _extract_answer(stdout: str) -> str:
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("answer:"):
            return stripped[len("answer:") :].strip()
    raise AssertionError(
        f"No line starting with 'Answer:' was found in stdout:\n{stdout}"
    )


@pytest.fixture(scope="session", autouse=True)
def prepare_syllabus_file():
    os.makedirs(PROJECT_DIR, exist_ok=True)
    with open(SYLLABUS_PATH, "w", encoding="utf-8") as f:
        f.write(SYLLABUS_CONTENT)
    # Clean any leftover output files from previous runs.
    for fname in ("ask_midterm.out", "ask_late.out", "ask_other.out"):
        p = os.path.join(PROJECT_DIR, fname)
        if os.path.exists(p):
            os.remove(p)
    yield


def test_main_py_exists():
    assert os.path.isfile(MAIN_PY), (
        f"Expected CLI entrypoint at {MAIN_PY}; the executor must create main.py."
    )


def test_ingest_command_succeeds():
    course_id = _course_id()
    result = _run_main(["ingest", "syllabus.md", "--course-id", course_id])
    assert result.returncode == 0, (
        "Expected `python3 main.py ingest ...` to exit 0, but got "
        f"returncode={result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    expected = f"Ingested syllabus for course: {course_id}"
    assert expected in result.stdout, (
        f"Expected stdout to contain '{expected}'. Got:\n{result.stdout}"
    )
    # Give the context engine a moment to index.
    time.sleep(5)


def test_alchemyst_context_contains_syllabus_chunk():
    """Use the Alchemyst Python SDK to verify the syllabus is retrievable
    when filtered by the course-scoped group_name."""
    try:
        from alchemyst_ai import AlchemystAI
    except Exception as exc:  # pragma: no cover - diagnostic
        pytest.fail(f"Failed to import alchemyst_ai SDK: {exc!r}")

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set for verification."

    client = AlchemystAI(api_key=api_key)
    course_id = _course_id()

    result = client.v1.context.search(
        query="When is the midterm exam?",
        similarity_threshold=0.3,
        scope="internal",
        metadata={"group_name": ["syllabus", course_id]},
    )

    contexts = getattr(result, "contexts", None) or []
    # Some SDK versions may return a dict-like object; handle that too.
    if not contexts and isinstance(result, dict):
        contexts = result.get("contexts", []) or []

    assert contexts, (
        "Expected at least one context chunk returned from Alchemyst for the "
        f"course-scoped query (group_name=['syllabus', '{course_id}']). "
        "The ingest step may not have stored the syllabus with the correct metadata."
    )

    joined = "\n".join(
        (getattr(c, "content", None) or (c.get("content") if isinstance(c, dict) else "") or "")
        for c in contexts
    )
    assert ("October 17" in joined) or ("Babbage Hall room 101" in joined), (
        "Expected at least one retrieved chunk to contain 'October 17' or "
        f"'Babbage Hall room 101'. Got chunks:\n{joined}"
    )


def test_ask_midterm_question():
    course_id = _course_id()
    result = _run_main(
        ["ask", "When is the midterm exam and where will it be held?", "--course-id", course_id]
    )
    assert result.returncode == 0, (
        "Expected `python3 main.py ask ...` (midterm) to exit 0, but got "
        f"returncode={result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    answer = _extract_answer(result.stdout)
    lower = answer.lower()
    assert "october 17" in lower, (
        f"Expected midterm answer to mention 'October 17'. Got: {answer!r}"
    )
    assert "babbage hall" in lower, (
        f"Expected midterm answer to mention 'Babbage Hall'. Got: {answer!r}"
    )


def test_ask_late_policy_question():
    course_id = _course_id()
    result = _run_main(
        ["ask", "What is the late policy for homework?", "--course-id", course_id]
    )
    assert result.returncode == 0, (
        "Expected `python3 main.py ask ...` (late policy) to exit 0, but got "
        f"returncode={result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    answer = _extract_answer(result.stdout)
    # Look for the numeric facts: "10" (percentage points) and "3" (max days).
    assert re.search(r"\b10\b", answer), (
        f"Expected late-policy answer to include the number 10 (percentage points per day). Got: {answer!r}"
    )
    assert re.search(r"\b3\b", answer), (
        f"Expected late-policy answer to include the number 3 (maximum days late). Got: {answer!r}"
    )


def test_ask_isolated_course_does_not_leak_midterm():
    """Context Arithmetic: a different course_id must not retrieve this course's syllabus."""
    other_course = _unrelated_course_id()
    result = _run_main(
        ["ask", "When is the midterm exam?", "--course-id", other_course]
    )
    assert result.returncode == 0, (
        "Expected `python3 main.py ask ...` (unrelated course) to exit 0, but got "
        f"returncode={result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    answer = _extract_answer(result.stdout)
    assert "october 17" not in answer.lower(), (
        "Course-isolation failure: an unrelated course_id retrieved this course's "
        f"midterm date. The metadata filter is not scoping results correctly. Got: {answer!r}"
    )
