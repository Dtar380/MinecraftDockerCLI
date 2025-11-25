#################################################
# IMPORTS
#################################################
from __future__ import annotations

import inspect
from pathlib import Path
import traceback
from typing import Any

from click import Choice, Command, Group

from ..core.docker import ComposeManager
from ..core.files import FileManager

#################################################
# CODE
#################################################
dicts = dict[str, Any]


class CustomGroup(Group):

    cwd: Path = Path.cwd()

    def __init__(self) -> None:
        super().__init__()
        self.file_manager = FileManager()
        self.compose_manager = ComposeManager()

        try:
            services = self.compose_manager.get_services()
        except Exception:
            services = []

        if not services:
            try:
                data: dicts = (
                    self.file_manager.read_json(self.cwd.joinpath("data.json"))
                    or {}
                )
                compose: dicts = data.get("compose", {}) or {}
                svc_list: list[dicts] = compose.get("services", []) or []
                names: list[str] = []
                for s in svc_list:
                    name = s.get("name")
                    if isinstance(name, str):
                        names.append(name)
                services = names
            except Exception:
                services = []

        if services:
            self.service_type = Choice([str(s) for s in services])
        else:
            self.service_type = None  # type: ignore

        self.__register_commands()

    def __register_commands(self) -> None:
        # Iterate only functions declared on the subclass (avoid inherited click methods)
        for name, func in inspect.getmembers(
            self.__class__, predicate=inspect.isfunction
        ):
            if name.startswith("_"):
                continue

            # Skip methods not defined on this exact class (i.e., inherited ones)
            if not func.__qualname__.startswith(self.__class__.__name__ + "."):
                continue

            method = getattr(self, name)
            try:
                result = method()
            except Exception as e:
                print(f"Error registering command '{name}': {e}")
                traceback.print_exc()
                continue

            if isinstance(result, Command):
                self.add_command(result)
