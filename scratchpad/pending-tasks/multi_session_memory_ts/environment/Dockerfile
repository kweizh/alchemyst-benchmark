FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /workspace && chmod 0755 /workspace

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI memory cross-session recall task environment with Node.js 20 and the @alchemystai/sdk TypeScript SDK available via npm."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages used by verification: requests
#   - Node.js v20 (npm bundled) so the executor can install @alchemystai/sdk and run a TypeScript script
#   - /workspace: empty project directory the executor uses for the Node.js project and /workspace/recall.json output
#   - /home/user: standard user home directory
