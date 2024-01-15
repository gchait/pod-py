"""Some general utilities to be used by other modules.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, NamedTuple, Optional

import click
import yaml


@dataclass(kw_only=True, slots=True, frozen=True)
class PodInfo:
    """A structure to store Pod metadata (or its entire manifest) in."""

    namespace: str
    name: str
    manifest: Optional[dict] = None

    def __str__(self):
        return f"Pod {self.name} in namespace {self.namespace}"

    @classmethod
    def extended_load(cls, yaml_path: Path) -> PodInfo:
        with yaml_path.open(mode="r", encoding="utf-8") as raw:
            manifest = yaml.safe_load(raw)

        if "metadata" not in manifest:
            kube_error("Missing pod `metadata`.")

        if not manifest["metadata"] or "name" not in manifest["metadata"]:
            kube_error("Missing pod `metadata.name`.")

        name = manifest["metadata"]["name"]
        namespace = manifest["metadata"].get("namespace", "default")
        return cls(namespace=namespace, name=name, manifest=manifest)

    @classmethod
    def basic_load(cls, namespace: str, name: str) -> PodInfo:
        return cls(namespace=namespace, name=name)


class CommandResult(NamedTuple):
    out: str = ""
    err: str = ""


def cli_print(msg: str) -> None:
    click.echo(msg)


def cli_error(msg: str) -> None:
    click.secho(msg, err=True, fg="red")
    sys.exit(1)


def kube_error(msg: str) -> None:
    click.secho(msg, err=True, fg="red")
    sys.exit(2)


def cli_eval_pod_manager_results(func: Callable, **kwargs) -> None:
    for stdout, stderr in func(**kwargs):
        if stdout:
            cli_print(stdout)
        if stderr:
            kube_error(stderr)
