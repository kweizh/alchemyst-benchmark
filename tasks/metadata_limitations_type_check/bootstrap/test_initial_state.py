import os
import sys

def test_project_dir_exists():
    assert os.path.isdir('/home/user/myproject'), "/home/user/myproject does not exist"

def test_alchemyst_ai_installed():
    try:
        import alchemyst_ai
    except ImportError:
        assert False, "alchemyst_ai package is not installed"
