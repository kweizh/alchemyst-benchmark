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
RUN mkdir -p /home/user/myproject/notes && chmod -R 0755 /home/user/myproject

RUN cat >/home/user/myproject/notes/refunds.md <<'EOF'
# Refund Policy

Our refund policy: We offer a 30-day money-back guarantee on all standard
purchases. To request a refund, customers must contact support@example.com
within 30 days of the original purchase date and provide their order number.

Refunds are issued back to the original payment method and may take up to
5-10 business days to appear on the customer's statement.

Subscription products may have different refund terms; consult the
subscription agreement for details.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="Python environment for an Alchemyst AI v0.10.0 + OpenAI context-aware CLI assistant in /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - alchemystai==0.10.0: Alchemyst AI Python SDK (note: v0.10.0 has NO memory.search)
#   - openai: OpenAI Python SDK for chat completions
#   - /home/user/myproject: project directory where the executor builds main.py
#   - /home/user/myproject/notes/refunds.md: seeded markdown note containing the
#       canonical "30-day money-back guarantee" phrase used by the verifier.
