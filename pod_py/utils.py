from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from sys import exit
from typing import NamedTuple, Optional

import click
import yaml


@dataclass(kw_only=True, slots=True, frozen=True)
class PodInfo:
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
            click.echo("Missing pod `metadata`.", err=True)
            exit(2)
        if not manifest["metadata"] or "name" not in manifest["metadata"]:
            click.echo("Missing pod `metadata.name`.", err=True)
            exit(2)

        name = manifest["metadata"]["name"]
        namespace = manifest["metadata"].get("namespace", "default")
        return cls(namespace=namespace, name=name, manifest=manifest)

    @classmethod
    def basic_load(cls, namespace: str, name: str) -> PodInfo:
        return cls(namespace=namespace, name=name)


class CommandResult(NamedTuple):
    out: str = ""
    err: str = ""
