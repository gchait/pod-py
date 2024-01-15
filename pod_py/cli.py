"""
Entrypoint for the CLI, only CLI-related objects.
"""

from dataclasses import dataclass
from typing import Callable

import click

from . import arguments
from .manager import PodManager
from .utils import PodInfo, cli_error, cli_eval_pod_manager_results


@dataclass(kw_only=True, slots=True)
class PodCliData:
    """A structure to store CLI context inside, and pass around."""
    pod_info: PodInfo
    pod_manager: PodManager
    func: Callable = lambda **_: None


@click.group()
@arguments.kubeconfig
@arguments.manifest
@click.pass_context
def new_pod(ctx, kubeconfig, manifest):
    """A CLI group for performing actions on a new Pod."""
    pod_info = PodInfo.extended_load(yaml_path=manifest)
    pod_manager = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)
    ctx.obj = PodCliData(pod_info=pod_info, pod_manager=pod_manager)


@click.group()
@arguments.kubeconfig
@arguments.namespace
@arguments.name
@click.pass_context
def existing_pod(ctx: click.Context, kubeconfig, namespace, name):
    """A CLI group for performing actions on an existing Pod."""
    pod_info = PodInfo.basic_load(namespace=namespace, name=name)
    pod_manager = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)
    ctx.obj = PodCliData(pod_info=pod_info, pod_manager=pod_manager)


@new_pod.command()
@click.pass_context
def deploy(ctx: click.Context, **kwargs):
    """Deploy a Pod."""
    ctx.obj.func = ctx.obj.pod_manager.deploy
    cli_eval_pod_manager_results(ctx.obj.func, **kwargs)


@existing_pod.command()
@arguments.command
@click.pass_context
def ex(ctx: click.Context, **kwargs):
    """Execute a Bash command inside a Pod."""
    ctx.obj.func = ctx.obj.pod_manager.execute
    cli_eval_pod_manager_results(ctx.obj.func, **kwargs)


@existing_pod.command()
@arguments.directory
@click.pass_context
def ls(ctx: click.Context, **kwargs):
    """List files inside a given directory in a Pod."""
    ctx.obj.func = ctx.obj.pod_manager.ls
    cli_eval_pod_manager_results(ctx.obj.func, **kwargs)


@existing_pod.command()
@arguments.src_path
@arguments.dest_path
@click.pass_context
def cp(ctx: click.Context, **kwargs):
    """Copy a file to/from a Pod, Use `pod://` to reference it."""
    is_src_pod = kwargs["src_path"].startswith("pod://")
    is_dest_pod = kwargs["dest_path"].startswith("pod://")

    match is_src_pod, is_dest_pod:
        case True, True:
            cli_error("Copying from a pod to itself isn't allowed.")
        
        case False, False:
            cli_error("Copying from the host to itself isn't allowed.")
        
        case True, False:
            kwargs["src_path"] = kwargs["src_path"].removeprefix("pod://")
            ctx.obj.func = ctx.obj.pod_manager.cp_from_pod
        
        case _:
            kwargs["dest_path"] = kwargs["dest_path"].removeprefix("pod://")
            ctx.obj.func = ctx.obj.pod_manager.cp_to_pod
        
    cli_eval_pod_manager_results(ctx.obj.func, **kwargs)
