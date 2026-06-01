import os
import subprocess
import time

import pytest


PROJECT_DIR = "/home/user/update-task"
DIST_MAIN = os.path.join(PROJECT_DIR, "dist", "main.js")

NEW_MARKER = "30-day"
OLD_MARKER = "14-day"
SEARCH_QUERY = "What is the refund policy?"


def _run_id() -> str:
    rid = (os.environ.get("ZEALT_RUN_ID") or "").strip()
    assert rid, "ZEALT_RUN_ID is required for verification but is unset."
    return rid


def _scoped_file_name(rid: str) -> str:
    return f"policy-{rid}.md"


def _client():
    from alchemyst_ai import AlchemystAI

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY is required to run the verifier."
    return AlchemystAI(api_key=api_key)


def _best_effort_delete(client, file_name: str) -> None:
    """Best-effort cleanup of any document with the given run-scoped file_name.

    Tries a few likely Python SDK delete signatures; ignores all errors.
    """
    candidates = [
        lambda: client.v1.context.delete(
            source="documentation", by_doc=True, by_id=False,
            metadata={"file_name": file_name},
        ),
        lambda: client.v1.context.delete(metadata={"file_name": file_name}),
        lambda: client.v1.context.delete(metadata={"fileName": file_name}),
    ]
    for call in candidates:
        try:
            call()
            return
        except Exception:
            continue


def _ensure_node_modules():
    node_modules = os.path.join(PROJECT_DIR, "node_modules")
    if not os.path.isdir(node_modules):
        install = subprocess.run(
            ["npm", "install"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=600,
        )
        assert install.returncode == 0, (
            f"`npm install` failed (rc={install.returncode}).\n"
            f"STDOUT:\n{install.stdout}\nSTDERR:\n{install.stderr}"
        )


def _ensure_built():
    if not os.path.isfile(DIST_MAIN):
        build = subprocess.run(
            ["npm", "run", "build"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert build.returncode == 0, (
            f"`npm run build` failed (rc={build.returncode}).\n"
            f"STDOUT:\n{build.stdout}\nSTDERR:\n{build.stderr}"
        )
    assert os.path.isfile(DIST_MAIN), (
        f"Expected built entrypoint at {DIST_MAIN} after `npm run build`."
    )


def _run_cli() -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "dist/main.js"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ},
    )


def _last_non_empty_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        if line.strip():
            return line
    return ""


@pytest.fixture(scope="session")
def env_ready():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist after the agent's work."
    )
    _ensure_node_modules()
    _ensure_built()

    rid = _run_id()
    client = _client()
    fname = _scoped_file_name(rid)

    # Best-effort pre-clean before tests.
    _best_effort_delete(client, fname)

    yield {"run_id": rid, "client": client, "file_name": fname}

    # Best-effort teardown.
    _best_effort_delete(client, fname)


def test_dist_main_present(env_ready):
    assert os.path.isfile(DIST_MAIN), (
        f"Expected built entrypoint at {DIST_MAIN} after `npm run build`."
    )


def test_cli_first_run_completes_update_cycle(env_ready):
    result = _run_cli()
    assert result.returncode == 0, (
        f"`node dist/main.js` failed (exit {result.returncode}).\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    last = _last_non_empty_line(result.stdout)
    assert NEW_MARKER in last, (
        f"Expected updated-content marker {NEW_MARKER!r} in the final stdout "
        f"line, got: {last!r}\nFull stdout:\n{result.stdout}"
    )
    assert OLD_MARKER not in last, (
        f"Old-content marker {OLD_MARKER!r} must NOT appear in the final "
        f"stdout line after the update cycle, got: {last!r}"
    )

    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    assert "409" in combined, (
        "Expected the CLI to observe a 409 Conflict on the duplicate-add step "
        "and surface it in stdout/stderr (e.g. log a message containing '409'). "
        f"Combined output did not mention 409.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_cli_is_rerunnable(env_ready):
    # Allow indexing to settle from the previous test.
    time.sleep(3)
    result = _run_cli()
    assert result.returncode == 0, (
        f"Second `node dist/main.js` invocation failed (exit {result.returncode}). "
        f"The CLI must be safely rerunnable.\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    last = _last_non_empty_line(result.stdout)
    assert NEW_MARKER in last, (
        f"Expected {NEW_MARKER!r} in the final stdout line on the second run, "
        f"got: {last!r}\nFull stdout:\n{result.stdout}"
    )
    assert OLD_MARKER not in last, (
        f"Old-content marker {OLD_MARKER!r} must NOT appear on the second run, "
        f"got: {last!r}"
    )


def test_v2_searchable_via_python_sdk(env_ready):
    client = env_ready["client"]
    fname = env_ready["file_name"]

    last_contexts = []
    last_err = None
    for _ in range(5):
        try:
            result = client.v1.context.search(
                query=SEARCH_QUERY,
                similarity_threshold=0.5,
                scope="internal",
            )
            contexts = getattr(result, "contexts", None) or []
            last_contexts = contexts
            # Look for chunks belonging to this run's file_name.
            mine = []
            for ctx in contexts:
                meta = getattr(ctx, "metadata", None) or {}
                # metadata can be dict-like or attr-like
                file_name = None
                if isinstance(meta, dict):
                    file_name = meta.get("file_name") or meta.get("fileName")
                else:
                    file_name = getattr(meta, "file_name", None) or getattr(meta, "fileName", None)
                if file_name == fname:
                    mine.append(ctx)
            if mine:
                has_new = any(NEW_MARKER in (getattr(c, "content", "") or "") for c in mine)
                has_old = any(OLD_MARKER in (getattr(c, "content", "") or "") for c in mine)
                if has_new and not has_old:
                    return
            # Fallback: if metadata isn't surfaced, accept any chunk that
            # clearly contains the v2 marker.
            new_anywhere = any(NEW_MARKER in (getattr(c, "content", "") or "") for c in contexts)
            old_anywhere = any(OLD_MARKER in (getattr(c, "content", "") or "") for c in contexts)
            if new_anywhere and not old_anywhere:
                return
        except Exception as e:
            last_err = e
        time.sleep(3)

    snippet = [getattr(c, "content", "") for c in last_contexts][:5]
    raise AssertionError(
        "Independent Python-SDK search did not confirm v2 indexing for "
        f"file_name={env_ready['file_name']!r}. Expected at least one returned "
        f"context whose content contains {NEW_MARKER!r} and none containing "
        f"{OLD_MARKER!r}.\n"
        f"Last error: {last_err!r}\nLast contexts (truncated): {snippet!r}"
    )
