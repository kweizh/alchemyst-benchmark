FROM ubuntu:24.04

# System dependencies + Python 3 toolchain + Alchemyst Python SDK.
# Note: we also pin `python3-pytest` from apt and install `pytest-json-ctrf`
# (required by the verifier harness) plus `alchemystai` (Python SDK, imported as
# `alchemyst_ai`) and `requests` for any auxiliary HTTP checks.
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        alchemystai \
        requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI Python SDK (alchemystai) task environment for the 409 Conflict handling task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - pip3 packages: pytest-json-ctrf, alchemystai (Python SDK for Alchemyst AI), requests
#   - /home/user/myproject: empty project directory where the agent writes solution.py and status.json
#   - The pre-seeded v1 document is created at evaluation start by the
#     session-scoped autouse fixture in environment/test_initial_state.py, which
#     runs with ALCHEMYST_AI_API_KEY and the run-scoped task env vars injected by
#     the Harbor evaluator.
