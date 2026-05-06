FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Node.js project with @alchemystai/sdk and a directory of markdown documents."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    npm init -y && \
    npm install @alchemystai/sdk tsx typescript @types/node

RUN mkdir -p /home/user/docs && \
    echo "Refunds are processed within 30 days." > /home/user/docs/policy1.md && \
    echo "Support hours are 9 AM to 5 PM EST." > /home/user/docs/policy2.md && \
    echo "Contact us at support@example.com for urgent issues." > /home/user/docs/policy3.md

# Container contents:
#   - Node.js v24 installed.
#   - /home/user/project - Node.js project with @alchemystai/sdk, tsx, typescript.
#   - /home/user/docs - Directory containing 3 policy markdown files.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
