import json
from collections.abc import Iterator
from pathlib import Path

from kubernetes.client.api.core_v1_api import CoreV1Api as KubeCoreV1
from kubernetes.client.exceptions import ApiException as KubeApiException
from kubernetes.config import load_kube_config
from kubernetes.stream import stream as kube_stream

from .utils import CommandResult as CR
from .utils import PodInfo


class PodManager:
    def __init__(self, kubeconfig_path: Path, pod_info: PodInfo):
        load_kube_config(config_file=kubeconfig_path)
        self._api = KubeCoreV1()
        self._pod_info = pod_info

    def deploy(self) -> Iterator[CR]:
        if not self._pod_info.manifest:
            raise ValueError(
                "Tried to deploy a pod without a manifest, which is not allowed here."
            )

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

    def execute(self, shell_command: str) -> Iterator[CR]:
        command = ["/bin/bash", "-c", shell_command]

        _ = kube_stream(
            self._api.connect_get_namespaced_pod_exec,
            self._pod_info.name,
            self._pod_info.namespace,
            command=command,
            tty=False,
            stdin=False,
            stdout=True,
            stderr=True,
        )

        yield CR()

    def ls(self, remote_path: str) -> Iterator[CR]:
        return self.execute(f"ls -lah {remote_path}")

    def cp_to_pod(self, local_path: str, remote_path: str) -> Iterator[CR]:
        ...
        yield CR()

    def cp_from_pod(self, remote_path: str, local_path: str) -> Iterator[CR]:
        ...
        yield CR()
