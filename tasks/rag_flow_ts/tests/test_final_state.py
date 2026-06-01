import os
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "run.log")


@pytest.fixture(scope="module")
def cli_run():
    """Run the CLI once with a refund-related question and capture stdout."""
    # Clean up any previous log file.
    if os.path.isfile(LOG_FILE):
        os.remove(LOG_FILE)

    env = os.environ.copy()
    # Sanity: required env vars must be present in the test environment.
    assert env.get("ALCHEMYST_AI_API_KEY", "").strip() != "", (
        "ALCHEMYST_AI_API_KEY must be set in the verifier environment."
    )
    assert env.get("ZEALT_RUN_ID", "").strip() != "", (
        "ZEALT_RUN_ID must be set in the verifier environment."
    )

    result = subprocess.run(
        [
            "npm",
            "start",
            "--silent",
            "--",
            "--question",
            "What is your refund policy?",
        ],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    # Persist stdout for debugging and later assertions.
    with open(LOG_FILE, "w") as f:
        f.write(result.stdout)

    return result


def test_cli_exits_successfully(cli_run):
    assert cli_run.returncode == 0, (
        f"CLI exited with status {cli_run.returncode}. "
        f"stdout=\n{cli_run.stdout}\nstderr=\n{cli_run.stderr}"
    )


def test_cli_stdout_contains_refund_chunk(cli_run):
    stdout = cli_run.stdout or ""
    assert "30-day" in stdout, (
        "Expected stdout to include the refund chunk substring '30-day' "
        "(indicating that the ingested refund-policy document was retrieved "
        f"via context.search). Got stdout:\n{stdout}"
    )


def test_document_ingested_with_run_id_file_name():
    """
    Use the real Alchemyst API via the Python SDK to confirm that the document
    ingested by the CLI is present in the user's context store and that its
    metadata.file_name uses the ZEALT_RUN_ID suffix.
    """
    run_id = os.environ.get("ZEALT_RUN_ID", "").strip()
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY", "").strip()
    assert run_id, "ZEALT_RUN_ID must be set in the verifier environment."
    assert api_key, "ALCHEMYST_AI_API_KEY must be set in the verifier environment."

    expected_file_name = f"refunds-{run_id}.md"

    from alchemyst_ai import AlchemystAI

    client = AlchemystAI(api_key=api_key)

    result = client.v1.context.search(
        query="refund policy 30-day money back guarantee",
        similarity_threshold=0.5,
        scope="internal",
    )

    contexts = getattr(result, "contexts", None) or []
    assert len(contexts) > 0, (
        "Expected at least one context returned by Alchemyst search for the "
        "refund-policy query, but got none. The CLI may have failed to ingest "
        "the document."
    )

    def _file_name_of(ctx):
        # Be tolerant of both attribute-style and dict-style SDK responses.
        metadata = getattr(ctx, "metadata", None)
        if metadata is None and isinstance(ctx, dict):
            metadata = ctx.get("metadata")
        if metadata is None:
            return None
        if isinstance(metadata, dict):
            return metadata.get("file_name") or metadata.get("fileName")
        return getattr(metadata, "file_name", None) or getattr(
            metadata, "fileName", None
        )

    file_names = [_file_name_of(c) for c in contexts]
    assert expected_file_name in file_names, (
        f"Expected to find a context document with file_name "
        f"'{expected_file_name}' in Alchemyst, but got file_names={file_names}."
    )
