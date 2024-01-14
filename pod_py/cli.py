import sys
from dataclasses import dataclass

import click

from .manager import PodManager
from .utils import PodInfo
from . import arguments


@dataclass(kw_only=True, slots=True)
class PodCliData:
    pod_info: PodInfo
    pod_manager: PodManager


@click.group()
@arguments.kubeconfig
@arguments.manifest
@click.pass_context
def new_pod(ctx, kubeconfig, manifest):
    pod_info=PodInfo.extended_load(yaml_path=manifest)
    pod_manager = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)
    ctx.obj = PodCliData(pod_info=pod_info, pod_manager=pod_manager)


@click.group()
@arguments.kubeconfig
@arguments.namespace
@arguments.name
@click.pass_context
def existing_pod(ctx: click.Context, kubeconfig, namespace, name):
    pod_info=PodInfo.basic_load(namespace=namespace, name=name)
    pod_manager = PodManager(kubeconfig=kubeconfig, pod_info=pod_info)
    ctx.obj = PodCliData(pod_info=pod_info, pod_manager=pod_manager)


@new_pod.command(help="Deploy a pod.")
@click.pass_context
def deploy(ctx: click.Context):
    for stdout, stderr in ctx.obj.pod_manager.deploy():
        if stdout:
            click.echo(stdout)
        if stderr:
            click.secho(stderr, err=True, fg="red")
            sys.exit(1)


@existing_pod.command(help="Execute a Bash command inside a pod.")
@arguments.command
@click.pass_context
def execute(ctx: click.Context, command: str):
    ...


@existing_pod.command(help="List files inside a given directory in a pod.")
@arguments.directory
@click.pass_context
def ls(ctx: click.Context, directory: str):
    ...


@existing_pod.command(help="Copy a file to/from the pod, Use `pod://` to reference it.")
@arguments.src_path
@arguments.dest_path
@click.pass_context
def cp(ctx: click.Context, src_path: str, dest_path: str):
    ...
