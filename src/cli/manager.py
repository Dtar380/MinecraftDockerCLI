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
        self.compose_manager.sleep = 2
        self.file_manager.sleep = 2

    def open(self) -> Command:
        help = "Open the terminal of a server."
        options = [
            Option(["--server"], type=self.server_type, default=None),
            Option(
                ["--detach-keys"],
                type=self.detach_keys_type,
                default="ctrl-p,ctrl-q",
            ),
        ]

        def callback(server: str, detach_keys: str = "ctrl-p,ctrl-q") -> None:
            self.compose_manager.open_terminal(server, detach_keys)

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
        options = [
            Option(["--attached"], is_flag=True, default=False),
            Option(
                ["--detach-keys"],
                type=self.detach_keys_type,
                default="ctrl-p,ctrl-q",
            ),
        ]

        def callback(
            attached: bool = False, detach_keys: str = "ctrl-p,ctrl-q"
        ) -> None:
            self.compose_manager.up(attached, detach_keys)

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

    def restart(self) -> Command:

        help = "Restart the containers."
        options: list[Option] = []

        def callback() -> None:
            self.compose_manager.stop()
            self.compose_manager.start()

        return Command(
            name=inspect.currentframe().f_code.co_name,  # type: ignore
            help=help,
            callback=callback,
            params=options,  # type: ignore
        )
