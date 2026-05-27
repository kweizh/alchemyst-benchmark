import os

ANSWER_FILE = "/workspace/answer.txt"


def test_answer_file_exists():
    assert os.path.isfile(ANSWER_FILE), (
        f"Expected output file {ANSWER_FILE} does not exist after running the task."
    )


def test_answer_file_non_empty():
    size = os.path.getsize(ANSWER_FILE)
    assert size > 0, f"Output file {ANSWER_FILE} is empty (size={size})."


def test_answer_file_contains_svelte():
    with open(ANSWER_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    lowered = content.lower()
    assert "svelte" in lowered, (
        "Expected the Session B response written to /workspace/answer.txt to mention "
        "'svelte' (the favorite framework recalled from Alchemyst cross-session memory). "
        f"Got: {content!r}"
    )


def test_answer_file_is_non_trivial():
    with open(ANSWER_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert len(content) >= 5, (
        f"Output file {ANSWER_FILE} content is too short to be a real LLM response: {content!r}"
    )
    assert content.lower() not in ("undefined", "null", "none"), (
        f"Output file {ANSWER_FILE} content looks like a sentinel/placeholder, not an LLM response: {content!r}"
    )
