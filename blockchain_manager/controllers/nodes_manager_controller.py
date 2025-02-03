import logging

from global_pydependency.base_controller import BaseController
from starlette.responses import JSONResponse

from services.nodes_manager_service import NodesManagerService


class NodeManagerController(BaseController):
    PATH = "/nodes"

    def __init__(self, container, router):
        super().__init__(container, router)
        self.node_service: NodesManagerService = self.container.get_service(NodesManagerService)

    def register_routes(self):
        self.router.add_api_route(
            path=f"{self.PATH}/sync_nodes",
            endpoint=self.sync_nodes,
            methods=["POST"]
        )

    async def sync_nodes(self):
        try:
            nodes = await self.node_service.sync_nodes()
            return JSONResponse(content={"nodes": nodes})
        except Exception as e:
            logging.error(f"Error syncing nodes: {e}")
            return JSONResponse(status_code=500, content={"error": f"Error syncing nodes: {e}"})
