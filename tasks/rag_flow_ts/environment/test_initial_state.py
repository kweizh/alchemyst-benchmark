import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_version_is_24():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip()
    assert version.startswith("v24."), (
        f"Expected Node.js v24.x to be installed, but got '{version}'."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_alchemyst_api_key_env_set():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY", "")
    assert api_key.strip() != "", (
        "ALCHEMYST_AI_API_KEY environment variable is not set or is empty."
    )


def test_zealt_run_id_env_set():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id.strip() != "", (
        "ZEALT_RUN_ID environment variable is not set or is empty."
    )
