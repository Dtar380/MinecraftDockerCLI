#################################################
# IMPORTS
#################################################
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from InquirerPy import inquirer  # type: ignore
from InquirerPy.validator import EmptyInputValidator  # type: ignore
from importlib_resources import files  # type: ignore
import psutil  # type: ignore

from ..utils.cli import clear, confirm


#################################################
# CODE
#################################################
class Menus:

    def __init__(
        self, network: str | None = None, update: bool = False
    ) -> None:
        self.network = network
        self.update = update

        self.cpus: float = psutil.cpu_count(logical=True) or 0
        self.memory: int = (
            psutil.virtual_memory().available // 1024**2 - 512 or 0
        )

        self.ports: dict[str, int] = {}
        self.resources: dict[str, Any] = {}

        if self.memory < 512:
            print("WARNING: RAM AMOUNT TOO LOW")
        clear(1)

    # Construct service contents for docker-compose
    def service(self, name: str) -> dict[str, Any]:
        self.__get_ports()
        expose = self.__expose()
        ports = [
            f"{port}:{port}"
            for name, port in self.ports.items()
            if name not in expose
        ]
        exposed = [self.ports[name] for name in expose]

        self.__resources()
        resources = deepcopy(self.resources)
        resources["limits"]["memory"] = (
            str(resources["limits"]["memory"] / 1024) + "g"
        )
        resources["reservations"]["memory"] = (
            str(resources["reservations"]["memory"] / 1024) + "g"
        )

        service: dict[str, Any] = {
            "name": name,
            "build": {"context": f"./servers/{name}/"},
            "env_file": f"./servers/{name}/.env",
            "working_dir": f"/{name}",
        }

        if ports:
            service["ports"] = ports
        if expose:
            service["expose"] = exposed
        if self.network:
            service["networks"] = [self.network]
        if resources:
            service["resources"] = resources

        return service

    def __get_ports(self) -> None:
        while True:
            clear(0.5)

            port_name = inquirer.text(  # type: ignore
                message="Add a name for the port: ",
                validate=EmptyInputValidator(),
            ).execute()

            port = inquirer.number(  # type: ignore
                message="Add port number: ",
                min_allowed=1,
                max_allowed=2**16 - 1,
                default=25565,
                validate=EmptyInputValidator(),
            ).execute()

            if confirm(
                msg=f"Want to add {port_name} assigned to port {port}? "
            ):
                self.ports[port_name] = port

                if not confirm(msg="Want to add more ports? ", default=False):
                    return None

    def __expose(self) -> list[str]:
        clear(0.5)

        expose: list[str] = []
        for name, port in self.ports.items():

            if confirm(
                msg=f"Want to expose {name} assigned to {port}? ", default=False
            ):
                expose.append(name)

        return expose

    def __resources(self) -> None:
        while True:
            clear(0.5)

            cpus_limit: float = float(
                inquirer.number(  # type: ignore
                    message="Select a limit of CPUs for this service: ",
                    min_allowed=0,
                    max_allowed=self.cpus,
                    float_allowed=True,
                    validate=EmptyInputValidator(),
                ).execute()
            )
            cpus_reservation: float = float(
                inquirer.number(  # type: ignore
                    message="Select a CPUs allocation for this service: ",
                    min_allowed=0,
                    max_allowed=cpus_limit,
                    float_allowed=True,
                    validate=EmptyInputValidator(),
                ).execute()
            )

            memory_limit: int = int(
                inquirer.number(  # type: ignore
                    message="Select a limit of RAM for this service (in MB): ",
                    min_allowed=0,
                    max_allowed=self.memory,
                    float_allowed=False,
                    validate=EmptyInputValidator(),
                ).execute()
            )
            memory_reservation: int = int(
                inquirer.number(  # type: ignore
                    message="Select a RAM allocation for this service (in MB): ",
                    min_allowed=0,
                    max_allowed=memory_limit,
                    float_allowed=False,
                    validate=EmptyInputValidator(),
                ).execute()
            )

            if confirm(
                msg="Confirm the RAM and CPU allocation for this service."
            ):
                break

        self.cpus -= cpus_limit
        self.memory -= memory_limit

        self.resources = {
            "limits": {"cpus": cpus_limit, "memory": memory_limit},
            "reservations": {
                "cpus": cpus_reservation,
                "memory": memory_reservation,
            },
        }

    # Construct env file contents
    def env(self, name: str) -> dict[str, Any]:
        heaps = self.__get_heaps()

        return {
            "CONTAINER_NAME": name,
            "SEVER_JAR": self.__get_jar(name),
            "JAVA_ARGS": self.__use_args(),
            "MIN_HEAP_SIZE": heaps[0],
            "MAX_HEAP_SIZE": heaps[1],
            "HOST_PORTS": self.ports,
        }

    def __get_jar(self, name: str) -> str:
        while True:
            clear(0.5)

            default = "proxy" if "proxy" in name else "server"
            jar: str = inquirer.text(  # type: ignore
                message="Enter your .jar file name: ",
                default=f"{default}.jar",
                validate=EmptyInputValidator(),
            ).execute()

            if confirm(msg=f"Confirm your jar file is {jar}"):
                break

        return jar

    def __use_args(self) -> str | None:
        clear(0.5)

        if confirm(msg="Want to use recommended args for the server? "):
            txt_file = Path(files("src.assets.config").joinpath("recommended-args.txt"))  # type: ignore
            with open(txt_file, "r+") as f:  # type: ignore
                data = f.readlines()
            return " ".join(data).replace("\n", "")
        return None

    def __get_heaps(self) -> list[str]:
        while True:
            clear(0.5)

            min_heap_size: int = int(
                inquirer.number(  # type: ignore
                    message="Select the minimum heap size: ",
                    min_allowed=self.resources["reservations"]["memory"],
                    max_allowed=self.resources["limits"]["memory"],
                    float_allowed=False,
                    default=self.resources["reservations"]["memory"],
                    validate=EmptyInputValidator(),
                ).execute()
            )

            max_heap_size: int = int(
                inquirer.number(  # type: ignore
                    message="Select the maximum heap size: ",
                    min_allowed=min_heap_size,
                    max_allowed=self.resources["limits"]["memory"],
                    float_allowed=False,
                    default=self.resources["limits"]["memory"],
                    validate=EmptyInputValidator(),
                ).execute()
            )

            if confirm(msg="Confirm Heap allocations"):
                break

        return [f"{min_heap_size}M", f"{max_heap_size}M"]
