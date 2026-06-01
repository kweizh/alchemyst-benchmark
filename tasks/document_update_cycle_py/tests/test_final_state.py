import os
import subprocess
import time

import pytest

PROJECT_DIR = "/home/user/myproject"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _file_name(run_id: str) -> str:
    return f"policy-{run_id}.md"


def _make_client():
    from alchemyst_ai import AlchemystAI

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable is not set."
    return AlchemystAI(api_key=api_key)


def _safe_delete(client, file_name: str) -> None:
    """Attempt to delete the document by file_name. Ignore not-found errors."""
    try:
        client.v1.context.delete(
            source=file_name,
            by_doc=True,
            organization_id=None,
        )
    except Exception:
        # Fallback: try minimal delete signature variants.
        try:
            client.v1.context.delete(source=file_name, by_doc=True)
        except Exception:
            try:
                client.v1.context.delete(source=file_name)
            except Exception:
                pass


@pytest.fixture(scope="session", autouse=True)
def pre_clean():
    """Pre-clean: remove any existing document with this run-id's file_name."""
    client = _make_client()
    file_name = _file_name(_run_id())
    _safe_delete(client, file_name)
    # Brief pause to let the delete propagate before the CLI runs.
    time.sleep(2)
    yield
    # Final cleanup after all tests run.
    _safe_delete(client, file_name)


@pytest.fixture(scope="session")
def cli_run():
    """Run the CLI once and capture stdout for stdout-based checks."""
    result = subprocess.run(
        ["python3", "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=300,
    )
    return result


def test_cli_exits_zero(cli_run):
    assert cli_run.returncode == 0, (
        f"`python3 main.py` exited with code {cli_run.returncode}.\n"
        f"STDOUT:\n{cli_run.stdout}\nSTDERR:\n{cli_run.stderr}"
    )


def test_stdout_contains_added_v1(cli_run):
    assert "Added v1" in cli_run.stdout, (
        f"Expected stdout to contain 'Added v1'. Stdout was:\n{cli_run.stdout}"
    )


def test_stdout_contains_409(cli_run):
    assert "409" in cli_run.stdout, (
        f"Expected stdout to contain '409' (Conflict observed). Stdout was:\n{cli_run.stdout}"
    )


def test_stdout_contains_deleted(cli_run):
    assert "Deleted" in cli_run.stdout, (
        f"Expected stdout to contain 'Deleted'. Stdout was:\n{cli_run.stdout}"
    )


def test_stdout_contains_added_v2(cli_run):
    assert "Added v2" in cli_run.stdout, (
        f"Expected stdout to contain 'Added v2'. Stdout was:\n{cli_run.stdout}"
    )


def test_stdout_contains_v2_keyword(cli_run):
    assert "60-day" in cli_run.stdout, (
        f"Expected stdout to contain '60-day' (v2 content). Stdout was:\n{cli_run.stdout}"
    )


def test_stdout_marker_ordering(cli_run):
    """The required substrings must appear in the documented order."""
    stdout = cli_run.stdout
    markers = ["Added v1", "409", "Deleted", "Added v2", "60-day"]
    positions = []
    for m in markers:
        idx = stdout.find(m)
        assert idx != -1, (
            f"Marker '{m}' not found in stdout. Stdout was:\n{stdout}"
        )
        positions.append(idx)
    assert positions == sorted(positions), (
        f"Markers appeared out of order. Positions: {dict(zip(markers, positions))}.\n"
        f"Stdout was:\n{stdout}"
    )


def test_stdout_no_stale_v1_content(cli_run):
    """The final search step output must not surface the old 30-day v1 policy."""
    stdout = cli_run.stdout
    added_v2_idx = stdout.find("Added v2")
    assert added_v2_idx != -1, "Marker 'Added v2' not found in stdout."
    post_v2 = stdout[added_v2_idx:]
    assert "30-day" not in post_v2, (
        "Stdout after 'Added v2' contained '30-day' — v1 content should not be surfaced after the update.\n"
        f"Stdout was:\n{stdout}"
    )


def test_live_service_search_returns_v2(cli_run):
    """After the CLI runs, the live service must return the v2 content for a refund query."""
    client = _make_client()
    file_name = _file_name(_run_id())

    # Poll because indexing may be near-real-time but not synchronous.
    deadline = time.time() + 60
    last_contexts = []
    while time.time() < deadline:
        result = client.v1.context.search(
            query="What is the refund policy?",
            similarity_threshold=0.5,
            scope="internal",
        )
        contexts = getattr(result, "contexts", None) or []
        last_contexts = contexts
        joined = " ".join(
            (getattr(c, "content", None) or (c.get("content") if isinstance(c, dict) else "")) or ""
            for c in contexts
        )
        if "60-day" in joined:
            break
        time.sleep(3)

    joined = " ".join(
        (getattr(c, "content", None) or (c.get("content") if isinstance(c, dict) else "")) or ""
        for c in last_contexts
    )
    assert "60-day" in joined, (
        f"Live search did not return v2 (`60-day`) content within timeout. Got: {joined!r}"
    )

    # For this run-id's document, the content must not contain the stale v1 marker.
    for c in last_contexts:
        content = (
            getattr(c, "content", None)
            or (c.get("content") if isinstance(c, dict) else "")
            or ""
        )
        metadata = (
            getattr(c, "metadata", None)
            or (c.get("metadata") if isinstance(c, dict) else None)
            or {}
        )
        meta_file_name = None
        if isinstance(metadata, dict):
            meta_file_name = metadata.get("file_name")
        else:
            meta_file_name = getattr(metadata, "file_name", None)
        if meta_file_name == file_name:
            assert "30-day" not in content, (
                f"Live search returned stale v1 content for {file_name}: {content!r}"
            )


def test_cli_is_rerunnable():
    """A second invocation of the CLI must also succeed and emit the same markers."""
    result = subprocess.run(
        ["python3", "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=300,
    )
    assert result.returncode == 0, (
        f"Second `python3 main.py` exited with code {result.returncode}.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    for marker in ["Added v1", "409", "Deleted", "Added v2", "60-day"]:
        assert marker in result.stdout, (
            f"Second run stdout missing marker '{marker}'. Stdout was:\n{result.stdout}"
        )
