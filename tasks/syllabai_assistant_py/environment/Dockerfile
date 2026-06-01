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
RUN mkdir -p /home/user/syllabai && chmod 0755 /home/user/syllabai

LABEL Author="generate-harbor-tasks"
LABEL Description="SyllabAI Assistant task environment with the Alchemyst AI Python SDK v0.10.0 and the OpenAI Python SDK for building a course-scoped syllabus Q&A CLI."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - alchemystai==0.10.0 (Alchemyst AI Python SDK) for Context Engine ingestion and retrieval
#   - openai (OpenAI Python SDK) for chat completions
#   - /home/user/syllabai: project directory for the executor's CLI implementation
