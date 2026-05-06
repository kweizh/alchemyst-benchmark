import os
import shutil
import pytest

PROJECT_DIR = "/home/user/app"

def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_npx_binary_available():
    assert shutil.which("npx") is not None, "npx binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_index_ts_exists():
    index_path = os.path.join(PROJECT_DIR, "index.ts")
    assert os.path.isfile(index_path), f"File {index_path} does not exist."

def test_package_json_exists():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"File {package_json_path} does not exist."