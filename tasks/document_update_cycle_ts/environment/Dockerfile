FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf alchemystai && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/update-task && chmod 0755 /home/user/update-task

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI TypeScript SDK task environment: Node.js v24, @alchemystai/sdk available via npm at task time, alchemystai Python SDK for verification."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (via NodeSource) for the TypeScript task runtime; @alchemystai/sdk is installed by the task itself with `npm install`
#   - alchemystai Python SDK installed via pip3 so the verifier can independently confirm context state
#   - /home/user/update-task: empty project directory the agent will populate
