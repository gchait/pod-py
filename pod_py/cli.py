"""
Entrypoint for the CLI, only clean-ish high-level CLI logic.
"""

from pathlib import Path
from typing import Any

import click

from . import arguments
from .manager import PodManager
from .utils import PodInfo, cli_error, cli_eval_pod_manager_results


@click.group()
@arguments.kubeconfig
@arguments.manifest
@click.pass_context
def new_pod(ctx: click.Context, kubeconfig: str, manifest: Path) -> None:
    """Perform actions on a new Pod."""
    pod_info = PodInfo.extended_load(yaml_path=manifest)
    ctx.obj = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)


@click.group()
@arguments.kubeconfig
@arguments.namespace
@arguments.name
@click.pass_context
def existing_pod(
    ctx: click.Context, kubeconfig: str, namespace: str, name: str
) -> None:
    """Perform actions on an existing Pod."""
    pod_info = PodInfo.basic_load(namespace=namespace, name=name)
    ctx.obj = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)


@new_pod.command()
@click.pass_context
def deploy(ctx: click.Context, **kwargs: Any) -> None:
    """Deploy a Pod."""
    cli_eval_pod_manager_results(ctx.obj.deploy, **kwargs)


@existing_pod.command()
@arguments.command
@click.pass_context
def ex(ctx: click.Context, **kwargs: Any) -> None:
    """Execute a Bash command inside a Pod."""
    cli_eval_pod_manager_results(ctx.obj.execute, **kwargs)


@existing_pod.command()
@arguments.pod_path
@click.pass_context
def ls(ctx: click.Context, **kwargs: Any) -> None:
    """List files inside a Pod."""
    cli_eval_pod_manager_results(ctx.obj.ls, **kwargs)


@existing_pod.command()
@arguments.src_path
@arguments.dest_path
@click.pass_context
def cp(ctx: click.Context, **kwargs: Any) -> None:
    """Copy files to/from a Pod, Use `pod://` to reference it."""
    is_src_pod = kwargs["src_path"].startswith("pod://")
    is_dest_pod = kwargs["dest_path"].startswith("pod://")

    match is_src_pod, is_dest_pod:
        case True, True:
            cli_error("Copying from a pod to itself isn't allowed.")

        case False, False:
            cli_error("Copying from the host to itself isn't allowed.")

        case True, False:
            kwargs["src_path"] = kwargs["src_path"].removeprefix("pod://")
            cli_eval_pod_manager_results(ctx.obj.cp_from_pod, **kwargs)

        case _:
            kwargs["dest_path"] = kwargs["dest_path"].removeprefix("pod://")
            cli_eval_pod_manager_results(ctx.obj.cp_to_pod, **kwargs)
