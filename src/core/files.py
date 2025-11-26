#################################################
# IMPORTS
#################################################
from __future__ import annotations

import json
from pathlib import Path
from time import sleep
from typing import Any, cast

from importlib_resources import as_file, files  # type: ignore
import jinja2
from yaspin import yaspin  # type: ignore

from .downloader import Downloader

#################################################
# CODE
#################################################
dicts = dict[str, Any]


class FileManager:
    """
    File manager class. In charge of reading, writting and creating files.
    """

    cwd = Path.cwd()

    def __init__(self, sleep: int = 0) -> None:
        self.sleep = sleep

    def save_files(self, data: dicts, build: bool = False) -> None:
        """
        Create/Update files and save them. Also copies the asset files.
        """

        tmps_path = files("src.assets.templates")
        composer_template = tmps_path.joinpath("docker-compose.yml.j2")
        env_template = tmps_path.joinpath(".env.j2")

        if not build:
            self.write_json(self.cwd.joinpath("data.json"), data)

        compose: dicts = data.get("compose") or {}
        with as_file(composer_template) as composer_tmp:  # type: ignore
            composer_tmp = cast(Path, composer_tmp)
            self.template_to_file(
                composer_tmp, compose, self.cwd.joinpath("docker-compose.yml")
            )

        server_files: list[dicts] = data.get("server_files", []) or []
        self.copy_server_files(self.cwd, server_files)

        if compose.get("web", False):
            self.copy_web_files(self.cwd)

        envs: list[dicts] = data.get("envs") or []
        for env in envs:
            relative_path = f"servers/{env.get('CONTAINER_NAME')}/.env"  # type: ignore
            with as_file(env_template) as env_tmp:  # type: ignore
                env_tmp = cast(Path, env_tmp)
                self.template_to_file(
                    env_tmp, env, self.cwd.joinpath(relative_path)
                )

        self.cwd.joinpath(".backup").mkdir(exist_ok=True)

    @yaspin(text="Reading JSON...", color="cyan")
    def read_json(self, file: Path) -> dict[Any, Any] | None:
        sleep(self.sleep)

        try:
            with open(file, "r+") as f:
                data = dict(json.load(f))
            return data
        except Exception:
            return None

    @yaspin(text="Writting JSON...", color="cyan")
    def write_json(self, file: Path, data: dict[Any, Any]) -> None:
        sleep(self.sleep)

        data_str = json.dumps(data, indent=2)
        with open(file, "w+") as f:
            f.write(data_str)
        return None

    @yaspin(text="Copying server files...", color="cyan")
    def copy_server_files(self, path: Path, server_files: list[dicts]) -> None:
        sleep(self.sleep)

        docker_pkg = files("src.assets.docker")
        dockerfile_res = docker_pkg.joinpath("minecraft.Dockerfile")
        dockerignore_res = docker_pkg.joinpath("minecraft.dockerignore")
        runsh_res = files("src.assets.scripts").joinpath("run.sh")
        readme_res = files("src.assets").joinpath("README.md")
        eula_res = files("src.assets.config").joinpath("eula.txt")

        # Ensure base path exists
        if not path.exists():
            raise ValueError("Path doesn't exist")

        # Read bytes from resources once
        dockerfile_bytes = dockerfile_res.read_bytes()
        dockerignore_bytes = dockerignore_res.read_bytes()
        runsh_bytes = runsh_res.read_bytes()
        readme_bytes = readme_res.read_bytes()
        eula_bytes = eula_res.read_bytes()

        # Write files for each server
        for server_file in server_files:
            name = str(server_file.get("name"))
            dest_dir = path.joinpath("servers", name)
            dest_dir.mkdir(parents=True, exist_ok=True)

            (dest_dir / "Dockerfile").write_bytes(dockerfile_bytes)
            (dest_dir / ".dockerignore").write_bytes(dockerignore_bytes)
            (dest_dir / "run.sh").write_bytes(runsh_bytes)

            mc_dir = dest_dir.joinpath("data")
            mc_dir.mkdir(parents=True, exist_ok=True)
            (mc_dir / "eula.txt").write_bytes(eula_bytes)

            server = server_file.get("server")
            if server:
                jar_file = server.get("jar_file") or None
                server_type = server.get("type") or None
                version = server.get("version") or None

                if server_type is None or jar_file is None:
                    continue

                d = Downloader("https://fill.papermc.io/v3/projects")
                d.download_latest(server_type, mc_dir, jar_file, version)

        # Write top-level README into the given path
        (path / "README.md").write_bytes(readme_bytes)

    @yaspin(text="Copying web files...", color="cyan")
    def copy_web_files(self, path: Path) -> None:
        sleep(self.sleep)
        docker_pkg = files("src.assets.docker")
        frontend_dockerfile_res = docker_pkg.joinpath("node.Dockerfile")
        frontend_dockerignore_res = docker_pkg.joinpath("node.dockerignore")
        backend_dockerfile_res = docker_pkg.joinpath("python.Dockerfile")
        backend_dockerignore_res = docker_pkg.joinpath("python.dockerignore")

        if not path.exists():
            raise ValueError("Path doesn't exist")

        frontend_dockerfile_bytes = frontend_dockerfile_res.read_bytes()
        frontend_dockerignore_bytes = frontend_dockerignore_res.read_bytes()
        backend_dockerfile_bytes = backend_dockerfile_res.read_bytes()
        backend_dockerignore_bytes = backend_dockerignore_res.read_bytes()

        web_dir = path.joinpath("web")
        web_dir.mkdir(parents=True, exist_ok=True)

        frontend_dir = web_dir.joinpath("frontend")
        backend_dir = web_dir.joinpath("backend")
        frontend_dir.mkdir(parents=True, exist_ok=True)
        backend_dir.mkdir(parents=True, exist_ok=True)

        (frontend_dir / "Dockerfile").write_bytes(frontend_dockerfile_bytes)
        (frontend_dir / ".dockerignore").write_bytes(
            frontend_dockerignore_bytes
        )
        (backend_dir / "Dockerfile").write_bytes(backend_dockerfile_bytes)
        (backend_dir / ".dockerignore").write_bytes(backend_dockerignore_bytes)

    @yaspin(text="Rendering template...", color="cyan")
    def template_to_file(
        self, template_path: Path, context: dict[Any, Any], dest_path: Path
    ) -> Path:
        sleep(self.sleep)

        rendered = self.__render_template(template_path, context)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(rendered, encoding="utf-8")
        return dest_path

    def __render_template(
        self, template_path: Path, context: dict[Any, Any]
    ) -> str:
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_path.parent)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template_obj = env.get_template(template_path.name)
        return template_obj.render(**context)
