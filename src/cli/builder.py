#################################################
# IMPORTS
#################################################
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from InquirerPy import inquirer  # type: ignore
from InquirerPy.validator import EmptyInputValidator  # type: ignore
from click import Command, Option

from ..utils.cli import clear, confirm
from .custom_group import CustomGroup
from .menu import Menus

#################################################
# CODE
#################################################
dicts = dict[str, Any]


class Builder(CustomGroup):

    no_json: str = "ERROR: Missing JSON file for services. Use 'create' first."
    no_data: str = "ERROR: JSON file is empty. Use 'create' first."
    no_services: str = "ERROR: No services found. Use 'create' first."

    def __init__(self) -> None:
        super().__init__()

    def create(self) -> Command:
        help = "Create all files for the containerization."
        options = [Option(["--network"], type=str, default=None)]

        def callback(network: str | None = None) -> None:
            clear(0)

            services: dict[str, dicts] = {}
            networks: dict[str, str] = {}
            envs: dict[str, dicts] = {}
            service_files: dict[str, dicts] = {}

            if self.cwd.joinpath("data.json").exists():
                exit(
                    "ERROR: data.json already exists, delete it or use another command."
                )

            if not network:
                menu = Menus()
                service, env, service_file = self.__get_data(menu)
                name: str = menu.name  # type: ignore
                services[name] = service
                envs[name] = env
                service_files[name] = service_file

            else:
                networks[network] = network

                menu = Menus(network=network)

                idx = 0
                while True:
                    menu.ports = {}

                    if idx == 0:
                        print("Creating proxy service...")
                    service, env, service_file = self.__get_data(
                        menu, name="proxy" if idx == 0 else None
                    )
                    name: str = menu.name  # type: ignore
                    services[name] = service
                    envs[name] = env
                    service_files[name] = service_file

                    clear(0.5)

                    if idx >= 1 and not confirm(
                        msg=f"Want to continue adding services? (Count: {len(services)})"
                    ):
                        break

                    idx += 1

            services_list = [svc for _, svc in services.items()]
            networks_list = [net for _, net in networks.items()]
            envs_list = [env for _, env in envs.items()]
            service_files_list = [
                svc_file for _, svc_file in service_files.items()
            ]

            clear(0)
            self.file_manager.save_files(
                data={
                    "compose": {
                        "services": services_list,
                        "networks": networks_list,
                    },
                    "envs": envs_list,
                    "service_files": service_files_list,
                }
            )
            clear(0)
            print("Files saved!")

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def update(self) -> Command:
        help = "Update the contents of the containers."
        options = [
            Option(["--service"], type=self.service_type, default=None),
            Option(["--add"], is_flag=True, default=False),
            Option(["--remove"], is_flag=True, default=False),
            Option(["--change"], is_flag=True, default=False),
        ]

        def callback(
            service: str | None = None,
            add: bool = False,
            remove: bool = False,
            change: bool = False,
        ) -> None:
            clear(0)

            if (add and remove) or (add and change) or (remove and change):
                exit("ERROR: You can only use one option flag.")

            path: Path = self.cwd.joinpath("data.json")

            if not path.exists():
                exit(self.no_json)

            data: dicts = self.file_manager.read_json(path) or {}

            if not data:
                exit(self.no_data)

            compose: dicts = data.get("compose", {}) or {}

            services_list: list[dicts] = compose.get("services", []) or []
            networks_list: list[str] = compose.get("networks", []) or []
            envs_list: list[dicts] = data.get("envs", []) or []
            service_files_list: list[dicts] = (
                data.get("service_files", []) or []
            )

            services: dict[Any, dicts] = {
                svc.get("name"): svc for svc in services_list
            }
            networks: dict[str, str] = {net: net for net in networks_list}
            envs: dict[Any, dicts] = {
                env.get("CONTAINER_NAME"): env for env in envs_list
            }
            service_files: dict[Any, dicts] = {
                svc_file.get("name"): svc_file
                for svc_file in service_files_list
            }

            if not services:
                exit(self.no_services)

            def find_index_by_name(name: str) -> int | None:
                for i, s in enumerate(services_list):
                    if s.get("name") == name:
                        return i
                return None

            if remove:
                target = service
                if not target:
                    names = [
                        s.get("name") for s in services_list if s.get("name")
                    ]
                    if not names:
                        exit("ERROR: No services found.")

                    target = inquirer.select(  # type: ignore
                        message="Select a service to remove: ", choices=names
                    ).execute()

                idx = find_index_by_name(target)  # type: ignore
                if idx is None:
                    exit(f"ERROR: Service '{target}' not found.")

                clear(0.5)
                
                if confirm(msg=f"Remove service '{target}'", default=False):
                    services_list.pop(idx)
                    envs_list = [
                        e
                        for e in envs_list
                        if e.get("CONTAINER_NAME") != target
                    ]
                    service_files_list = [
                        f for f in service_files_list if f.get("name") != target
                    ]
                    compose["services"] = services_list
                    compose["networks"] = networks_list
                    data["compose"] = compose
                    data["envs"] = envs_list
                    data["service_files"] = service_files_list
                    self.file_manager.save_files(data)
                    print(f"Service '{target}' removed and files updated.")

            elif add:
                name = service
                if not name:
                    name = self.__get_name("Enter the name of the service: ")
                if find_index_by_name(name):
                    if not confirm(
                        msg=f"Service '{name}' already exists. Overwrite? "
                    ):
                        exit("WARNING: Add cancelled.")

                network = None
                if networks:
                    network = inquirer.select(  # type: ignore
                        message="Select a network: ",
                        choices=networks_list,
                        validate=EmptyInputValidator(),
                    ).execute()
                menu = Menus(network=network)

                service_obj, env_obj, svc_file_obj = self.__get_data(menu, name)
                service_obj["name"] = name
                env_obj["CONTAINER_NAME"] = name
                svc_file_obj["name"] = name

                services[name] = service_obj
                envs[name] = env_obj
                service_files[name] = svc_file_obj

                clear(0.5)

                if confirm(msg=f"Add service '{name}'"):
                    services_list = [svc for _, svc in services.items()]
                    networks_list = [net for _, net in networks.items()]
                    envs_list = [env for _, env in envs.items()]
                    service_files_list = [
                        svc_file for _, svc_file in service_files.items()
                    ]

                    compose["services"] = services_list
                    compose["networks"] = networks_list
                    data["compose"] = compose
                    data["envs"] = envs_list
                    data["service_files"] = service_files_list
                    self.file_manager.save_files(data)
                    print(f"Service '{name}' removed and files updated.")

            elif change:
                name = service
                names = [svc.get("name") for svc in services_list]
                if not name:
                    name = str(
                        inquirer.select(  # type: ignore
                            message="Select the service: ",
                            choices=names,
                            validate=EmptyInputValidator(),
                        ).execute()
                    )
                idx_svc = find_index_by_name(name)
                if idx_svc is None:
                    exit(f"ERROR: Service '{name}' not found.")

                network = None
                if networks:
                    network = inquirer.select(  # type: ignore
                        message="Select a network: ",
                        choices=networks_list,
                        validate=EmptyInputValidator(),
                    ).execute()

                service_obj = services_list[idx_svc]
                env_obj = envs_list[idx_svc]
                svc_file_obj = service_files_list[idx_svc]

                defaults = {
                    "service": service_obj,
                    "env": env_obj,
                    "service_files": svc_file_obj,
                }

                menu = Menus(network=network, defaults=defaults)

                service_obj, env_obj, svc_file_obj = self.__get_data(menu, name)
                service_obj["name"] = name
                env_obj["CONTAINER_NAME"] = name
                svc_file_obj["name"] = name

                services[name] = service_obj
                envs[name] = env_obj
                service_files[name] = svc_file_obj

                clear(0.5)

                if confirm(msg=f"Update service '{name}'"):
                    services_list = [svc for _, svc in services.items()]
                    networks_list = [net for _, net in networks.items()]
                    envs_list = [env for _, env in envs.items()]
                    service_files_list = [
                        svc_file for _, svc_file in service_files.items()
                    ]

                    compose["services"] = services_list
                    compose["networks"] = networks_list
                    data["compose"] = compose
                    data["envs"] = envs_list
                    data["service_files"] = service_files_list
                    self.file_manager.save_files(data)
                    print(f"Service '{name}' removed and files updated.")

            else:
                print("Use --add, --remove or --change flag.")
                print("Use --services [service] for faster output.")
                for s in services:
                    print(f" - {s.get('name')}")

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def build(self) -> Command:
        help = "Build the files for the containerization."
        options: list[Option] = []

        def callback() -> None:
            clear(0)

            path: Path = self.cwd.joinpath("data.json")

            if not path.exists():
                exit(self.no_json)

            data: dicts = self.file_manager.read_json(path) or {}

            if not data:
                exit(self.no_data)

            clear(0)
            self.file_manager.save_files(data, build=True)
            clear(0)
            print("Files saved!")

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def __get_data(
        self, menu: Menus, name: str | None = None
    ) -> tuple[dicts, dicts, dicts]:
        if not name:
            name = self.__get_name(message="Enter the name of the service: ")

        menu.name = name

        service = menu.service()
        env = menu.env()
        service_files = menu.service_files()

        return (service, env, service_files)

    def __get_name(self, message: str) -> str:
        while True:
            clear(0.5)
            name: str = inquirer.text(  # type: ignore
                message=message, validate=EmptyInputValidator()
            ).execute()

            if confirm(
                msg=f"Want to name this service '{name}'? ",
                default=True,
            ):
                break

        return name
