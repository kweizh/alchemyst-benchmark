import os
import subprocess
import time
import socket
import json
import urllib.request
import pytest

PROJECT_DIR = "/home/user/project"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Start the app
    process = subprocess.Popen(
        ["node", "index.js"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the app to be ready
    if not wait_for_port(3000):
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_ingest_and_research(start_app):
    # Test POST /ingest
    ingest_url = "http://localhost:3000/ingest"
    ingest_data = json.dumps({
        "content": "The new B2B product is awesome.",
        "group": "b2b_news"
    }).encode('utf-8')
    
    req = urllib.request.Request(ingest_url, data=ingest_data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected POST /ingest to return 200, got {response.status}"
    except urllib.error.HTTPError as e:
        pytest.fail(f"POST /ingest failed with status {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        pytest.fail(f"POST /ingest failed: {e}")

    # Wait a bit for indexing (just in case Alchemyst AI needs a moment)
    time.sleep(5)

    # Test GET /research
    research_url = "http://localhost:3000/research?query=B2B&group=b2b_news"
    try:
        with urllib.request.urlopen(research_url) as response:
            assert response.status == 200, f"Expected GET /research to return 200, got {response.status}"
            body = response.read().decode('utf-8')
            assert "B2B" in body or "awesome" in body, f"Expected search results to contain ingested content, got: {body}"
    except urllib.error.HTTPError as e:
        pytest.fail(f"GET /research failed with status {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        pytest.fail(f"GET /research failed: {e}")
