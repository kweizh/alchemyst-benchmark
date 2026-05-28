import json
import os
import shutil

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_DIR = "/workspace"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_workspace_directory_exists():
    assert os.path.isdir(WORKSPACE_DIR), (
        f"Workspace directory {WORKSPACE_DIR} does not exist."
    )


def test_package_json_exists():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), (
        f"package.json file {pkg_path} does not exist."
    )


def test_required_dependencies_declared():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}) or {})
    deps.update(pkg.get("devDependencies", {}) or {})
    for required in ("ai", "@ai-sdk/openai", "@alchemystai/aisdk"):
        assert required in deps, (
            f"Required dependency '{required}' is not declared in package.json."
        )


def test_node_modules_installed():
    for mod in ("ai", "@ai-sdk/openai", "@alchemystai/aisdk"):
        mod_dir = os.path.join(PROJECT_DIR, "node_modules", mod)
        assert os.path.isdir(mod_dir), (
            f"Expected node module '{mod}' to be pre-installed at {mod_dir}."
        )


def test_node_version_is_20_or_newer():
    import subprocess

    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, (
        f"Node.js version must be >= 20, found {version}."
    )
