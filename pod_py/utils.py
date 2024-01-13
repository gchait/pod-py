from __future__ import annotations
from dataclasses import dataclass
from os import error
from typing import Optional
from pathlib import Path
import yaml
import click


@dataclass(kw_only=True, slots=True, frozen=True)
class Pod:
    name: str
    namespace: str
    manifest: Optional[dict] = None

    @classmethod
    def extended_load(cls, yaml_location: Path) -> Pod:
        with yaml_location.open(mode="r", encoding="utf-8") as raw:
            manifest = yaml.safe_load(raw)

        if "metadata" not in manifest:
            click.echo("Missing pod `metadata`.", err=True)
            # FAIL HERE
        if "name" not in manifest["metadata"]:
            click.echo("Missing pod `metadata.name`.", err=True)
            # FAIL HERE

        name = manifest["metadata"]["name"]
        namespace = manifest["metadata"].get("namespace", "default")
        return cls(
            name=name,
            namespace=namespace,
            manifest=manifest,
        )
    
    @classmethod
    def basic_load(cls, name: str, namespace: str) -> Pod:
        return cls(name=name, namespace=namespace)


@dataclass(kw_only=True, slots=True)
class CmdResult:
    out: str = ""
    err: str = ""
