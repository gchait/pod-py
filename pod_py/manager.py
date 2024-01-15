"""
The PodManager is the "backend" of the CLI.
All Kubernetes logic sits here, no CLI logic should.
"""

import json
from collections.abc import Iterator
from pathlib import Path

from kubernetes.client.api.core_v1_api import CoreV1Api as KubeCoreV1
from kubernetes.client.exceptions import ApiException as KubeApiException
from kubernetes.config import load_kube_config
from kubernetes.stream import stream as kube_stream

from .utils import CommandResult as CR
from .utils import PodInfo
import io
import tarfile
from tempfile import TemporaryFile


class PodManager:
    def __init__(self, kubeconfig: Path, pod_info: PodInfo):
        load_kube_config(config_file=kubeconfig)
        self._api = KubeCoreV1()
        self._pod_info = pod_info

    def deploy(self) -> Iterator[CR]:
        try:
            self._api.create_namespaced_pod(
                body=self._pod_info.manifest, namespace=self._pod_info.namespace
            )

        except KubeApiException as kae:
            msg = "Creation failed."
            if kae.body:
                msg = json.loads(kae.body).get("message", msg)
            yield CR(err=msg)

        yield CR(out=f"{self._pod_info} created successfully!")

    def execute(self, command: str) -> Iterator[CR]:
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
            yield CR(out=resp)

        except KubeApiException as kae:
            msg = "Command execution failed."
            if kae.reason:
                msg = kae.reason.split(" -+-+- ")[-1]
            yield CR(err=msg)

    def ls(self, directory: str) -> Iterator[CR]:
        return self.execute(f"ls -lah {directory}")

    def cp_to_pod(self, src_path: str, dest_path: str) -> Iterator[CR]:
        src, dest = Path(src_path), Path(dest_path)

        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:tar") as tar:
            tar.add(src, arcname=dest.joinpath(src.name))
        commands = [buf.getvalue()]

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

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                yield CR(out=f"STDOUT: {resp.read_stdout()}")
            if resp.peek_stderr():
                yield CR(out=f"STDERR: {resp.read_stderr()}")
            if commands:
                c = commands.pop(0)
                resp.write_stdin(c)
            else:
                break
        resp.close()

        yield CR(out=f"File {src_path} copied to pod successfully!")

    def cp_from_pod(self, src_path: str, dest_path: str) -> Iterator[CR]:
        src, dest = src_path.removeprefix("/"), Path(dest_path)

        with TemporaryFile() as tar_buffer:
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

            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    tar_buffer.write(resp.read_stdout().encode("utf-8"))
                if resp.peek_stderr():
                    yield CR(err=resp.read_stderr())
            resp.close()

            tar_buffer.flush()
            tar_buffer.seek(0)

            with tarfile.open(fileobj=tar_buffer, mode="r:") as tar:
                for member in tar.getmembers():
                    if member.isdir():
                        continue

                    fname = member.name.rsplit("/", 1)[1]
                    tar.makefile(member, dest.joinpath(fname))

        yield CR(out=f"File {src_path} copied to host successfully!")
