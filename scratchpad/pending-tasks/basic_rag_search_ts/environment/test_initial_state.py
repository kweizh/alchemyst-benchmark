import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/rag_task"


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
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_alchemyst_sdk_installed():
    sdk_path = os.path.join(PROJECT_DIR, "node_modules", "@alchemystai", "sdk")
    assert os.path.isdir(sdk_path), (
        f"@alchemystai/sdk is not installed at {sdk_path}. "
        "It must be pre-installed in the environment."
    )


def test_tsx_available():
    # tsx is required to execute the TypeScript script via `npx tsx`.
    tsx_path = os.path.join(PROJECT_DIR, "node_modules", "tsx")
    assert os.path.isdir(tsx_path), (
        f"tsx is not installed at {tsx_path}. It must be pre-installed in the environment."
    )


def test_alchemyst_api_key_env_var_set():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set."
    )


def test_zealt_run_id_env_var_set():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable must be set."
