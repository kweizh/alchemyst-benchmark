FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf alchemystai && \
    npm install -g typescript && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/alchemyst-task && \
    cd /home/user/alchemyst-task && \
    npm init -y && \
    npm install @alchemystai/sdk typescript @types/node

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI environment with Node.js v24, TypeScript, and @alchemystai/sdk installed."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - pip3 packages: alchemystai (for verification)
#   - Node.js v24 for the TypeScript task environment
#   - global npm packages: typescript
#   - /home/user/alchemyst-task: directory for the project
#   - /home/user/alchemyst-task/node_modules: @alchemystai/sdk, typescript, @types/node
