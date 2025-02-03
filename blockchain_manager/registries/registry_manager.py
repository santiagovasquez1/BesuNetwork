import importlib
import inspect
import logging
import os
from pathlib import Path
import pkgutil
from global_pydependency.base_service_registry import BaseServiceRegistry
from global_pydependency.dependency_injector import DependencyContainer


class RegistryManager:

    def __init__(self, container: DependencyContainer):
        self.container = container
        self.registered_services = []

    @staticmethod
    def create_registry(container: DependencyContainer):
        registry = RegistryManager(container)
        registry.register_services()
        return registry

    def register_services(self):
        registry_dir = os.path.dirname(__file__)
        relative_module = (
            Path(registry_dir)
            .relative_to(Path(registry_dir).parent)
            .as_posix()
            .replace("/", ".")
        )

        for _, module_name, is_pkg in pkgutil.iter_modules([registry_dir]):
            if not is_pkg:
                module = importlib.import_module(f"{relative_module}.{module_name}")
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(cls, BaseServiceRegistry)
                        and cls != BaseServiceRegistry
                    ):
                        instance = cls(self.container)
                        self.registered_services.append(instance)
                        logging.info(f"Registered services from {cls.__name__}")
