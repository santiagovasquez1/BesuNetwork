import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from dotenv import load_dotenv

from global_pydependency.dependency_injector import DependencyContainer
from global_pydependency.controller_registry import ControllersRegistry
from registries.registry_manager import RegistryManager

load_dotenv()

logging.basicConfig(level=logging.INFO, force=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Aquí puedes agregar cualquier inicialización adicional si lo necesitas.
    yield
    # Shutdown: Se ejecuta al finalizar el ciclo de vida de la aplicación.
    container = app.state.container
    if container:
        try:
            await container.shutdown()
            logging.info("Container shutdown successfully.")
        except Exception as e:
            logging.error(f"Error during container shutdown: {e}")
            raise e


def create_app() -> FastAPI:
    logging.info("Setting up FastAPI app")
    # Asigna el lifespan handler al crear la aplicación.
    app = FastAPI(lifespan=lifespan)
    router = APIRouter()

    # Crear y configurar el contenedor de dependencias.
    container = DependencyContainer()
    RegistryManager.create_registry(container)
    ControllersRegistry.create(
        container=container,
        router=router,
        package="controllers",
    )

    app.include_router(router)
    # Guarda el contenedor en el estado de la aplicación para accederlo luego en el lifespan.
    app.state.container = container

    logging.info("FastAPI app setup complete")
    return app


app = create_app()


@app.get("/health_check")
async def health_check():
    return {"status": "ok"}
