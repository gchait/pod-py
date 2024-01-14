from dataclasses import dataclass

import click

from . import arguments
from .manager import PodManager
from .utils import PodInfo, cli_error, cli_eval_pod_manager_results


@dataclass(kw_only=True, slots=True)
class PodCliData:
    pod_info: PodInfo
    pod_manager: PodManager


@click.group()
@arguments.kubeconfig
@arguments.manifest
@click.pass_context
def new_pod(ctx, kubeconfig, manifest):
    pod_info = PodInfo.extended_load(yaml_path=manifest)
    pod_manager = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)
    ctx.obj = PodCliData(pod_info=pod_info, pod_manager=pod_manager)


@click.group()
@arguments.kubeconfig
@arguments.namespace
@arguments.name
@click.pass_context
def existing_pod(ctx: click.Context, kubeconfig, namespace, name):
    pod_info = PodInfo.basic_load(namespace=namespace, name=name)
    pod_manager = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)
    ctx.obj = PodCliData(pod_info=pod_info, pod_manager=pod_manager)


@new_pod.command(help="Deploy a Pod.")
@click.pass_context
def deploy(ctx: click.Context):
    func = ctx.obj.pod_manager.deploy
    cli_eval_pod_manager_results(func)


@existing_pod.command(help="Execute a Bash command inside a Pod.")
@arguments.command
@click.pass_context
def execute(ctx: click.Context, command: str):
    func = ctx.obj.pod_manager.execute
    cli_eval_pod_manager_results(func, command=command)


@existing_pod.command(help="List files inside a given directory in a Pod.")
@arguments.directory
@click.pass_context
def ls(ctx: click.Context, directory: str):
    func = ctx.obj.pod_manager.ls
    cli_eval_pod_manager_results(func, directory=directory)


@existing_pod.command(help="Copy a file to/from a Pod, Use `pod://` to reference it.")
@arguments.src_path
@arguments.dest_path
@click.pass_context
def cp(ctx: click.Context, src_path: str, dest_path: str):
    is_src_pod = src_path.startswith("pod://")
    is_dest_pod = dest_path.startswith("pod://")

    if is_src_pod and is_dest_pod:
        cli_error("Copying from a pod to itself isn't allowed.")

    if not is_src_pod and not is_dest_pod:
        cli_error("Copying from the host to itself isn't allowed.")

    if is_src_pod:
        src_path = src_path.removeprefix("pod://")
        func = ctx.obj.pod_manager.cp_from_pod

    else:
        dest_path = dest_path.removeprefix("pod://")
        func = ctx.obj.pod_manager.cp_to_pod

    cli_eval_pod_manager_results(func, src_path=src_path, dest_path=dest_path)
