import os
import shutil
import subprocess


PROJECT_DIR = "/workspace"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 is not available in PATH."


def test_python_version_is_311_or_higher():
    result = subprocess.run(
        ["python3", "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"],
        capture_output=True,
        text=True,
        check=True,
    )
    parts = result.stdout.strip().split()
    assert len(parts) == 2, f"Unexpected python version output: {result.stdout!r}"
    major, minor = int(parts[0]), int(parts[1])
    assert (major, minor) >= (3, 11), (
        f"Python 3.11+ is required, found {major}.{minor}."
    )


def test_alchemyst_ai_sdk_importable():
    result = subprocess.run(
        ["python3", "-c", "import alchemyst_ai; print(alchemyst_ai.__name__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Failed to import alchemyst_ai SDK. stderr: {result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_alchemyst_api_key_env_present():
    assert os.environ.get("ALCHEMYST_AI_API_KEY"), (
        "ALCHEMYST_AI_API_KEY environment variable must be set in the task environment."
    )


def test_zealt_run_id_env_present():
    assert os.environ.get("ZEALT_RUN_ID"), (
        "ZEALT_RUN_ID environment variable must be set in the task environment."
    )
