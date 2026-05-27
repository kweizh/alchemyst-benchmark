FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -sf /usr/bin/python3 /usr/local/bin/python && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        alchemystai \
        openai && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/cli-chatbot && chmod 0755 /home/user/cli-chatbot
RUN mkdir -p /workspace && chmod 0755 /workspace

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI CLI chatbot (Python) task environment with alchemystai and openai SDKs."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Alchemyst AI Python SDK: alchemystai
#   - OpenAI Python SDK: openai
#   - /home/user/cli-chatbot: working directory for the CLI chatbot project
#   - /workspace: directory for the captured CLI reply file (/workspace/cli_reply.txt)
