import os
import shutil
import subprocess

PROJECT_DIR = "/workspace"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_node_version_is_20_plus():
    result = subprocess.run(
        ["node", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Node.js major version must be >= 20, got {version}."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_alchemyst_api_key_is_set():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable must be set."


def test_openai_api_key_is_set():
    api_key = os.environ.get("OPENAI_API_KEY")
    assert api_key, "OPENAI_API_KEY environment variable must be set."


def test_zealt_run_id_is_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set."


def test_alchemyst_sdk_resolvable():
    result = subprocess.run(
        ["npm", "view", "@alchemystai/sdk", "name"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        "Unable to resolve @alchemystai/sdk via npm. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "@alchemystai/sdk" in result.stdout, (
        f"npm view did not return the expected package name: {result.stdout!r}"
    )


def test_vercel_ai_sdk_resolvable():
    result = subprocess.run(
        ["npm", "view", "ai", "name"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        "Unable to resolve the 'ai' (Vercel AI SDK) package via npm. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_ai_sdk_openai_resolvable():
    result = subprocess.run(
        ["npm", "view", "@ai-sdk/openai", "name"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        "Unable to resolve @ai-sdk/openai via npm. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "@ai-sdk/openai" in result.stdout, (
        f"npm view did not return the expected package name: {result.stdout!r}"
    )
