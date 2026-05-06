FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages alchemystai==0.10.0

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Alchemyst AI environment with alchemystai installed and a project directory created."

RUN mkdir -p /home/user/project

# Container contents:
#   - alchemystai installed via pip3
#   - /home/user/project: project directory for the task

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
