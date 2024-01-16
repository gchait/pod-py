install:
    command -v poetry || { >&2 echo "Please install poetry first."; exit 2; }
    poetry install

kube:
    minikube start --driver=docker

fmt:
    poetry run ruff format .

lint:
    poetry run ruff check --fix .
    poetry run mypy --pretty .
    poetry run bandit --skip=B101 -qr .

test:
    poetry run pytest -W ignore::DeprecationWarning .

qa: fmt lint test
