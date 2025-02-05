import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from global_pydependency.configuration import Configuration
from kubernetes import client, config


class KubernatesClient:
    def __init__(self, config: Configuration, namespace: str):
        self.config = config
        self.namespace = namespace
        self.client = self.get_api_instance()

    def load_kube_config(self):
        try:
            logging.info("Trying to load kube config from incluster")
            config.load_incluster_config()
            logging.info("Connection sucess from incluster")
        except Exception:
            try:
                config.load_kube_config(config_file=self.config.get("KUBE_CONFIG_FILE"))
            except Exception as e:
                logging.error(f"Error loading kube config: {e}")
                raise e

    def get_api_instance(self) -> client.CoreV1Api:
        self.load_kube_config()
        return client.CoreV1Api()

    async def list_pods(self):
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, self.client.list_namespaced_pod, self.namespace)
        return result
