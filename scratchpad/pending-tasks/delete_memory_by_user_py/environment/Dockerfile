FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        software-properties-common gnupg && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.11 python3.11-venv python3.11-distutils && \
    python3.11 -m ensurepip --upgrade && \
    python3.11 -m pip install --break-system-packages --ignore-installed --no-cache-dir \
        pip pytest pytest-json-ctrf alchemystai && \
    pip3 install --break-system-packages --no-cache-dir pytest-json-ctrf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Make python3.11 the default `python3` and `python` so the task environment
# satisfies the "Python 3.11+" requirement.
RUN ln -sf /usr/bin/python3.11 /usr/local/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/local/bin/python

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject && chmod 0755 /home/user/myproject
RUN mkdir -p /workspace && chmod 0755 /workspace

LABEL Author="generate-harbor-tasks"
LABEL Description="Alchemyst AI Python SDK environment for the delete_memory_by_user_py task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - Python 3.11 from deadsnakes PPA, made default `python3`/`python`
#   - pip installed for python3.11 via get-pip.py
#   - always required pip3 packages: pytest-json-ctrf
#   - Alchemyst AI Python SDK (`alchemystai`) + pytest, pytest-json-ctrf for python3.11
#   - /home/user/myproject: working directory for the executor
#   - /workspace: output directory for /workspace/post_delete_search.json
