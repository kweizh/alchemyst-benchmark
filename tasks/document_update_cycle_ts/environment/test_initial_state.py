import os
import shutil
import subprocess


HOME_DIR = "/home/user"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_npx_binary_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."


def test_node_major_version_is_24():
    result = subprocess.run(
        ["node", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"`node --version` failed (rc={result.returncode}).\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    version = result.stdout.strip().lstrip("v")
    major = version.split(".")[0] if version else ""
    assert major == "24", (
        f"Expected Node.js major version 24, got {result.stdout.strip()!r}."
    )


def test_home_directory_exists():
    assert os.path.isdir(HOME_DIR), f"Expected home directory {HOME_DIR} to exist."


def test_alchemyst_api_key_env_present():
    key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert key, (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task "
        "environment so the CLI can authenticate with the real Alchemyst AI service."
    )


def test_zealt_run_id_env_present():
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, (
        "ZEALT_RUN_ID environment variable must be set so the CLI can "
        "namespace its file_name and run concurrently with other trials."
    )


def test_python_alchemyst_sdk_importable():
    # The verifier (final state test) uses the Python SDK to independently
    # confirm what the TypeScript CLI did, so it must be importable in the
    # environment.
    import importlib

    mod = importlib.import_module("alchemyst_ai")
    assert mod is not None, "alchemyst_ai Python SDK must be importable for verification."
