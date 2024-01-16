"""
Arguments are declared here so the `cli` module won't be ugly.
"""

from pathlib import Path

import click

kubeconfig = click.argument(
    "kubeconfig",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        allow_dash=False,
    ),
)

manifest = click.argument(
    "manifest",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        allow_dash=False,
        path_type=Path,
    ),
)

namespace = click.argument("namespace")

name = click.argument("name")

command = click.argument("command")

pod_path = click.argument("pod_path")

src_path = click.argument("src_path")

dest_path = click.argument("dest_path")
