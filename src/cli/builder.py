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

    no_json: str = "ERROR: Missing JSON file for servers. Use 'create' first."
    no_data: str = "ERROR: JSON file is empty. Use 'create' first."
    no_servers: str = "ERROR: No servers found. Use 'create' first."

    def __init__(self) -> None:
        super().__init__()
        self.compose_manager.sleep = 2
        self.file_manager.sleep = 2

    def create(self) -> Command:
        help = "Create all files for the containerization."
        options = [Option(["--network"], is_flag=True, default=False)]

        def callback(network: bool = False) -> None:
            clear(0)

            servers: dict[str, dicts] = {}
            database: dict[str, str] = {}
            web: bool = False
            envs: dict[str, dicts] = {}
            server_files: dict[str, dicts] = {}

            if self.cwd.joinpath("data.json").exists():
                exit(
                    "ERROR: data.json already exists, delete it or use another command."
                )

            menu = Menus()

            if not network:
                server, env, server_file = self.__get_data(menu)
                name: str = menu.name  # type: ignore
                servers[name] = server
                envs[name] = env
                server_files[name] = server_file
            else:
                idx = 0
                while True:
                    menu.ports = {}

                    if idx == 0:
                        print("Creating proxy server...")
                    server, env, server_file = self.__get_data(
                        menu, name="proxy" if idx == 0 else None
                    )
                    name: str = menu.name  # type: ignore
                    servers[name] = server
                    envs[name] = env
                    server_files[name] = server_file

                    clear(0.5)

                    if idx >= 1 and not confirm(  # type: ignore
                        msg=f"Want to continue adding servers? (Count: {len(servers)})",
                    ):
                        break

                    idx += 1

                if confirm(msg="Want to use a sql database?"):
                    database = menu.database()

                if confirm(msg="Want to add a web server?"):
                    web = True

            servers_list = [svc for _, svc in servers.items()]
            envs_list = [env for _, env in envs.items()]
            server_files_list = [
                svc_file for _, svc_file in server_files.items()
            ]

            clear(0)
            self.file_manager.save_files(
                data={
                    "compose": {
                        "servers": servers_list,
                        "database": database,
                        "web": web,
                    },
                    "envs": envs_list,
                    "server_files": server_files_list,
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
            Option(["--server"], type=self.server_type, default=None),
            Option(["--add"], is_flag=True, default=False),
            Option(["--remove"], is_flag=True, default=False),
            Option(["--change"], is_flag=True, default=False),
            Option(["--database"], is_flag=True, default=False),
            Option(["--web"], is_flag=True, default=False),
        ]

        def callback(
            server: str | None = None,
            add: bool = False,
            remove: bool = False,
            change: bool = False,
            database: bool = False,
            web: bool = False,
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

            servers_list: list[dicts] = compose.get("servers", []) or []
            envs_list: list[dicts] = data.get("envs", []) or []
            server_files_list: list[dicts] = data.get("server_files", []) or []

            servers: dict[Any, dicts] = {
                svc.get("name"): svc for svc in servers_list
            }
            envs: dict[Any, dicts] = {
                env.get("CONTAINER_NAME"): env for env in envs_list
            }
            server_files: dict[Any, dicts] = {
                svc_file.get("name"): svc_file for svc_file in server_files_list
            }

            if not servers:
                exit(self.no_servers)

            def find_index_by_name(name: str) -> int | None:
                for i, s in enumerate(servers_list):
                    if s.get("name") == name:
                        return i
                return None

            if remove:
                target = server
                if not target:
                    names = [
                        s.get("name") for s in servers_list if s.get("name")
                    ]
                    if not names:
                        exit("ERROR: No servers found.")

                    target = inquirer.select(  # type: ignore
                        message="Select a server to remove: ", choices=names
                    ).execute()

                idx = find_index_by_name(target)  # type: ignore
                if idx is None:
                    exit(f"ERROR: server '{target}' not found.")

                clear(0.5)

                if confirm(msg=f"Remove server '{target}'", default=False):
                    servers_list.pop(idx)
                    envs_list = [
                        e
                        for e in envs_list
                        if e.get("CONTAINER_NAME") != target
                    ]
                    server_files_list = [
                        f for f in server_files_list if f.get("name") != target
                    ]
                    compose["servers"] = servers_list
                    data["compose"] = compose
                    data["envs"] = envs_list
                    data["server_files"] = server_files_list
                    self.file_manager.save_files(data)
                    print(f"server '{target}' removed and files updated.")

            elif add:
                name = server
                if not name:
                    name = self.__get_name("Enter the name of the server: ")
                if find_index_by_name(name):
                    if not confirm(
                        msg=f"server '{name}' already exists. Overwrite? "
                    ):
                        exit("WARNING: Add cancelled.")

                menu = Menus()

                server_obj, env_obj, svc_file_obj = self.__get_data(menu, name)
                server_obj["name"] = name
                env_obj["CONTAINER_NAME"] = name
                svc_file_obj["name"] = name

                servers[name] = server_obj
                envs[name] = env_obj
                server_files[name] = svc_file_obj

                clear(0.5)

                if confirm(msg=f"Add server '{name}'"):
                    servers_list = [svc for _, svc in servers.items()]
                    envs_list = [env for _, env in envs.items()]
                    server_files_list = [
                        svc_file for _, svc_file in server_files.items()
                    ]

                    compose["servers"] = servers_list
                    data["compose"] = compose
                    data["envs"] = envs_list
                    data["server_files"] = server_files_list
                    self.file_manager.save_files(data)
                    print(f"server '{name}' removed and files updated.")

            elif change:
                name = server
                names = [svc.get("name") for svc in servers_list]
                if not name:
                    name = str(
                        inquirer.select(  # type: ignore
                            message="Select the server: ",
                            choices=names,
                            validate=EmptyInputValidator(),
                        ).execute()
                    )
                idx_svc = find_index_by_name(name)
                if idx_svc is None:
                    exit(f"ERROR: server '{name}' not found.")

                server_obj = servers_list[idx_svc]
                env_obj = envs_list[idx_svc]
                svc_file_obj = server_files_list[idx_svc]

                defaults = {
                    "server": server_obj,
                    "env": env_obj,
                    "server_files": svc_file_obj,
                }

                menu = Menus(defaults=defaults)

                server_obj, env_obj, svc_file_obj = self.__get_data(menu, name)
                server_obj["name"] = name
                env_obj["CONTAINER_NAME"] = name
                svc_file_obj["name"] = name

                servers[name] = server_obj
                envs[name] = env_obj
                server_files[name] = svc_file_obj

                clear(0.5)

                if confirm(msg=f"Update server '{name}'"):
                    servers_list = [svc for _, svc in servers.items()]
                    envs_list = [env for _, env in envs.items()]
                    server_files_list = [
                        svc_file for _, svc_file in server_files.items()
                    ]

                    compose["servers"] = servers_list
                    data["compose"] = compose
                    data["envs"] = envs_list
                    data["server_files"] = server_files_list
                    self.file_manager.save_files(data)
                    print(f"server '{name}' removed and files updated.")

            elif database:
                current: dict[str, str] = compose.get("database", {}) or {}
                defaults = (
                    None
                    if current == {}
                    else {"database": current}  # type: ignore
                )
                menu = Menus(defaults=defaults)
                db = menu.database()
                if confirm(msg="Update database?"):
                    compose["database"] = db
                    data["compose"] = compose
                    self.file_manager.save_files(data)
                    print("Database was updated.")

            elif web:
                current = compose.get("web", False)
                if confirm(msg="Update web status?"):
                    compose["web"] = not current
                    data["compose"] = compose
                    self.file_manager.save_files(data)
                    print("Web status was changed.")

            else:
                print(
                    "Use --add, --remove, --change, --web or --database flag."
                )
                print("Use --servers [server] for faster output.")
                for s in servers:
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
            name = self.__get_name(message="Enter the name of the server: ").lower()

        menu.name = name

        server = menu.server()
        env = menu.env()
        server_files = menu.server_files()

        return (server, env, server_files)

    def __get_name(self, message: str) -> str:
        while True:
            clear(0.5)
            name: str = inquirer.text(  # type: ignore
                message=message, validate=EmptyInputValidator()
            ).execute()

            if confirm(
                msg=f"Want to name this server '{name}'? ",
                default=True,
            ):
                break

        return name
