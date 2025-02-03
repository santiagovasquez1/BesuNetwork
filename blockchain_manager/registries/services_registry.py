from global_pydependency.base_service_registry import (
    BaseServiceRegistry,
    register_service,
)
from global_pydependency.dependency_injector import DependencyContainer
from services.nodes_manager_service import NodesManagerService


class ServiceRegistry(BaseServiceRegistry):
    def __init__(self, container: DependencyContainer):
        self.container = container
        super().__init__()

    @register_service
    def register_services(self):
        self.container.add_singleton(NodesManagerService)
