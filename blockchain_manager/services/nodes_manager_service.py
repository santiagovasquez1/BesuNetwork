import logging
import re
from clients.kubernate_client import KubernatesClient


class NodesManagerService:
    def __init__(self, kubernates_client: KubernatesClient):
        self.kubernates_client = kubernates_client

    async def sync_nodes(self):
        try:
            logging.info("Syncing nodes")
            pods = await self.kubernates_client.list_pods()
            pods_names = [
                pod.metadata.name
                for pod in pods.items
                if re.match(r"besu-node-\d+", pod.metadata.name)
            ]

            return {"pod_names": pods_names}
        except Exception as e:
            logging.error(f"Error syncing nodes: {e}")
            raise e
