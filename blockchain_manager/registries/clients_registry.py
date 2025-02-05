import logging
from global_pydependency.base_service_registry import (
    BaseServiceRegistry,
    register_service,
)
from global_pydependency.dependency_injector import DependencyContainer
from global_pydependency.configuration import Configuration
from clients.kubernate_client import KubernatesClient


class ClientsRegistry(BaseServiceRegistry):
    def __init__(self, container: DependencyContainer):
        self.container = container
        super().__init__()

    @register_service
    def register_clients(self):
        self.container.add_singleton(Configuration)

        config = self.container.get_service(Configuration)
        namespace = config.get("K8S_NAMESPACE","besu-network")
        logging.info(f"Using namespace: {namespace}")
        self.container.add_singleton(
            KubernatesClient,
            lambda: KubernatesClient(
                self.container.get_service(Configuration), namespace
            ),
        )
