import json
import os
import re
import subprocess

import pytest


PROJECT_DIR = "/home/user/myproject"
RESULT_LINE_RE = re.compile(r"^RESULT:\s*(\{.*\})\s*$")


def _run_id():
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID must be set in the verifier environment."
    return rid


def _file_name():
    return f"conflict-doc-{_run_id()}.md"


def _source():
    return f"conflict-handling-{_run_id()}"


def _alchemyst_client():
    from alchemyst_ai import AlchemystAI

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set in the verifier environment."
    return AlchemystAI(api_key=api_key)


def _delete_best_effort(client):
    """Best-effort cleanup of any docs ingested under this run-id's source."""
    try:
        client.v1.context.delete(source=_source(), by_doc=True)
    except Exception:
        pass


def _list_doc_file_names(client):
    """Return a list of file names visible to the API key, tolerant of response shape."""
    names = []
    candidates = (
        lambda c: c.v1.context.view.docs(),
        lambda c: c.v1.context.view.retrieve(),
    )
    for fn in candidates:
        try:
            result = fn(client)
        except Exception:
            continue
        docs = getattr(result, "documents", None)
        if docs is None and isinstance(result, dict):
            docs = result.get("documents")
        if docs is None:
            docs = getattr(result, "contexts", None)
            if docs is None and isinstance(result, dict):
                docs = result.get("contexts")
        if not docs:
            continue
        for doc in docs:
            name = None
            for key in ("file_name", "fileName"):
                name = getattr(doc, key, None)
                if name:
                    break
                if isinstance(doc, dict) and doc.get(key):
                    name = doc.get(key)
                    break
            if name is None:
                meta = getattr(doc, "metadata", None)
                if meta is None and isinstance(doc, dict):
                    meta = doc.get("metadata")
                if meta is not None:
                    for key in ("file_name", "fileName"):
                        if isinstance(meta, dict) and meta.get(key):
                            name = meta.get(key)
                            break
                        v = getattr(meta, key, None)
                        if v:
                            name = v
                            break
            if isinstance(name, str):
                names.append(name)
        if names:
            return names
    return names


def _parse_result_line(stdout: str):
    """Find the last `RESULT: {...}` line in stdout and parse it as JSON."""
    last_match = None
    for line in stdout.splitlines():
        m = RESULT_LINE_RE.match(line.strip())
        if m:
            last_match = m
    assert last_match is not None, (
        "Expected stdout to contain a final line of the form "
        "'RESULT: {\"status\": \"ok\", \"conflict_resolved\": <bool>}'. "
        f"Got stdout:\n{stdout}"
    )
    try:
        return json.loads(last_match.group(1))
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            f"Failed to JSON-decode RESULT payload {last_match.group(1)!r}: {exc!r}"
        )


def _run_cli():
    proc = subprocess.run(
        ["python3", "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=180,
    )
    return proc


@pytest.fixture(scope="module")
def alchemyst_client():
    return _alchemyst_client()


@pytest.fixture(scope="module", autouse=True)
def _preclean_and_teardown(alchemyst_client):
    # Remove any leftover document from a previous failed run for this run-id.
    _delete_best_effort(alchemyst_client)
    yield
    _delete_best_effort(alchemyst_client)


def test_main_py_exists():
    main_py = os.path.join(PROJECT_DIR, "main.py")
    assert os.path.isfile(main_py), f"Expected agent to create the CLI entrypoint at {main_py}."


def test_first_invocation_clean_add():
    proc = _run_cli()
    assert proc.returncode == 0, (
        f"First `python3 main.py` invocation exited with rc={proc.returncode}.\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    payload = _parse_result_line(proc.stdout)
    assert payload.get("status") == "ok", (
        f"Expected RESULT.status == 'ok' on first run; got payload={payload!r}"
    )
    assert payload.get("conflict_resolved") is False, (
        "Expected RESULT.conflict_resolved == false on the first (clean) run; "
        f"got payload={payload!r}"
    )


def test_second_invocation_handles_409_cleanly():
    proc = _run_cli()
    assert proc.returncode == 0, (
        f"Second `python3 main.py` invocation must succeed (rc=0); got rc={proc.returncode}.\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    payload = _parse_result_line(proc.stdout)
    assert payload.get("status") == "ok", (
        f"Expected RESULT.status == 'ok' on second run; got payload={payload!r}"
    )
    assert payload.get("conflict_resolved") is True, (
        "Expected RESULT.conflict_resolved == true on the second run "
        "(because the same file_name already exists, a 409 should be detected and resolved). "
        f"Got payload={payload!r}"
    )


def test_document_visible_on_alchemyst_after_runs(alchemyst_client):
    file_names = _list_doc_file_names(alchemyst_client)
    expected = _file_name()
    assert expected in file_names, (
        f"Expected to find a document with file_name=={expected!r} on the Alchemyst "
        f"side after both CLI runs. Observed file names: {file_names!r}"
    )
