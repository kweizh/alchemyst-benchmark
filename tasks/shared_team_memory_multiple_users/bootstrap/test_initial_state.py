import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_alchemyst_ai_installed():
    result = subprocess.run(
        ["python3", "-c", "import alchemyst_ai"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"alchemyst_ai package is not installed: {result.stderr}"
