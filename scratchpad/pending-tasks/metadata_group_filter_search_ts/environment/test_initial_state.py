import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_node_version_20_or_higher():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Node.js version must be >= 20, got {version}."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_workspace_directory_exists():
    assert os.path.isdir("/workspace"), "/workspace directory does not exist."


def test_alchemystai_sdk_installed():
    sdk_path = os.path.join(PROJECT_DIR, "node_modules", "@alchemystai", "sdk")
    assert os.path.isdir(sdk_path), (
        f"@alchemystai/sdk is not installed at {sdk_path}."
    )


def test_alchemyst_api_key_set():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable is not set."
    )


def test_zealt_run_id_set():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "ZEALT_RUN_ID environment variable is not set."
    )


def test_group_result_does_not_exist():
    assert not os.path.exists("/workspace/group_result.json"), (
        "/workspace/group_result.json should not exist before the task starts."
    )
