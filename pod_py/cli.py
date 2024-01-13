from pathlib import Path
from sys import exit

import click

from .manager import PodManager
from .utils import PodInfo


@click.group()
def cli():
    pass


@cli.command(help="Deploy a pod.")
@click.argument(
    "kubeconfig",
    type=click.Path(exists=True, dir_okay=False, readable=True, allow_dash=False),
)
@click.argument(
    "manifest_path",
    type=click.Path(
        exists=True, dir_okay=False, readable=True, allow_dash=False, path_type=Path
    ),
)
def deploy(kubeconfig: Path, manifest_path: Path):
    pod_info = PodInfo.extended_load(yaml_path=manifest_path)
    pod_manager = PodManager(kubeconfig_path=kubeconfig, pod_info=pod_info)

    for stdout, stderr in pod_manager.deploy():
        if stdout:
            click.echo(stdout)
        if stderr:
            click.secho(stderr, err=True, fg="red")
            exit(1)


@cli.command(help="Execute a Bash command inside a pod.")
@click.argument(
    "kubeconfig",
    type=click.Path(exists=True, dir_okay=False, readable=True, allow_dash=False),
)
@click.argument("namespace")
@click.argument("name")
@click.argument("command")
def execute(kubeconfig: Path, namespace: str, name: str, command: str):
    ...


@cli.command(help="List files inside a given directory in a pod.")
@click.argument(
    "kubeconfig",
    type=click.Path(exists=True, dir_okay=False, readable=True, allow_dash=False),
)
@click.argument("namespace")
@click.argument("name")
@click.argument("directory")
def ls(kubeconfig: Path, namespace: str, name: str, directory: str):
    ...


@cli.command(help="Copy a file to/from the pod, Use `pod://` to reference it.")
@click.argument(
    "kubeconfig",
    type=click.Path(exists=True, dir_okay=False, readable=True, allow_dash=False),
)
@click.argument("namespace")
@click.argument("name")
@click.argument("src_path")
@click.argument("dest_path")
def cp(kubeconfig: Path, namespace: str, name: str, src_path: str, dest_path: str):
    ...
