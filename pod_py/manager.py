from pathlib import Path
from kubernetes.client.api.core_v1_api import CoreV1Api as KubeCoreV1
from kubernetes.config import load_kube_config
from kubernetes.stream import stream as kube_stream

from .utils import Pod, CmdResult


class PodManager:
    def __init__(self, kubeconfig_path: Path, pod: Pod):
        load_kube_config(config_file=kubeconfig_path)
        self._api = KubeCoreV1()
        self._pod = pod
        self._result = CmdResult()

    def deploy(self) -> CmdResult:
        if not self._pod.manifest:
            raise ValueError(
                "Tried to deploy a pod without a manifest, which is not allowed here."
            )

        try:
            self._api.create_namespaced_pod(
                body=self._pod.manifest, namespace=self._pod.namespace
            )
        except:  # catch bad pod schema, pod already exists
            pass  # maybe check if pod is running? probably out of scope

        return self._result

    def exec(self, shell_command: str) -> CmdResult:
        command = ["/bin/bash", "-c", shell_command]

        resp = kube_stream(
            self._api.connect_get_namespaced_pod_exec,
            self._pod.name,
            self._pod.namespace,
            command=command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        
        return self._result

    def ls(self, remote_path: str) -> CmdResult:
        return self.exec(f"ls -lah {remote_path}")

    def cp_to_pod(self, local_path: str, remote_path: str) -> CmdResult:
        ...
        return self._result

    def cp_from_pod(self, remote_path: str, local_path: str) -> CmdResult:
        ...
        return self._result
