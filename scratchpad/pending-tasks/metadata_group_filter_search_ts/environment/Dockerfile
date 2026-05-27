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
RUN mkdir -p /workspace && chmod 0777 /workspace

RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "alchemyst-group-filter-search",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "@alchemystai/sdk": "latest",
    "uuid": "latest"
  }
}
EOF

RUN cd /home/user/myproject && npm install --no-audit --no-fund

LABEL Author="generate-harbor-tasks"
LABEL Description="Node.js 20 + Alchemyst AI TypeScript SDK environment for testing the group_name vs groupName parameter inconsistency."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests (used by tests/test_final_state.py for direct API cross-check)
#   - Node.js v20 (NodeSource) for the @alchemystai/sdk TypeScript task environment
#   - /home/user/myproject: Node.js project with @alchemystai/sdk and uuid pre-installed via npm
#   - /workspace: directory where /workspace/group_result.json will be written by the task
