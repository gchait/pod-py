set dotenv-load

run *ARGS: venv
    python3 -m pod_py {{ARGS}}

fmt: venv
    isort "${PY_SRC}" > /dev/null
    black "${PY_SRC}" 2> /dev/null

lint: venv
    flake8 --max-line-length "${PY_MAX_LINE_LEN}" "${PY_SRC}"
    pylint "${PY_SRC}"
    bandit -r "${PY_SRC}"

test: venv
    python3 -m unittest

venv:
    #!/bin/bash
    set -euo pipefail
    python3 -m venv ./.venv
    source ./.venv/bin/activate
    set -x
    pip3 install -q -r ./requirements_dev.txt -r ./requirements.txt
