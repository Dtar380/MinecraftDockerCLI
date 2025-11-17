#################################################
# IMPORTS
#################################################
from __future__ import annotations

import json
from pathlib import Path
from shutil import copyfileobj
from typing import Any, cast

from importlib_resources import as_file, files  # type: ignore
import jinja2
import requests  # type: ignore
from yaspin import yaspin  # type: ignore

#################################################
# CODE
#################################################
dicts = dict[str, Any]


class FileManager:
    """
    File manager class. In charge of reading, writting and creating files.
    """

    cwd = Path.cwd()

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

        services: list[dicts] = compose.get("services", []) or []
        names: list[str] = [service.get("name") for service in services]  # type: ignore
        self.copy_files(self.cwd, names)

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
    def read_json(self, file: Path) -> dict[Any, Any]:
        with open(file, "r+") as f:
            data = dict(json.load(f))
        return data

    @yaspin(text="Writting JSON...", color="cyan")
    def write_json(self, file: Path, data: dict[Any, Any]) -> None:
        data_str = json.dumps(data, indent=2)
        with open(file, "w+") as f:
            f.write(data_str)
        return None

    @yaspin(text="Copying files...", color="cyan")
    def copy_files(self, path: Path, services: list[str]) -> None:
        docker_pkg = files("src.assets.docker")
        dockerfile_res = docker_pkg.joinpath("Dockerfile")
        dockerignore_res = docker_pkg.joinpath(".dockerignore")
        runsh_res = files("src.assets.scripts").joinpath("run.sh")
        readme_res = files("src.assets").joinpath("README.md")
        eula_res = files("src.assets.config").joinpath("eula.txt")

        # Ensure base path exists
        if not path.exists():
            raise ValueError("Path doesnt exist")

        # Read bytes from resources once
        dockerfile_bytes = dockerfile_res.read_bytes()
        dockerignore_bytes = dockerignore_res.read_bytes()
        runsh_bytes = runsh_res.read_bytes()
        readme_bytes = readme_res.read_bytes()
        eula_bytes = eula_res.read_bytes()

        # Write files for each service
        for service in services:
            dest_dir = path.joinpath("servers", service)
            dest_dir.mkdir(parents=True, exist_ok=True)

            (dest_dir / "Dockerfile").write_bytes(dockerfile_bytes)
            (dest_dir / ".dockerignore").write_bytes(dockerignore_bytes)
            (dest_dir / "run.sh").write_bytes(runsh_bytes)

            mc_dir = dest_dir.joinpath("data")
            mc_dir.mkdir(parents=True, exist_ok=True)
            (mc_dir / "eula.txt").write_bytes(eula_bytes)

            if "proxy" in service.lower():
                plugins = mc_dir.joinpath("plugins")
                plugins.mkdir(exist_ok=True)
                self.__download_proxy(mc_dir)

        # Write top-level README into the given path
        (path / "README.md").write_bytes(readme_bytes)

    def __download_proxy(self, path: Path) -> None:
        api = "https://fill.papermc.io/v3/projects/velocity"

        ver_resp = requests.get(api)
        versions = ver_resp.json()
        if not versions:
            return
        try:
            version = list(versions.get("versions").values())[0][0]
        except Exception:
            return

        builds_resp = requests.get(f"{api}/versions/{version}")
        builds = builds_resp.json()
        if not builds:
            return
        try:
            build = list(builds.get("builds"))[0]
        except Exception:
            return

        final_resp = requests.get(f"{api}/versions/{version}/builds/{build}")
        final = final_resp.json()
        if not final:
            return
        try:
            downloads = final.get("downloads")
            if "server:default" in downloads:
                download_url = downloads["server:default"].get("url")
            else:
                return
        except Exception:
            return

        if not download_url:
            return

        out_path = path.joinpath("proxy.jar")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                copyfileobj(r.raw, f)
        try:
            (path / "proxy_ver.txt").write_text(
                f"velocity-{version}-{build}.jar"
            )
        except Exception:
            return

    @yaspin(text="Rendering template...", color="cyan")
    def template_to_file(
        self, template_path: Path, context: dict[Any, Any], dest_path: Path
    ) -> Path:
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
