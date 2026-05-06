import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/app"

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_alchemystai_installed():
    result = subprocess.run(["python3", "-c", "import alchemyst_ai"], capture_output=True)
    assert result.returncode == 0, "alchemyst_ai python package is not installed."
