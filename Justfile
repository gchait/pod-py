install:
    command -v poetry || { >&2 echo "Please install poetry first."; exit 2; }
    poetry install

kube:
    minikube start --driver=docker

fmt:
    poetry run ruff format .

lint:
    poetry run ruff check .
    poetry run mypy --pretty --disable-error-code=import-untyped .
    poetry run bandit --skip=B101 -qr .

test:
    poetry run pytest -W ignore::DeprecationWarning .

qa: fmt lint test
