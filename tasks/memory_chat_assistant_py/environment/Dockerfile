FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        alchemystai==0.10.0 \
        openai && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Python environment for an Alchemyst AI v0.10.0 + OpenAI memory-aware chat-assistant CLI task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - alchemystai==0.10.0: Alchemyst AI Python SDK (note: v0.10.0 has NO memory.search)
#   - openai: OpenAI Python SDK for chat completions
#   - /home/user/myproject: empty project directory where the executor builds main.py
