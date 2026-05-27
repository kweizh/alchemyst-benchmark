FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages pytest-json-ctrf alchemystai && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI Python SDK environment with a pre-existing policy document for the document-update-cycle task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - alchemystai (Alchemyst AI Python SDK) installed via pip3 for the task
#   - /home/user/myproject: working directory for the task. The pre-existing
#     policy document is ingested into the Alchemyst AI platform by the
#     initial-state pytest fixture (preload_initial_document) using
#     ALCHEMYST_AI_API_KEY and ZEALT_RUN_ID provided at runtime via envs.json.
