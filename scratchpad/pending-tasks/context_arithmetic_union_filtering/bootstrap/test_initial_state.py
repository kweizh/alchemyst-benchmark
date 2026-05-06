import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_python_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."

def test_alchemyst_library_installed():
    import subprocess
    result = subprocess.run(["python3", "-c", "import alchemyst_ai"], capture_output=True)
    assert result.returncode == 0, f"alchemyst_ai library not installed. stderr: {result.stderr.decode()}"
