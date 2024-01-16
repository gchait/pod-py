## Pod-Py

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

**A simple CLI to create or manage a Kubernetes Pod.**

![](./demo.gif)
<sub>Demo created with [asciinema](https://github.com/asciinema/asciinema) and [agg](https://github.com/asciinema/agg).</sub>


### Prerequisites
- Python 3.12+ (might work with .11 or even .10, haven't tested).
- [Poetry](https://python-poetry.org/docs/#installation).
- [Just](https://just.systems/man/en/chapter_4.html).
- A running Kubernetes cluster (I used [Minikube](https://minikube.sigs.k8s.io/docs/start/) here).
- A kubeconfig file that gives you Pod management permissions.
- I haven't tested this on Windows, but it might work regardless.


### Assumptions
- The Pod has only one container.
- The Pod has `bash` and `tar`.
- For `deploy`, your YAML file contains only a Pod and nothing more.


### Installation
```
git clone https://github.com/gchait/pod-py.git
cd pod-py
just install
```


### Usage

##### A new Pod
```
❯ poetry run pod-py-new ~/.kube/config ./pod.yaml --help
Usage: pod-py-new [OPTIONS] KUBECONFIG MANIFEST COMMAND [ARGS]...

  Perform actions on a new Pod.

Options:
  --help  Show this message and exit.

Commands:
  deploy  Deploy a Pod.
```

##### Manage an existing Pod
```
❯ poetry run pod-py-manage ~/.kube/config hi nginx --help
Usage: pod-py-manage [OPTIONS] KUBECONFIG NAMESPACE NAME COMMAND [ARGS]...

  Perform actions on an existing Pod.

Options:
  --help  Show this message and exit.

Commands:
  cp  Copy files to/from a Pod, Use `pod://` to reference it.
  ex  Execute a Bash command inside a Pod.
  ls  List files inside a Pod.
```

##### Commands used in the demo above
```
❯ just kube
❯ just install
❯ just qa
❯ poetry run pod-py-new ~/.kube/config ./pod.yaml deploy
❯ mkdir -p /tmp/very/much; echo -n "lala\n123\nlala\n456" > /tmp/very/much/hello.txt
❯ poetry run pod-py-manage ~/.kube/config hi nginx cp /tmp/very pod:///tmp
❯ poetry run pod-py-manage ~/.kube/config hi nginx ex "cat /tmp/very/much/hello.txt"
❯ poetry run pod-py-manage ~/.kube/config hi nginx ls /etc/nginx
❯ poetry run pod-py-manage ~/.kube/config hi nginx cp pod:///etc/nginx/nginx.conf .
❯ head ./nginx.conf
```

### Important notes and decisions
- There are 2 separate top-level commands/scripts (`pod-py-new`, `pod-py-manage`) because of [this issue](https://github.com/pallets/click/issues/347). I didn't like the hacky solutions I found online.

- The public methods of `PodManager` are generators because I wanted to support many `yield`s over a long period of time, e.g. for long/complex actions/pipelines, while a second CLI thread is free to do other things, e.g. display a progress bar according to some shared state. The `PodManager` is designed to communicate only with the CLI, which in turn can communicate with the end-user.

- I kept it simple, everything is a Click `argument` (no `option`s) and everything is required. No defaults, no `nargs`.

- Because the `cp` backend is `tar` (and Python's `tarfile`) in both directions, technically both files and directories should be supported. I suppose that `cat` is a simpler solution for single files.

- The `new_pod` CLI group exists (rather than straight up calling `deploy` directly) to support more actions on non-existing Pods, such as client-side schema validation, security best-practices linting, scanning the image itself (e.g. with `grype`) etc. Also, it's more elegant to have 2 parallel groups so that all upstream commands are comparable in logic, argument/context inheritence, and development processes.


### Ideas to make it better
- A proper CI/CD pipeline (with GitHub actions being an obvious pick here), feature branching, tags, releases etc.

- Add an option to run this as a docker container, to have somewhat less prerequisites. Might be overkill.

- Package it for proper hosted distribution (there is no reason since `kubectl` exists, but would still be fun/funny), at least for `pip`, `dnf`, `apt`, `scoop` and standalones (maybe for more architectures, maybe PyInstaller).

- Add more (and actual) tests.

- Take actual advantage of the `PodManager` generating results on the fly, or refactor it to just build `out` and `err` strings and return them at once.

- When executing on the Pod, find a way to get the return code and return the same one to the end-user.

- Verify which Python version is actually required here.

- Handle more exceptions, I probably didn't cover a lot that could go wrong.


<sub><sup>Disclaimer: This is not the best I can do. It might be the best I can do in less than a week, in my free time, using technologies I've never used before such as Click, Poetry and Ruff (which I do believe are the best for the job). Of course, no kind of AI was used.</sub></sup>
