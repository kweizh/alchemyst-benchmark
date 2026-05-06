import os
import subprocess
import time
import socket
import pytest
import requests

PROJECT_DIR = "/home/user/zendocs-backend"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Install dependencies just in case
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)
    
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
        # Kill the process group before failing
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on required port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_generate_and_search(start_app):
    base_url = "http://localhost:3000"

    # Step 1: POST to /api/docs/generate
    payload1 = {
        "fileName": "doc1.md",
        "content": "Zendocs is a great tool for SEO.",
        "group": "marketing"
    }
    res1 = requests.post(f"{base_url}/api/docs/generate", json=payload1)
    assert res1.status_code == 200, f"Expected 200 OK for first generate, got {res1.status_code}: {res1.text}"

    # Wait a bit for indexing
    time.sleep(2)

    # Step 2: GET to /api/docs/search
    res2 = requests.get(f"{base_url}/api/docs/search", params={"q": "Zendocs", "group": "marketing"})
    assert res2.status_code == 200, f"Expected 200 OK for first search, got {res2.status_code}: {res2.text}"
    data2 = res2.json()
    assert "Zendocs is a great tool" in str(data2), f"Expected 'Zendocs is a great tool' in search results, got: {data2}"

    # Step 3: POST to /api/docs/generate (Update)
    payload3 = {
        "fileName": "doc1.md",
        "content": "Zendocs is an amazing tool for SEO and indexing.",
        "group": "marketing"
    }
    res3 = requests.post(f"{base_url}/api/docs/generate", json=payload3)
    assert res3.status_code == 200, f"Expected 200 OK for second generate (update), got {res3.status_code}: {res3.text}"

    # Wait a bit for indexing
    time.sleep(2)

    # Step 4: GET to /api/docs/search (Updated content)
    res4 = requests.get(f"{base_url}/api/docs/search", params={"q": "indexing", "group": "marketing"})
    assert res4.status_code == 200, f"Expected 200 OK for second search, got {res4.status_code}: {res4.text}"
    data4 = res4.json()
    assert "indexing" in str(data4), f"Expected 'indexing' in search results, got: {data4}"

    # Step 5: GET to /api/docs/search (Different group)
    res5 = requests.get(f"{base_url}/api/docs/search", params={"q": "indexing", "group": "engineering"})
    assert res5.status_code == 200, f"Expected 200 OK for third search, got {res5.status_code}: {res5.text}"
    data5 = res5.json()
    results = data5.get("results", [])
    assert len(results) == 0, f"Expected empty results for different group, got: {results}"
