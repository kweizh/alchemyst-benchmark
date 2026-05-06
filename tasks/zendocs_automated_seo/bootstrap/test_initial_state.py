import os
import shutil
import pytest

PROJECT_DIR = "/home/user/zendocs-backend"

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_node_installed():
    assert shutil.which("node") is not None, "Node.js is not installed."
    assert shutil.which("npm") is not None, "npm is not installed."
