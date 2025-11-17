#################################################
# IMPORTS
#################################################
from __future__ import annotations

import inspect

from InquirerPy import inquirer  # type: ignore
from InquirerPy.validator import EmptyInputValidator  # type: ignore
from click import Command, Option

from .custom_group import CustomGroup


#################################################
# CODE
#################################################
class Manager(CustomGroup):

    def __init__(self) -> None:
        super().__init__()

    def open(self) -> Command:
        help = "Open the terminal of a service."
        options = [Option(["--service"], type=self.service_type, default=None)]

        def callback(service: str) -> None:
            self.compose_manager.open_terminal(service)

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def backup(self) -> Command:

        help = "Create a backup of the containers."
        options: list[Option] = []

        def callback() -> None:
            self.compose_manager.back_up(self.cwd)

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def up(self) -> Command:
        help = "Start up the containers after changes."
        options = [Option(["--attached"], is_flag=True, default=False)]

        def callback(attached: bool = False) -> None:
            self.compose_manager.up(attached)

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def down(self) -> Command:

        help = "Delete the containers."
        options = [Option(["--rm-volumes"], is_flag=True, default=True)]

        def callback(rm_volumes: bool = True) -> None:
            self.compose_manager.down(rm_volumes)

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def start(self) -> Command:

        help = "Start the containers."
        options: list[Option] = []

        def callback() -> None:
            self.compose_manager.start()

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )

    def stop(self) -> Command:

        help = "Stop the containers."
        options: list[Option] = []

        def callback() -> None:
            self.compose_manager.stop()

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )
