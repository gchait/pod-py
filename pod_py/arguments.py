import click
from pathlib import Path


kubeconfig = click.argument(
    "kubeconfig",
    type=click.Path(exists=True, dir_okay=False, readable=True, allow_dash=False),
)

manifest = click.argument(
    "manifest",
    type=click.Path(
        exists=True, dir_okay=False, readable=True, allow_dash=False, path_type=Path
    ),
)

namespace = click.argument("namespace")

name = click.argument("name")

command = click.argument("command")

directory = click.argument("directory")

src_path = click.argument("src_path")

dest_path = click.argument("dest_path")
