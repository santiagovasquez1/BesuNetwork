import asyncio
import logging
import re
from typing import List

import httpx
from clients.kubernate_client import KubernatesClient
from models.rpc_payload import RpcPayload


class NodesManagerService:
    def __init__(self, kubernates_client: KubernatesClient):
        self.kubernates_client = kubernates_client

    async def sync_nodes(self):
        try:
            logging.info("Syncing nodes")
            service_name = await self.kubernates_client.get_service_name("besu-node")
            pods = await self.kubernates_client.list_pods()

            pods_dns = [
                f"{pod.metadata.name}.{service_name}.{self.kubernates_client.namespace}.svc.cluster.local"
                for pod in pods.items
                if re.match(r"besu-node-\d+", pod.metadata.name)
            ]

            logging.info(f"DNS of pods: {pods_dns}")

            enode_information_tasks = [
                self._get_enode_information(node_dns) for node_dns in pods_dns
            ]

            enodes = await asyncio.gather(*enode_information_tasks)
            logging.info(f"Enodes: {enodes}")

            add_node_to_allowlist_tasks = [
                self._add_node_to_allowlist(node_dns, enodes) for node_dns in pods_dns
            ]

            await asyncio.gather(*add_node_to_allowlist_tasks)

            add_admin_peer_tasks = []
            for i, node_dns in enumerate(pods_dns):
                temp_enodes = enodes[:i] + enodes[i + 1 :]
                for enode in temp_enodes:                    
                    add_admin_peer_tasks.append(self._add_admin_peer(node_dns, enode))

            add_admin_peer_results = await asyncio.gather(*add_admin_peer_tasks)

            logging.info(f"Nodes synced: {add_admin_peer_results}")
            return add_admin_peer_results
        except Exception as e:
            logging.error(f"Error syncing nodes: {e}")
            raise e

    async def _get_enode_information(self, node_dns: str):
        try:
            payload = RpcPayload(
                id=1,
                jsonrpc="2.0",
                method="admin_nodeInfo",
                params=[],
            ).model_dump()
            url = f"http://{node_dns}:8540"
            response = await self._make_request(url, "POST", payload)
            enode = response.get("result").get("enode")
            enode = enode.replace("127.0.0.1", node_dns)
            return enode
        except Exception as e:
            logging.error(f"Error getting node information: {e}")
            raise e

    async def _add_node_to_allowlist(self, node_dns: str, enodes: List[str]):
        try:
            payload = RpcPayload(
                id=1,
                jsonrpc="2.0",
                method="admin_addPeer",
                params=[enodes],
            ).model_dump()

            url = f"http://{node_dns}:8540"
            logging.info(f"Adding node to allowlist: {node_dns}")
            response = await self._make_request(url, "POST", payload)
            logging.info(f"Node added to allowlist: {node_dns}")
            return response.get("result")
        except Exception as e:
            logging.error(f"Error adding node to allowlist: {e}")
            raise e

    async def _add_admin_peer(self, dns: str, enode:str):
        try:

            
            payload = RpcPayload(
                id=1,
                jsonrpc="2.0",
                method="admin_addPeer",
                params=[enode],
            ).model_dump()

            url = f"http://{dns}:8540"
            logging.info(f"Adding node to allowlist: {dns}")
            response = await self._make_request(url, "POST", payload)
            logging.info(f"Node added to allowlist: {dns}")
            return response.get("result")
        except Exception as e:
            logging.error(f"Error adding node to allowlist: {e}")
            raise e

    async def _make_request(self, url: str, methd: str, payload: dict) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(methd, url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logging.error(f"Error getting node information: {e}")
            raise e
