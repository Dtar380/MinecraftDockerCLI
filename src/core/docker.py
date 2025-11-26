#################################################
# IMPORTS
#################################################
from __future__ import annotations

from pathlib import Path
from subprocess import PIPE, CalledProcessError, CompletedProcess, run
from time import sleep, strftime
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

    cwd = Path.cwd()

    def __init__(self, sleep: int = 0) -> None:
        self.composer_file = self.cwd.joinpath("docker-compose.yml")
        self.file_manager = FileManager()
        self.sleep = sleep

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

    @yaspin(text="Stopping servers...", color="cyan")
    def stop(self) -> CompletedProcess[str]:
        sleep(self.sleep)

        return self.__run("stop")

    @yaspin(text="Starting servers...", color="cyan")
    def start(self) -> CompletedProcess[str]:
        sleep(self.sleep)

        return self.__run("start")

    @yaspin(text="Removing Container...", color="cyan")
    def down(self, remove_volumes: bool = False) -> CompletedProcess[str]:
        sleep(self.sleep)

        args = ["down"]
        if remove_volumes:
            args.append("-v")
        return self.__run(*args)

    @yaspin(text="Putting Up Container...", color="cyan")
    def up(
        self, attached: bool = True, detach_keys: str = "ctrl-p,ctrl-q"
    ) -> CompletedProcess[str]:
        sleep(self.sleep)

        args = ["up", "--build"]
        if not attached:
            args.append("-d")
        else:
            args.extend(["--detach-keys", detach_keys])
            print(f"Use '{detach_keys}' to detach (press sequentially).\n")
        return self.__run(*args)

    def open_terminal(
        self, server: str, detach_keys: str = "ctrl-p,ctrl-q"
    ) -> None:
        try:
            print(f"Use '{detach_keys}' to detach (press sequentially).\n")
            run(
                ["docker", "attach", "--detach-keys", detach_keys, server],
                check=True,
            )
            return
        except CalledProcessError:
            pass
        except Exception:
            pass

        for shell in ("/bin/bash", "/bin/sh"):
            cmd = ["docker", "exec", "-it", server, shell]
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
        sleep(self.sleep)

        backup_path = cwd.joinpath(".backup")
        compose_json = cwd.joinpath("data.json")

        backup_path.mkdir(exist_ok=True)
        data: dict[str, Any] = self.file_manager.read_json(compose_json) or {}
        if not data:
            exit("ERROR: data.json is empty")

        servers = data.get("compose", {}).get("servers", []) or []  # type: ignore
        names: list[str] = [
            svc.get("name") for svc in servers if svc.get("name") is not None  # type: ignore
        ]

        for svc_name in names:
            tar_file = backup_path.joinpath(
                f"{svc_name}_{strftime('%d-%m-%Y_%H-%M-%S')}.tar.gz"
            )

            path_inside = "/server"
            try:
                with open(tar_file, "wb") as f:
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
                        stdout=f,
                        stderr=PIPE,
                    )
            except Exception as exc:
                print(f"Error writting backup file {tar_file}: {exc}")
                continue
            if proc.returncode != 0:
                err = proc.stderr.decode(errors="ignore")
                print(f"tar failed for container {svc_name}: {err}")
                continue

        database: dict[str, str] = data.get("compose", {}).get("database", {}) or {}
        if database:
            db_user: str = database.get("user", "")
            db_name: str = database.get("db", "")
            db_backup_file = backup_path.joinpath(
                f"database_{strftime('%d-%m-%Y_%H-%M-%S')}.sql"
            )
            try:
                with open(db_backup_file, "wb") as f:
                    proc = run(
                        [
                            "docker",
                            "exec",
                            "-t",
                            "postgres_db",
                            "pg_dump",
                            "-U", db_user,
                            "-F", "c",
                            db_name
                        ],
                        stdout=f,
                        stderr=PIPE,
                    )
            except Exception as exc:
                print(f"Error writting backup file for sql database: {exc}")
                return
            if proc.returncode != 0:
                err = proc.stderr.decode(errors="ignore")
                print(f"Failed to extract the sql database: {err}")
