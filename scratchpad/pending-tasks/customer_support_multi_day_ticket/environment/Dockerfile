FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages alchemystai

RUN mkdir -p /home/user/app && chmod -R 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Alchemyst AI python environment for multi-day support ticket."

# Container contents:
#   - alchemystai python package installed
#   - /home/user/app

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
