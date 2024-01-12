from kubernetes.config import load_kube_config
from kubernetes.client.api.core_v1_api import CoreV1Api as KubeCoreV1
from kubernetes.stream import stream as kube_stream
from os import PathLike
import yaml


class PodManager:
    def __init__(self, kubeconfig_path: PathLike, pod: Pod):
        load_kube_config(config_file=kubeconfig_path)
        self._api = KubeCoreV1()
        self._pod = pod

    def deploy(self, pod_yaml: str):
        pod_manifest = yaml.safe_load(pod_yaml)
        namespace = pod_manifest["metadata"].get("namespace", "default")
        self._api.create_namespaced_pod(body=pod_manifest, namespace=namespace)

    def exec(self, shell_command: str) -> tuple[int, str, str]:
        command = ["/bin/bash", "-c", shell_command]

        resp = kube_stream(
            self._api.connect_get_namespaced_pod_exec,
            self._name,
            self._namespace,
            command=command,
            stderr=True, stdin=False,
            stdout=True, tty=False,
        )
        print(resp)
        return 0, "", ""

    def ls(self, remote_path: str):
        return self.exec(f"ls -lah {remote_path}")

    def cp_to_pod(self, local_path: str, remote_path: str):
        ...

    def cp_from_pod(self, remote_path: str, local_path: str):
        ...
