#################################################
# IMPORTS
#################################################
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from InquirerPy import inquirer  # type: ignore
from InquirerPy.base.control import Choice  # type: ignore
from InquirerPy.validator import (  # type: ignore
    EmptyInputValidator,
    PasswordValidator,
)
from importlib_resources import files  # type: ignore
import psutil  # type: ignore

from ..utils.cli import clear, confirm


#################################################
# CODE
#################################################
class Menus:

    def __init__(
        self,
        update: bool = False,
        defaults: dict[str, Any] | None = None,
    ) -> None:
        self.update = update
        self.defaults = defaults

        self.cpus: float = psutil.cpu_count(logical=True) or 0
        self.memory: int = (
            psutil.virtual_memory().available // 1024**2 - 512 or 0
        )

        self.ports: dict[str, int] = {}
        self.resources: dict[str, Any] = {}

        if self.memory < 512:
            print("WARNING: RAM AMOUNT TOO LOW")
        clear(1)

        self.jar_file: str | None
        self.name: str = ""

    # Construct server contents for docker-compose
    def server(self) -> dict[str, Any]:
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

        server: dict[str, Any] = {
            "name": self.name,
            "build": {"context": f"./servers/{self.name}/"},
            "env_file": f"./servers/{self.name}/.env",
            "working_dir": f"/{self.name}",
        }

        if ports:
            server["ports"] = ports
        if expose:
            server["expose"] = exposed
        if resources:
            server["resources"] = resources

        return server

    def __get_ports(self) -> None:
        index = 0
        while True:
            clear(0.5)

            if self.defaults:
                port_default = int(
                    list(self.defaults["env"]["HOST_PORTS"].values())[index]
                )
                name_default = str(
                    list(self.defaults["env"]["HOST_PORTS"].keys())[index]
                )
            else:
                port_default: int | None = 25565 if index == 0 else None  # type: ignore
                name_default: str | None = "HOST" if index == 0 else None  # type: ignore

            port_name = inquirer.text(  # type: ignore
                message="Add a name for the port: ",
                default=name_default,
                validate=EmptyInputValidator(),
            ).execute()

            port = inquirer.number(  # type: ignore
                message="Add port number: ",
                min_allowed=1,
                max_allowed=2**16 - 1,
                default=port_default,
                validate=EmptyInputValidator(),
            ).execute()

            if confirm(
                msg=f"Want to add {port_name} assigned to port {port}? "
            ):
                self.ports[port_name] = port
                index += 1

            if index >= 1 and not confirm(
                msg="Want to add more ports? ", default=False
            ):
                return None

    def __expose(self) -> list[str]:
        clear(0.5)

        expose: list[str] = []
        for name, port in self.ports.items():
            if confirm(
                msg=f"Want to expose {name} assigned to {port}? ",
                default=False if "proxy" in self.name else True,
            ):
                expose.append(name)

        return expose

    def __resources(self) -> None:
        while True:
            clear(0.5)

            if self.defaults:
                resources = self.defaults["server"]["resources"]
                def_cpus_limit = float(resources["limits"]["cpus"])
                def_cpus_reservation = float(resources["reservations"]["cpus"])
                def_memory_limit = int(
                    float(resources["limits"]["memory"].removesuffix("g"))
                    * 1024
                )
                def_memory_reservation = int(
                    float(resources["reservations"]["memory"].removesuffix("g"))
                    * 1024
                )
            else:
                def_cpus_limit = 1
                def_cpus_reservation = 0
                def_memory_limit = 1024
                def_memory_reservation = 256

            cpus_limit: float = float(
                inquirer.number(  # type: ignore
                    message="Select a limit of CPUs for this server: ",
                    min_allowed=0,
                    max_allowed=self.cpus,
                    float_allowed=True,
                    default=def_cpus_limit,
                    validate=EmptyInputValidator(),
                ).execute()
            )
            cpus_reservation: float = float(
                inquirer.number(  # type: ignore
                    message="Select a CPUs allocation for this server: ",
                    min_allowed=0,
                    max_allowed=cpus_limit,
                    float_allowed=True,
                    default=def_cpus_reservation,
                    validate=EmptyInputValidator(),
                ).execute()
            )

            memory_limit: int = int(
                inquirer.number(  # type: ignore
                    message="Select a limit of RAM for this server (in MB): ",
                    min_allowed=0,
                    max_allowed=self.memory,
                    float_allowed=False,
                    default=def_memory_limit,
                    validate=EmptyInputValidator(),
                ).execute()
            )
            memory_reservation: int = int(
                inquirer.number(  # type: ignore
                    message="Select a RAM allocation for this server (in MB): ",
                    min_allowed=0,
                    max_allowed=memory_limit,
                    float_allowed=False,
                    default=def_memory_reservation,
                    validate=EmptyInputValidator(),
                ).execute()
            )

            if confirm(
                msg="Confirm the RAM and CPU allocation for this server."
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
    def env(self) -> dict[str, Any]:
        heaps = self.__get_heaps()
        if self.defaults:
            self.jar_file = self.defaults["env"]["SERVER_JAR"]
        else:
            self.jar_file = self.__get_jar()
        args = self.__use_args() or ""

        return {
            "CONTAINER_NAME": self.name,
            "SERVER_JAR": self.jar_file,
            "JAVA_ARGS": args,
            "MIN_HEAP_SIZE": heaps[0],
            "MAX_HEAP_SIZE": heaps[1],
            "HOST_PORTS": self.ports,
        }

    def __get_jar(self) -> str:
        while True:
            clear(0.5)

            default = "proxy" if "proxy" in self.name.lower() else "server"
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

        if confirm(
            msg="Want to use recommended args for the server? ",
            default=False if "proxy" in self.name else True,
        ):
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

    def server_files(self) -> dict[str, Any]:
        type = self.__get_server_type()

        files: dict[str, Any] = {
            "name": self.name,
            "server": {
                "jar_file": self.jar_file,
                "type": type,
                "version": self.__get_version(type),
            },
        }

        return files

    def __get_server_type(self) -> str:
        choices = (
            ["folia", "paper"]
            if "proxy" not in self.name.lower()
            else ["velocity"]
        )
        return inquirer.select(  # type: ignore
            message="Choose server type: ",
            choices=choices,
            validate=EmptyInputValidator(),
        ).execute()

    def __get_version(self, type: str) -> str | None:
        import requests  # type: ignore

        response = requests.get(f"https://fill.papermc.io/v3/projects/{type}")
        json_response = response.json()
        versions: dict[str, list[str]] = json_response.get("versions", {}) or {}
        choices: list[Any] = [Choice(value=None, name="Latest")]
        for version in versions.values():
            choices.extend(version)

        return inquirer.select(  # type: ignore
            message="Select the version: ", choices=choices
        ).execute()

    def database(self) -> dict[str, str]:
        db: dict[str, str] = {}
        if self.defaults:
            db = self.defaults.get("database", {})
        user = db.get("user", "")
        password = db.get("password", "")
        name = db.get("db", "")

        return {
            "user": self.__get_name("Enter a username: ", user),
            "password": self.__get_password(password),
            "db": self.__get_name("Enter a name for the database: ", name),
        }

    def __get_name(self, msg: str, default: str = "") -> str:
        while True:
            clear(0.5)

            name = str(
                inquirer.text(  # type: ignore
                    message=msg, default=default, validate=EmptyInputValidator()
                ).execute()
            )

            if confirm(msg="Confirm your input: "):
                return name

    def __get_password(self, default: str = "") -> str:
        clear(0.5)
        password = str(
            inquirer.secret(  # type: ignore
                message="Enter your database password: ",
                default=default,
                validate=PasswordValidator(
                    length=8,
                    cap=True,
                    number=True,
                    message="Password must have 8+ characters, caps and numbers.",
                ),
            ).execute()
        )

        return password
