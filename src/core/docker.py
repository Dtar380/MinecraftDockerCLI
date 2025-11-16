#################################################
# IMPORTS
#################################################
from __future__ import annotations

from gzip import GzipFile
from pathlib import Path
from subprocess import PIPE, CalledProcessError, CompletedProcess, run
from time import strftime
from typing import Any

from yaspin import yaspin

from .files import FileManager


#################################################
# CODE
#################################################
class ComposeManager:
    """
    Compose manager class. In charge of executing docker commands.
    """

    def __init__(self) -> None:
        self.composer_file = Path.cwd().joinpath("docker-compose.yml")
        self.file_manager = FileManager()

    def __run(
        self,
        *args: str,
        capture_output: bool = False,
        print_output: bool = True,
    ) -> CompletedProcess[str]:
        command = ["docker", "compose", "-f", str(self.composer_file), *args]
        result = run(command, text=True, capture_output=capture_output)
        if result.returncode != 0 and print_output:
            print("ERROR: ", result.stderr)
        elif print_output:
            print("Command run: ", result.stdout)
        return result

    def get_services(self) -> list[str]:
        result = self.__run(
            "config", "--services", capture_output=True, print_output=False
        )
        if result.returncode != 0:
            return []
        services = [
            line.strip() for line in result.stdout.splitlines() if line.strip()
        ]
        return services

    @yaspin("Stopping Services...", color="cyan")
    def stop(self) -> CompletedProcess[str]:
        return self.__run("stop")

    @yaspin("Starting Services...", color="cyan")
    def start(self) -> CompletedProcess[str]:
        return self.__run("start")

    @yaspin("Removing Container...", color="cyan")
    def down(self, remove_volumes: bool = False) -> CompletedProcess[str]:
        args = ["down"]
        if remove_volumes:
            args.append("-v")
        return self.__run(*args)

    @yaspin("Putting Up Container...", color="cyan")
    def up(self, detached: bool = True) -> CompletedProcess[str]:
        args = ["up"]
        if detached:
            args.append("-d")
        return self.__run(*args)

    @yaspin("Backing Up Container...", color="cyan")
    def back_up(self, cwd: Path = Path.cwd()) -> None:
        backup_path = cwd.joinpath(".backup")
        compose_json = cwd.joinpath("data.json")

        backup_path.mkdir(exist_ok=True)
        data: dict[str, Any] = self.file_manager.read_json(compose_json)
        services = data.get("composer", {}).get("services", []) or []  # type: ignore
        names: list[str] = [svc.get("name") for svc in services if svc.get("name") is not None]  # type: ignore
        for svc_name in names:
            tar_file = backup_path.joinpath(
                f"{svc_name}_{strftime("%d-%m-%Y_%H:%M:%S")}.tar.gz"
            )
            container_name = self.__get_container_name(svc_name)
            if not container_name:
                continue

            path_inside = f"/{svc_name}"
            with open(tar_file, "wb") as f:
                proc = run(
                    [
                        "docker",
                        "exec",
                        container_name,
                        "tar",
                        "-C",
                        path_inside,
                        "-cv",
                        ".",
                    ],
                    stdout=PIPE,
                )
                with GzipFile(fileobj=f, mode="wb") as gz:
                    gz.write(proc.stdout)

    def __get_container_name(self, service_name: str) -> str | None:
        result = self.__run("ps", capture_output=True)
        lines = result.stdout.splitlines()
        for line in lines[2:]:  # skip header
            if service_name in line:
                return line.split()[0]
        return None

    def open_terminal(self, service: str) -> None:
        container = self.__get_container_name(service)
        if not container:
            print(f"Service: '{service}' not found.")
            return
        for shell in ("/bin/bash", "/bin/sh"):
            cmd = ["docker", "exec", "-it", container, shell]
            try:
                run(cmd, text=True)
                return
            except CalledProcessError:
                continue
            except Exception:
                continue

        print("Couldn't open a shell in the container")
