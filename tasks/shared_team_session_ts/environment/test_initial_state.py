import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"package.json missing at {pkg_path}."


def test_alchemystai_sdk_installed():
    sdk_pkg = os.path.join(PROJECT_DIR, "node_modules", "@alchemystai", "sdk", "package.json")
    assert os.path.isfile(sdk_pkg), (
        "Expected @alchemystai/sdk to be pre-installed under node_modules."
    )


def test_workspace_dir_exists():
    assert os.path.isdir("/workspace"), "/workspace directory does not exist."


def test_alchemyst_api_key_env_var_set():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable is not set."


def test_zealt_run_id_env_var_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."


def test_package_json_declares_alchemystai_sdk():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = pkg.get("dependencies", {})
    assert "@alchemystai/sdk" in deps, (
        "Expected @alchemystai/sdk to be declared in dependencies of package.json."
    )
