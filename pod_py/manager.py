"""
The PodManager is the "backend" of the CLI.
All Kubernetes logic sits here, no CLI logic should.
"""

import io
import json
import tarfile
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryFile

from kubernetes.client.api.core_v1_api import CoreV1Api as KubeCoreV1
from kubernetes.client.exceptions import ApiException as KubeApiException
from kubernetes.config import load_kube_config
from kubernetes.stream import stream as kube_stream

from .utils import CommandResult as Cr
from .utils import PodInfo


class PodManager:
    """Using IO, Tars, the Kubernetes SDK and more to manage Pods and stream results."""

    def __init__(self, kubeconfig: str, pod_info: PodInfo):
        """Initialize a new PodManager."""
        load_kube_config(config_file=kubeconfig)
        self._api = KubeCoreV1()
        self._pod_info = pod_info

    @staticmethod
    def _extract_msg_create_error(kae: KubeApiException) -> str:
        """Extract an error message from the Pod creation API."""
        msg = "Creation failed."
        if kae.body:
            msg = json.loads(kae.body).get("message", msg)
        return msg

    @staticmethod
    def _extract_msg_exec_error(kae: KubeApiException) -> str:
        """Extract an error message from the Pod exec API."""
        msg = "Command execution failed."
        if kae.reason:
            msg = kae.reason.split(" -+-+- ")[-1]
        return msg

    def deploy(self) -> Iterator[Cr]:
        """Deploy a new Pod using the SDK and instance state."""
        try:
            self._api.create_namespaced_pod(
                body=self._pod_info.manifest,
                namespace=self._pod_info.namespace,
            )

        except KubeApiException as kae:
            yield Cr(err=self._extract_msg_create_error(kae))

        yield Cr(out=f"{self._pod_info} created successfully!")

    def execute(self, command: str) -> Iterator[Cr]:
        """Execute a Bash command inside a Pod using the SDK and instance state."""
        resp = None
        try:
            resp = kube_stream(
                self._api.connect_get_namespaced_pod_exec,
                self._pod_info.name,
                self._pod_info.namespace,
                command=["/bin/bash", "-c", command],
                tty=False,
                stdin=False,
                stdout=True,
                stderr=True,
            )

        except KubeApiException as kae:
            yield Cr(err=self._extract_msg_exec_error(kae))

        if resp:
            yield Cr(out=resp)

    def ls(self, pod_path: str) -> Iterator[Cr]:
        """Just use the execute method to run a pretty ls command."""
        return self.execute(f"ls -lah {pod_path}")

    def cp_to_pod(self, src_path: str, dest_path: str) -> Iterator[Cr]:
        """Copy a file/directory from the host to the Pod, using a tar buffer."""
        src, dest = Path(src_path), Path(dest_path)

        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:tar") as tar:
            tar.add(src, arcname=dest.joinpath(src.name))
        commands = [buf.getvalue()]

        resp = None
        try:
            resp = kube_stream(
                self._api.connect_get_namespaced_pod_exec,
                self._pod_info.name,
                self._pod_info.namespace,
                command=["tar", "xvf", "-", "-C", "/"],
                tty=False,
                stdin=True,
                stdout=True,
                stderr=True,
                _preload_content=False,
            )
        except KubeApiException as kae:
            yield Cr(err=self._extract_msg_exec_error(kae))
        if not resp:
            return

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stderr():
                yield Cr(err=resp.read_stderr())
            if commands:
                c = commands.pop(0)
                resp.write_stdin(c)
            else:
                break
        resp.close()

        yield Cr(out=f"{src_path} copied to pod successfully!")

    def cp_from_pod(self, src_path: str, dest_path: str) -> Iterator[Cr]:
        """Copy a file/directory from the Pod to the host, using a tar buffer."""
        src, dest = src_path.removeprefix("/"), Path(dest_path)

        with TemporaryFile() as tar_buffer:
            resp = None
            try:
                resp = kube_stream(
                    self._api.connect_get_namespaced_pod_exec,
                    self._pod_info.name,
                    self._pod_info.namespace,
                    command=["tar", "cf", "-", "-C", "/", src],
                    tty=False,
                    stdin=True,
                    stdout=True,
                    stderr=True,
                    _preload_content=False,
                )
            except KubeApiException as kae:
                yield Cr(err=self._extract_msg_exec_error(kae))
            if not resp:
                return

            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    tar_buffer.write(resp.read_stdout().encode("utf-8"))
                if resp.peek_stderr():
                    yield Cr(err=resp.read_stderr())
            resp.close()

            tar_buffer.flush()
            tar_buffer.seek(0)

            with tarfile.open(fileobj=tar_buffer, mode="r:") as tar:
                for member in tar.getmembers():
                    if member.isdir():
                        continue

                    fname = member.name.rsplit("/", 1)[1]
                    tar.makefile(member, dest.joinpath(fname))

        yield Cr(out=f"{src_path} copied to host successfully!")
