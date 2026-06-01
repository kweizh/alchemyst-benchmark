import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
MAIN_PY = os.path.join(PROJECT_DIR, "main.py")
NOTES_FILE = "notes/refunds.md"


def _run(args, timeout=180):
    env = os.environ.copy()
    return subprocess.run(
        ["python3", "main.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )


def test_cli_entrypoint_exists():
    """The executor must have created the CLI entrypoint at main.py."""
    assert os.path.isfile(MAIN_PY), (
        f"Expected the executor to create a CLI entrypoint at {MAIN_PY}."
    )


def test_ingest_then_ask_returns_grounded_answer():
    """
    Verification Step 1: Run `ingest` then `ask`, and confirm OpenAI's
    answer references the 30-day refund period taken from the ingested
    document.
    """
    ingest = _run(["ingest", NOTES_FILE])
    assert ingest.returncode == 0, (
        f"`python3 main.py ingest {NOTES_FILE}` exited with rc={ingest.returncode}.\n"
        f"stdout:\n{ingest.stdout}\nstderr:\n{ingest.stderr}"
    )

    ask = _run(["ask", "What is the refund period?"])
    assert ask.returncode == 0, (
        f"`python3 main.py ask ...` exited with rc={ask.returncode}.\n"
        f"stdout:\n{ask.stdout}\nstderr:\n{ask.stderr}"
    )
    combined = (ask.stdout or "") + "\n" + (ask.stderr or "")
    # The OpenAI answer must reference the 30-day window drawn from the
    # ingested context.
    assert re.search(r"30[\s-]*days?", combined, re.IGNORECASE), (
        "Expected the OpenAI answer to reference a '30 day' / '30-day' refund "
        "period drawn from the ingested context, but it was not found in the "
        f"CLI output.\nstdout:\n{ask.stdout}\nstderr:\n{ask.stderr}"
    )


def test_ingest_is_idempotent():
    """
    Verification Step 2: Re-running `ingest` on the same file must not
    crash on a 409 Conflict. The CLI should be re-runnable.
    """
    second = _run(["ingest", NOTES_FILE])
    assert second.returncode == 0, (
        "Second invocation of `ingest` must not crash with an uncaught 409 "
        "Conflict. The CLI must be idempotent (use ZEALT_RUN_ID, "
        "delete-then-add, or handle the conflict).\n"
        f"stdout:\n{second.stdout}\nstderr:\n{second.stderr}"
    )


def test_document_persisted_to_alchemyst_backend():
    """
    Verification Step 3: Independently confirm via the Python SDK that the
    document content was actually persisted to the live Alchemyst service.
    """
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set for backend verification."

    try:
        from alchemyst_ai import AlchemystAI
    except ImportError as exc:  # noqa: BLE001
        pytest.fail(f"Cannot import alchemyst_ai SDK in verifier env: {exc}")

    client = AlchemystAI(api_key=api_key)
    try:
        response = client.v1.context.search(
            query="refund period",
            scope="internal",
            similarity_threshold=0.3,
        )
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"client.v1.context.search raised an exception: {exc!r}")

    contexts = getattr(response, "contexts", None)
    if contexts is None and isinstance(response, dict):
        contexts = response.get("contexts")
    assert contexts, (
        "client.v1.context.search returned no contexts. The CLI's `ingest` "
        "subcommand does not appear to have persisted data to Alchemyst."
    )

    joined_lower = ""
    for ctx in contexts:
        content = getattr(ctx, "content", None)
        if content is None and isinstance(ctx, dict):
            content = ctx.get("content")
        if isinstance(content, str):
            joined_lower += "\n" + content.lower()

    assert "30-day" in joined_lower or "30 day" in joined_lower, (
        "Searched Alchemyst context does not contain the '30-day' phrase from "
        "the ingested refunds.md. Either `ingest` did not persist the file "
        "contents, or it was scoped differently than `scope=\"internal\"`. "
        f"Joined contexts (first 500 chars): {joined_lower[:500]!r}"
    )


def test_main_py_reads_env_vars_and_does_not_hardcode_keys():
    """
    Verification Step 4: Static check that the CLI source references the
    expected environment variables and does not embed the runtime secrets.
    """
    with open(MAIN_PY, "r", encoding="utf-8", errors="ignore") as fh:
        source = fh.read()

    assert "ALCHEMYST_AI_API_KEY" in source, (
        "main.py should reference the ALCHEMYST_AI_API_KEY environment variable name."
    )
    assert "OPENAI_API_KEY" in source, (
        "main.py should reference the OPENAI_API_KEY environment variable name."
    )
    assert "ZEALT_RUN_ID" in source, (
        "main.py should reference the ZEALT_RUN_ID environment variable to "
        "namespace the ingested file_name metadata."
    )

    alch_runtime = os.environ.get("ALCHEMYST_AI_API_KEY", "")
    if alch_runtime:
        assert alch_runtime not in source, (
            "The runtime ALCHEMYST_AI_API_KEY value appears to be hardcoded in "
            "main.py. Read it from the environment variable instead."
        )
    openai_runtime = os.environ.get("OPENAI_API_KEY", "")
    if openai_runtime:
        assert openai_runtime not in source, (
            "The runtime OPENAI_API_KEY value appears to be hardcoded in "
            "main.py. Read it from the environment variable instead."
        )


def test_main_py_imports_openai():
    """
    Verification Step 5: Static check that main.py invokes the real OpenAI
    SDK rather than mocking the chat completion.
    """
    with open(MAIN_PY, "r", encoding="utf-8", errors="ignore") as fh:
        source = fh.read()
    assert re.search(r"^\s*(from\s+openai|import\s+openai)\b", source, re.MULTILINE), (
        "main.py must import the `openai` package (e.g. `from openai import OpenAI` "
        "or `import openai`) so the `ask` subcommand goes through a real OpenAI call."
    )
