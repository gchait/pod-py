run *ARGS:
    poetry run pod-py {{ARGS}}

clean:
    find . -type d -name "__pycache__" | xargs rm -rf {};

install:
    command -v poetry || { >&2 echo "Please install poetry first."; exit 2; }
    poetry install

fmt:
    poetry run isort --profile=black .
    poetry run black .

lint:
    poetry run flake8 --max-line-length=90 .
    poetry run bandit --skip=B101 -r .

test:
    poetry run pytest .

qa: fmt lint test

kube:
    minikube start --driver=docker
