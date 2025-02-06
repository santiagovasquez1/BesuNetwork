import asyncio
import logging
import re
from typing import List

import httpx
from clients.kubernate_client import KubernatesClient
from models.pod_information import PodInformation
from models.requests.add_account_blockchain_request import AddAccountToBlockchainRequest
from models.rpc_payload import RpcPayload


class NodesManagerService:
    def __init__(self, kubernates_client: KubernatesClient):
        self.kubernates_client = kubernates_client

    async def _get_node_info(self):
        service_name = await self.kubernates_client.get_service_name("besu-node")
        pods = await self.kubernates_client.list_pods()

        pods_info = [
            PodInformation(
                name=pod.metadata.name,
                dns=f"{pod.metadata.name}.{service_name}.{self.kubernates_client.namespace}.svc.cluster.local",
                ip=pod.status.pod_ip,
            )
            for pod in pods.items
            if re.match(r"besu-node-\d+", pod.metadata.name)
        ]
        logging.info("\n".join([f"{pod.name} - {pod.dns} - {pod.ip}" for pod in pods_info]))
        return pods_info

    async def sync_nodes(self):
        try:
            logging.info("Syncing nodes")
            pods_info = await self._get_node_info()

            logging.info(f"DNS of pods: {pods_info}")

            enode_information_tasks = [
                self._get_enode_information(pod_info) for pod_info in pods_info
            ]

            enodes = await asyncio.gather(*enode_information_tasks)
            logging.info(f"Enodes: {enodes}")

            add_node_to_allowlist_tasks = [
                self._add_node_to_allowlist(pod_info.ip, enodes)
                for pod_info in pods_info
            ]

            await asyncio.gather(*add_node_to_allowlist_tasks)

            add_admin_peer_tasks = []
            for i, pod_info in enumerate(pods_info):
                temp_enodes = enodes[:i] + enodes[i + 1 :]
                for enode in temp_enodes:
                    add_admin_peer_tasks.append(
                        self._add_admin_peer(pod_info.ip, enode)
                    )

            add_admin_peer_results = await asyncio.gather(*add_admin_peer_tasks)

            logging.info(f"Nodes synced: {add_admin_peer_results}")
            return add_admin_peer_results
        except Exception as e:
            logging.error(f"Error syncing nodes: {e}")
            raise e

    async def _get_enode_information(self, pod_info: PodInformation):
        try:
            payload = RpcPayload(
                id=1,
                jsonrpc="2.0",
                method="admin_nodeInfo",
                params=[],
            ).model_dump()
            url = f"http://{pod_info.ip}:8540"
            response = await self._make_request(url, "POST", payload)
            enode = response.get("result").get("enode")
            enode = enode.replace("127.0.0.1", pod_info.ip)
            return enode
        except Exception as e:
            logging.error(f"Error getting node information: {e}")
            raise e

    async def _add_node_to_allowlist(self, node_dns: str, enodes: List[str]):
        try:
            payload = RpcPayload(
                id=1,
                jsonrpc="2.0",
                method="perm_addNodesToAllowlist",
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

    async def _add_admin_peer(self, dns: str, enode: str):
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

    async def add_account_to_blockchain(self, rquest: AddAccountToBlockchainRequest):
        try:
            if not Web3.is_checksum_address(rquest.account_address):
                raise ValueError("Invalid account address")

            pods_info = await self._get_node_info()
            payload = RpcPayload(
                id=1,
                jsonrpc="2.0",
                method="perm_addAccountsToAllowlist",
                params=[[rquest.account_address]],
            ).model_dump()

            add_account_tasks = [
                self._make_request(f"http://{pod_info.dns}:8540", "POST", payload)
                for pod_info in pods_info
            ]

            responses = await asyncio.gather(*add_account_tasks)
            return {
                "responses": responses,
                "account_address": rquest.account_address,
            }
        except Exception as e:
            logging.error(f"Error adding account to blockchain: {e}")
            raise e
