import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/agent"

@pytest.fixture(scope="module", autouse=True)
def setup_seed():
    """Run seed.js to populate Alchemyst AI context."""
    assert os.path.isfile(os.path.join(PROJECT_DIR, "seed.js")), "seed.js not found in /home/user/agent"
    
    result = subprocess.run(
        ["node", "seed.js"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"seed.js failed to execute: {result.stderr}"

def test_agent_with_context():
    """Verify the agent can retrieve the secret code from Alchemyst AI."""
    assert os.path.isfile(os.path.join(PROJECT_DIR, "agent.js")), "agent.js not found in /home/user/agent"
    
    result = subprocess.run(
        ["node", "agent.js", "What is the secret launch code for Project Nova?"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"agent.js failed to execute: {result.stderr}"
    assert "8847-ALPHA" in result.stdout, f"Expected '8847-ALPHA' in output, got: {result.stdout}"

def test_agent_fallback():
    """Verify the agent can answer general questions using LLM fallback."""
    result = subprocess.run(
        ["node", "agent.js", "What is the capital of France?"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"agent.js failed to execute: {result.stderr}"
    assert "Paris" in result.stdout, f"Expected 'Paris' in output, got: {result.stdout}"
