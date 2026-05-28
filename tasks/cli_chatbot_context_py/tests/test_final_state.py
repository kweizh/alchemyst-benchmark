import os
import subprocess
import sys


PROJECT_DIR = "/home/user/cli-chatbot"
CHAT_SCRIPT = os.path.join(PROJECT_DIR, "chat.py")
REPLY_FILE = "/workspace/cli_reply.txt"


def _run_chat(prompt: str):
    """Invoke chat.py with a single positional question argument and capture stdout."""
    env = os.environ.copy()
    return subprocess.run(
        [sys.executable, CHAT_SCRIPT, prompt],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        env=env,
        timeout=180,
    )


def test_chat_script_exists():
    assert os.path.isfile(CHAT_SCRIPT), (
        f"Expected chat.py at {CHAT_SCRIPT} but it was not found."
    )


def test_first_invocation_ingest_fact():
    """Run the CLI to state the fact. Must exit 0."""
    # Clean up any prior reply file before the full two-call sequence.
    if os.path.exists(REPLY_FILE):
        os.remove(REPLY_FILE)

    result = _run_chat("My company is named Zenith Robotics")
    assert result.returncode == 0, (
        "First chat.py invocation (ingest fact) must exit with status 0. "
        f"stdout: {result.stdout!r} stderr: {result.stderr!r}"
    )


def test_second_invocation_recalls_fact():
    """Run the CLI asking about the fact and persist stdout to /workspace/cli_reply.txt."""
    result = _run_chat("What is my company?")
    assert result.returncode == 0, (
        "Second chat.py invocation (recall) must exit with status 0. "
        f"stdout: {result.stdout!r} stderr: {result.stderr!r}"
    )

    # Persist the reply to /workspace/cli_reply.txt as required by the truth plan.
    os.makedirs(os.path.dirname(REPLY_FILE), exist_ok=True)
    with open(REPLY_FILE, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    assert os.path.isfile(REPLY_FILE), (
        f"Expected reply file at {REPLY_FILE} to exist after the recall call."
    )


def test_reply_file_contains_company_name():
    assert os.path.isfile(REPLY_FILE), (
        f"Expected reply file at {REPLY_FILE} to exist before checking its content."
    )
    with open(REPLY_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "zenith robotics" in content.lower(), (
        "Expected the CLI's recall answer (saved at /workspace/cli_reply.txt) to "
        f"mention 'Zenith Robotics'. Got: {content!r}"
    )
