import json
import os
import time

import pytest


ANSWER_FILE = "/workspace/syllabus_answers.json"

EXPECTED_QUESTIONS = {
    "When is the midterm?",
    "What textbook is required?",
    "What is the grading policy?",
}

EXPECTED_KEYWORDS = {
    "When is the midterm?": "october 15",
    "What textbook is required?": "stewart",
    "What is the grading policy?": "homework 30%",
}


@pytest.fixture(scope="session")
def answer_payload():
    assert os.path.isfile(ANSWER_FILE), (
        f"Expected output file {ANSWER_FILE} to exist after the task ran."
    )
    with open(ANSWER_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"{ANSWER_FILE} is not valid JSON: {exc}"
            ) from exc
    return data


@pytest.fixture(scope="session")
def run_id():
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID environment variable must be set during verification."
    return rid


def test_top_level_schema(answer_payload, run_id):
    assert isinstance(answer_payload, dict), (
        f"Top-level JSON in {ANSWER_FILE} must be an object, got {type(answer_payload).__name__}."
    )
    assert "run_id" in answer_payload, (
        f"Top-level JSON in {ANSWER_FILE} must contain a 'run_id' key."
    )
    assert "answers" in answer_payload, (
        f"Top-level JSON in {ANSWER_FILE} must contain an 'answers' key."
    )
    assert answer_payload["run_id"] == run_id, (
        f"Expected 'run_id' field to equal ZEALT_RUN_ID ({run_id}), "
        f"got {answer_payload['run_id']!r}."
    )


def test_answers_list_shape(answer_payload):
    answers = answer_payload["answers"]
    assert isinstance(answers, list), (
        f"'answers' field must be a list, got {type(answers).__name__}."
    )
    assert len(answers) == 3, (
        f"Expected exactly 3 answer entries, got {len(answers)}."
    )
    seen_questions = set()
    for entry in answers:
        assert isinstance(entry, dict), (
            f"Each entry of 'answers' must be an object, got {type(entry).__name__}."
        )
        assert "question" in entry and "snippet" in entry, (
            f"Each entry must contain 'question' and 'snippet' fields. Got keys: {list(entry.keys())}."
        )
        assert isinstance(entry["snippet"], str) and entry["snippet"].strip(), (
            f"Snippet for question {entry.get('question')!r} must be a non-empty string."
        )
        seen_questions.add(entry["question"])
    assert seen_questions == EXPECTED_QUESTIONS, (
        f"Expected questions {EXPECTED_QUESTIONS}, got {seen_questions}."
    )


def test_snippet_keywords(answer_payload):
    answers = answer_payload["answers"]
    by_question = {entry["question"]: entry["snippet"] for entry in answers}
    for question, keyword in EXPECTED_KEYWORDS.items():
        snippet = by_question.get(question, "")
        assert keyword in snippet.lower(), (
            f"Expected snippet for {question!r} to contain {keyword!r} (case-insensitive), "
            f"got: {snippet!r}."
        )


def test_documents_present_in_alchemyst(run_id):
    """Verify the ingestion side-effect actually reached the Alchemyst context engine."""
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set during verification."

    from alchemyst_ai import AlchemystAI

    client = AlchemystAI(api_key=api_key)

    # Allow a brief settle period for any final indexing.
    last_error = None
    contexts = []
    for _ in range(5):
        try:
            result = client.v1.context.search(
                query="Math 101 syllabus",
                similarity_threshold=0.3,
                scope="internal",
                metadata={"group_name": ["syllabus", "math101", run_id]},
            )
            contexts = getattr(result, "contexts", None) or []
            if len(contexts) >= 3:
                break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(3)

    if last_error and not contexts:
        raise AssertionError(
            f"Failed to query Alchemyst context engine: {last_error!r}"
        )
    assert len(contexts) >= 3, (
        f"Expected at least 3 indexed snippets in group "
        f"['syllabus', 'math101', {run_id!r}], got {len(contexts)}."
    )
