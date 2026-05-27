import os
import shutil
import subprocess
import time

import pytest
import requests


PROJECT_DIR = "/home/user/update_task"
ALCHEMYST_BASE_URL = "https://platform-backend.getalchemystai.com"
ORIGINAL_CONTENT = (
    "Onboarding Policy: Effective date: 2024-01-01. "
    "All new hires must complete onboarding within 30 days of their start date."
)


def _run_id():
    return os.environ.get("ZEALT_RUN_ID", "local")


def _file_name():
    return f"onboarding_v1-{_run_id()}.md"


def _source():
    return f"onboarding-docs-{_run_id()}"


def _headers():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session", autouse=True)
def preload_initial_document():
    """Pre-load the original (v1) onboarding policy document into Alchemyst AI.

    This fixture runs before any test in this module. It removes any
    pre-existing document under the run-scoped ``source`` (for retry
    safety), then ingests the original onboarding content. The content is
    intentionally distinct from the updated (v2) content that the agent
    is expected to ingest, so the final-state test can tell them apart.
    """
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        # Without an API key we cannot pre-load. Let the env-var test fail
        # with a clear message instead of crashing here.
        yield
        return

    run_id = _run_id()
    file_name = _file_name()
    source = _source()

    # Best-effort cleanup of any prior state for this run-id, so the
    # initial-state setup is idempotent across retries.
    try:
        requests.post(
            f"{ALCHEMYST_BASE_URL}/api/v1/context/delete",
            json={
                "source": source,
                "by_doc": True,
                "by_id": False,
                "organization_id": "",
            },
            headers=_headers(),
            timeout=60,
        )
    except Exception:
        pass
    time.sleep(2)

    # Ingest the original v1 document via the real Alchemyst REST API.
    add_response = requests.post(
        f"{ALCHEMYST_BASE_URL}/api/v1/context/add",
        json={
            "documents": [
                {
                    "content": ORIGINAL_CONTENT,
                    "metadata": {
                        "file_name": file_name,
                        "group_name": [run_id],
                    },
                }
            ],
            "source": source,
            "context_type": "resource",
            "scope": "internal",
        },
        headers=_headers(),
        timeout=120,
    )
    assert add_response.status_code in (200, 201), (
        f"Pre-loading the original onboarding document failed with status "
        f"{add_response.status_code}: {add_response.text}"
    )

    # Give the backend a moment to finish indexing the document.
    time.sleep(5)
    yield


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_node_version_is_20_or_higher():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Expected Node.js >= 20, got {version}."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_npx_binary_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_alchemyst_sdk_installed():
    sdk_path = os.path.join(PROJECT_DIR, "node_modules", "@alchemystai", "sdk")
    assert os.path.isdir(sdk_path), (
        f"@alchemystai/sdk is not installed at {sdk_path}. "
        "It must be pre-installed in the environment."
    )


def test_tsx_available():
    tsx_path = os.path.join(PROJECT_DIR, "node_modules", "tsx")
    assert os.path.isdir(tsx_path), (
        f"tsx is not installed at {tsx_path}. "
        "It must be pre-installed in the environment."
    )


def test_alchemyst_api_key_env_var_set():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set."
    )


def test_zealt_run_id_env_var_set():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable must be set."


def test_original_document_indexed():
    """The original (v1) onboarding policy must be retrievable via search."""
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY must be set to verify initial state."

    run_id = _run_id()
    last_contents: list[str] = []
    for _ in range(6):
        response = requests.post(
            f"{ALCHEMYST_BASE_URL}/api/v1/context/search",
            json={
                "query": "What is the onboarding effective date?",
                "similarity_threshold": 0.3,
                "scope": "internal",
                "metadata": {"groupName": [run_id]},
            },
            headers=_headers(),
            timeout=60,
        )
        if response.status_code == 200:
            body = response.json() or {}
            contexts = body.get("contexts") or []
            last_contents = [
                (ctx.get("content") or "") for ctx in contexts
                if isinstance(ctx, dict)
            ]
            if any("Effective date: 2024-01-01" in c for c in last_contents):
                return
        time.sleep(3)

    raise AssertionError(
        "Expected to find the original v1 onboarding document "
        "(containing 'Effective date: 2024-01-01') after pre-loading, "
        f"but search returned: {last_contents!r}"
    )
