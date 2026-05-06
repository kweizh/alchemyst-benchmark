FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages alchemystai

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Alchemyst AI python RAG task environment with a sample policy document."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    cat >policy.txt <<'EOF'
General Return Policy: Items can be returned within 30 days of receipt.
Electronics Policy: Electronics can be returned within 14 days in unopened condition.
Clothing Policy: Clothing can be returned within 30 days with tags attached.
EOF

# Container contents:
#   - alchemystai python SDK installed.
#   - /home/user/project  — task working directory
#   - /home/user/project/policy.txt — policy document to be indexed

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]