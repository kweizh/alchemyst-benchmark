import os
import shutil
import pytest

PROJECT_DIR = "/home/user/alchemyst_project"

def test_python3_binary_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."
