import os
import shutil

def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."

def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_alchemystai_python_package_available():
    try:
        import alchemystai
    except ImportError:
        assert False, "alchemystai Python package is not installed."

def test_api_key_in_env():
    assert "ALCHEMYST_AI_API_KEY" in os.environ, "ALCHEMYST_AI_API_KEY environment variable is missing."