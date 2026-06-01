import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
QUERY = "What is the user's dietary preference?"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID", "").strip()
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _user_id() -> str:
    return f"alice-{_run_id()}"


def _session_b() -> str:
    return f"session-b-{_run_id()}"


def _alchemyst_client():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable is not set."
    try:
        from alchemyst_ai import AlchemystAI  # type: ignore
    except ImportError as exc:  # pragma: no cover - import-time check
        pytest.fail(
            f"`alchemyst_ai` Python SDK is not importable in the verifier "
            f"environment: {exc}"
        )
    return AlchemystAI(api_key=api_key)


@pytest.fixture(scope="session", autouse=True)
def cleanup_memory_before_tests():
    """Best-effort cleanup of any leftover memory for this run's user."""
    client = _alchemyst_client()
    try:
        client.v1.context.memory.delete(user_id=_user_id())
    except Exception:
        # The user may not have any prior memory yet; ignore failures.
        pass
    yield


def _run_cli() -> subprocess.CompletedProcess:
    main_path = os.path.join(PROJECT_DIR, "main.py")
    assert os.path.isfile(main_path), (
        f"Expected the executor's CLI entrypoint at {main_path}, "
        "but the file does not exist."
    )
    return subprocess.run(
        [
            "python3",
            "main.py",
            "--user-id",
            _user_id(),
            "--session-id",
            _session_b(),
            "--query",
            QUERY,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=os.environ.copy(),
        timeout=180,
    )


def _assert_recall(stdout: str, context_label: str) -> None:
    assert re.search(r"vegan", stdout, re.IGNORECASE), (
        f"{context_label}: expected the CLI stdout to recall the user's "
        f"vegan preference, but 'vegan' was not found. Got stdout:\n{stdout}"
    )
    assert re.search(r"peanut", stdout, re.IGNORECASE), (
        f"{context_label}: expected the CLI stdout to recall the user's "
        f"peanut allergy, but 'peanut' was not found. Got stdout:\n{stdout}"
    )


def test_first_run_recalls_preference():
    """The CLI must store in Session A and recall from Session B on first run."""
    result = _run_cli()
    assert result.returncode == 0, (
        "First CLI run failed with non-zero exit code "
        f"{result.returncode}.\nSTDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    _assert_recall(result.stdout, context_label="First CLI run")


def test_memory_persisted_in_backend_cross_session():
    """Verify the memory exists on the Alchemyst backend for this user,
    independently of the executor's CLI, using the v0.10.0 Python SDK.
    """
    client = _alchemyst_client()

    user_id = _user_id()
    found_text_parts = []

    # Try the documented v0.10.0 retrieval surface: client.v1.context.search.
    try:
        result = client.v1.context.search(
            query="dietary preference vegan peanut allergy",
            similarity_threshold=0.9,
            minimum_similarity_threshold=0.1,
            scope="internal",
            metadata={"user_id": user_id},
        )
        contexts = getattr(result, "contexts", None) or []
        for ctx in contexts:
            content = getattr(ctx, "content", None)
            if content is None and isinstance(ctx, dict):
                content = ctx.get("content")
            if content:
                found_text_parts.append(str(content))
    except Exception:
        # Fall through to alternate retrieval surfaces below.
        pass

    # Fallback: try client.v1.context.search without metadata filter.
    if not (
        any("vegan" in t.lower() for t in found_text_parts)
        and any("peanut" in t.lower() for t in found_text_parts)
    ):
        try:
            result = client.v1.context.search(
                query=f"user {user_id} dietary preference vegan peanut",
                similarity_threshold=0.9,
                minimum_similarity_threshold=0.1,
                scope="internal",
            )
            contexts = getattr(result, "contexts", None) or []
            for ctx in contexts:
                content = getattr(ctx, "content", None)
                if content is None and isinstance(ctx, dict):
                    content = ctx.get("content")
                if content:
                    found_text_parts.append(str(content))
        except Exception:
            pass

    # Fallback: try client.v1.context.view.docs with user_id filter.
    if not (
        any("vegan" in t.lower() for t in found_text_parts)
        and any("peanut" in t.lower() for t in found_text_parts)
    ):
        try:
            view_result = client.v1.context.view.docs(user_id=user_id)
            # The response shape may vary; serialize defensively.
            try:
                import json
                serialized = json.dumps(
                    view_result,
                    default=lambda o: getattr(o, "__dict__", str(o)),
                )
            except Exception:
                serialized = str(view_result)
            found_text_parts.append(serialized)
        except Exception:
            pass

    combined = "\n".join(found_text_parts).lower()
    assert "vegan" in combined and "peanut" in combined, (
        "Expected the Alchemyst backend to contain a memory for user "
        f"'{user_id}' mentioning both 'vegan' and 'peanut', but the "
        "retrieved content via the v0.10.0 Python SDK retrieval surfaces did "
        f"not include both keywords. Retrieved content:\n{combined!r}"
    )


def test_rerun_is_idempotent_and_still_recalls():
    """Re-running the CLI must continue to succeed and still recall."""
    result = _run_cli()
    assert result.returncode == 0, (
        "Second CLI run failed with non-zero exit code "
        f"{result.returncode}.\nSTDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    _assert_recall(result.stdout, context_label="Second CLI run")
