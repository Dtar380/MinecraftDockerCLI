#################################################
# IMPORTS
#################################################
from __future__ import annotations

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

    @yaspin(text="Stopping Services...", color="cyan")
    def stop(self) -> CompletedProcess[str]:
        return self.__run("stop")

    @yaspin(text="Starting Services...", color="cyan")
    def start(self) -> CompletedProcess[str]:
        return self.__run("start")

    @yaspin(text="Removing Container...", color="cyan")
    def down(self, remove_volumes: bool = False) -> CompletedProcess[str]:
        args = ["down"]
        if remove_volumes:
            args.append("-v")
        return self.__run(*args)

    @yaspin(text="Putting Up Container...", color="cyan")
    def up(self, attached: bool = True) -> CompletedProcess[str]:
        args = ["up", "--build"]
        if not attached:
            args.extend(["-d"])
        return self.__run(*args)

    def open_terminal(self, service: str, detach_keys: str = "ctrl-k") -> None:
        try:
            print(f"Use '{detach_keys}' to detach (press sequentially).\n")
            run(
                ["docker", "attach", "--detach-keys", detach_keys, service],
                check=True,
            )
            return
        except CalledProcessError:
            pass
        except Exception:
            pass

        for shell in ("/bin/bash", "/bin/sh"):
            cmd = ["docker", "exec", "-it", service, shell]
            try:
                run(cmd, check=True)
                return
            except CalledProcessError:
                continue
            except Exception:
                continue

        print("Couldn't open a shell in the container")

    @yaspin(text="Backing Up Container...", color="cyan")
    def back_up(self, cwd: Path = Path.cwd()) -> None:
        backup_path = cwd.joinpath(".backup")
        compose_json = cwd.joinpath("data.json")

        backup_path.mkdir(exist_ok=True)
        data: dict[str, Any] = self.file_manager.read_json(compose_json)
        services = data.get("compose", {}).get("services", []) or []  # type: ignore
        names: list[str] = [svc.get("name") for svc in services if svc.get("name") is not None]  # type: ignore

        print(names)
        for svc_name in names:
            tar_file = backup_path.joinpath(
                f"{svc_name}_{strftime("%d-%m-%Y_%H:%M:%S")}.tar.gz"
            )

            path_inside = "/server"
            print(svc_name)
            try:
                proc = run(
                    [
                        "docker",
                        "exec",
                        svc_name,
                        "tar",
                        "-C",
                        path_inside,
                        "-czf",
                        "-",
                        ".",
                    ],
                    stdout=PIPE,
                    stderr=PIPE,
                )
            except Exception as exc:
                print(f"Error running tar inside container {svc_name}: {exc}")
                continue
            if proc.returncode != 0:
                err = proc.stderr.decode(errors="ignore")
                print(f"tar failed for container {svc_name}: {err}")
                continue
            try:
                with open(tar_file, "wb") as f:
                    f.write(proc.stdout)
            except Exception as exc:
                print(f"Error writting backup file {tar_file}: {exc}")
                continue
