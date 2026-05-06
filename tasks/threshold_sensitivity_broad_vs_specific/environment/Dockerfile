FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages alchemystai openai

RUN mkdir -p /home/user/project && chmod 0755 /home/user/project

LABEL Author="any-task-builder"
LABEL Description="Alchemyst AI environment for testing threshold sensitivity."

# Container contents:
#   - python3 and alchemystai installed
#   - /home/user/project created

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
