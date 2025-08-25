from dataclasses import asdict, dataclass

import uvicorn
import uvicorn.importer

from starconsumers.applications import StarConsumers
from starconsumers.exceptions import StarConsumersCLIException


@dataclass(frozen=True)
class ServerConfiguration:
    host: str
    port: int
    reload: bool
    root_path: str


@dataclass(frozen=True)
class AppConfiguration:
    path: str
    tasks: list[str]


class ApplicationRunner:
    def run(
        self, app_configuration: AppConfiguration, server_configuration: ServerConfiguration
    ) -> None:
        app = uvicorn.importer.import_from_string(app_configuration.path)
        if not isinstance(app, StarConsumers):
            raise StarConsumersCLIException(
                f"The application {app_configuration.path} is not a {StarConsumers} instance"
            )

        app.activate_tasks(app_configuration.tasks)
        uvicorn.run(app=app, lifespan="on", log_level="warning", **asdict(server_configuration))
