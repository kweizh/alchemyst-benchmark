FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-create the project directory and install the Alchemyst AI TypeScript SDK
# plus tsx (for running TypeScript files directly) so the agent only has to
# write the script.
RUN mkdir -p /home/user/rag_task && \
    cd /home/user/rag_task && \
    npm init -y >/dev/null && \
    npm install --silent @alchemystai/sdk tsx typescript @types/node

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI TypeScript SDK task environment with Node.js 24, @alchemystai/sdk, and tsx pre-installed."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests (used by tests/test_final_state.py to hit the real Alchemyst API)
#   - Node.js v24 for the TypeScript task environment
#   - /home/user/rag_task: project directory with @alchemystai/sdk, tsx, typescript, @types/node pre-installed
