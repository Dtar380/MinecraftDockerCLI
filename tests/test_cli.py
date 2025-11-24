from __future__ import annotations

from importlib import import_module
import json
from pathlib import Path
from typing import Any

from click import Context
from click.testing import CliRunner
import pytest  # type: ignore

from .__vars__ import *


class Test_CLI:

    def setup_method(self) -> None:
        self.runner = CliRunner()
        from src import cli

        self.cli = cli

    # HELP
    def test_help(self) -> None:
        result = self.runner.invoke(self.cli, ["--help"])
        assert result.exit_code == 0
        assert "Builder" in result.stdout
        assert "Manager" in result.stdout
        commands = self.cli.list_commands(Context(self.cli))
        for command in commands:
            result = self.runner.invoke(self.cli, [command, "--help"])
            assert result.exit_code == 0

    # BUILDER
    def test_create_errors(
        self, isolate_cwd: Path, monkeypatch: pytest.MonkeyPatch     
    ) -> None:
        base = isolate_cwd

        data: dicts = {
            "compose": {"services": [s1, s2], "network": ["network"]},
            "envs": [e1, e2],
            "service_files": [f1, f2],
        }
        (base / "data.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

        result = self.runner.invoke(self.cli, ["create"])
        assert result.exit_code != 0

    def test_create(
        self, isolate_cwd: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        service = s1
        env = e1
        service_file = f1

        from src.cli.builder import Builder

        monkeypatch.setattr(
            Builder,
            "_Builder__get_data",
            lambda self, menu, name=None: (service, env, service_file),  # type: ignore
        )

        result = self.runner.invoke(self.cli, ["create"])
        assert result.exit_code == 0
        assert "Files saved!" in result.output

        base = isolate_cwd
        assert (base / "data.json").exists()
        data = json.loads((base / "data.json").read_text(encoding="utf-8"))
        assert data is not None

        services = data.get("compose", {}).get("services", [])
        assert len(services) == 1
        assert services[0] == service

        networks = data.get("compose", {}).get("networks", [])
        assert len(networks) == 0

        envs = data.get("envs", [])
        assert len(envs) == 1
        assert envs[0] == env

        service_files = data.get("service_files", [])
        assert len(service_files) == 1
        assert service_files[0] == service_file

        assert (base / "docker-compose.yml").exists()
        expected = self.__render_template(
            data=data.get("compose"), template_name="docker-compose.yml.j2"
        )
        actual = (base / "docker-compose.yml").read_text(encoding="utf-8")
        assert expected == actual

        name = services[0].get("name")

        assert (base / "servers" / name / ".env").exists()
        expected = self.__render_template(data=envs[0], template_name=".env.j2")
        actual = (base / "servers" / name / ".env").read_text(encoding="utf-8")
        assert expected == actual

        assert (base / "servers" / name / "Dockerfile").exists()
        assert (base / "servers" / name / "run.sh").exists()
        assert (base / "servers" / name / "data" / "eula.txt").exists()

    def test_create_network(
        self, isolate_cwd: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.cli.builder import Builder

        seq = [(s1, e1, f1), (s2, e2, f2)]

        def get_data(
            self: Any, menu: Any, name: str | None = None
        ) -> tuple[dicts, dicts, dicts]:
            try:
                return seq.pop(0)
            except IndexError:
                return (s2, e2, f2)

        monkeypatch.setattr(Builder, "_Builder__get_data", get_data)
        monkeypatch.setattr(
            Builder,
            "_Builder__get_name",
            lambda self, message, network=False: "network",  # type: ignore
        )

        confirms = [True, True, False]
        def fake_confirm(msg: str, default: bool = True) -> bool:
            try:
                return confirms.pop(0)
            except IndexError:
                return True

        modules = ["src.utils.cli", "src.cli.builder", "src.cli.menu"]
        for mod_name in modules:
            mod = import_module(mod_name)
            monkeypatch.setattr(mod, "confirm", fake_confirm)

        result = self.runner.invoke(self.cli, ["create", "--network"])
        assert result.exit_code == 0

        base = isolate_cwd
        assert (base / "data.json").exists()
        data = json.loads((base / "data.json").read_text(encoding="utf-8"))
        assert data is not None

        services = data.get("compose", {}).get("services", [])
        assert len(services) == 2
        for svc_json, svc_expected in zip(services, (s1, s2)):
            assert svc_json == svc_expected

        networks = data.get("compose", {}).get("networks", [])
        assert len(networks) == 1
        assert "network" == networks[0]

        envs = data.get("envs", [])
        assert len(envs) == 2
        for env_json, env_expected in zip(envs, (e1, e2)):
            assert env_json == env_expected

        service_files = data.get("service_files", [])
        assert len(service_files) == 2
        for svc_files_json, svc_files_expected in zip(service_files, (f1, f2)):
            assert svc_files_json == svc_files_expected

        assert (base / "docker-compose.yml").exists()
        expected = self.__render_template(
            data=data.get("compose"), template_name="docker-compose.yml.j2"
        )
        actual = (base / "docker-compose.yml").read_text(encoding="utf-8")
        assert expected == actual

        names = sorted([s.get("name") for s in services])
        for i, name in enumerate(names):
            assert (base / "servers" / name / ".env").exists()
            expected = self.__render_template(
                data=envs[i], template_name=".env.j2"
            )
            actual = (base / "servers" / name / ".env").read_text(
                encoding="utf-8"
            )
            assert expected == actual

            assert (base / "servers" / name / "Dockerfile").exists()
            assert (base / "servers" / name / "run.sh").exists()
            assert (base / "servers" / name / "data" / "eula.txt").exists()

    def test_update_errors(self, isolate_cwd: Path) -> None:
        result = self.runner.invoke(self.cli, ["update", "--add", "--remove"])
        assert result.exit_code != 0
        result = self.runner.invoke(self.cli, ["update", "--add", "--change"])
        assert result.exit_code != 0
        result = self.runner.invoke(
            self.cli, ["update", "--remove", "--change"]
        )
        assert result.exit_code != 0
        result = self.runner.invoke(
            self.cli, ["update", "--add", "--remove", "--change"]
        )
        assert result.exit_code != 0

        base = isolate_cwd
        if (base / "data.json").exists():
            (base / "data.json").unlink()

        result = self.runner.invoke(self.cli, ["update"])
        assert result.exit_code != 0
        assert (
            "ERROR: Missing JSON file for services. Use 'create' first."
            in result.output
        )

        (base / "data.json").write_text(data="")
        result = self.runner.invoke(self.cli, ["update"])
        assert result.exit_code != 0
        print(result.output)
        assert "ERROR: JSON file is empty. Use 'create' first." in result.output

        (base / "data.json").write_text(
            data=json.dumps(
                {"compose": {"services": [], "networks": []}, "envs": []},
                indent=2,
            ),
            encoding="utf-8",
        )
        result = self.runner.invoke(self.cli, ["update"])
        assert result.exit_code != 0
        print(result.output)
        assert "ERROR: No services found. Use 'create' first." in result.output

        root = Path(__file__).resolve().parent.parent
        template = root / "src" / "assets" / "templates" / "template.json"
        with open(template, "r", encoding="utf-8") as f:
            data = json.load(f)
        (base / "data.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
        result = self.runner.invoke(self.cli, ["update"])
        assert result.exit_code != 0
        assert "Use --add, --remove or --change flag." in result.output

    def test_update_remove(
        self, isolate_cwd: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        base = isolate_cwd

        data: dicts = {
            "compose": {"services": [s1, s2], "network": ["network"]},
            "envs": [e1, e2],
            "service_files": [f1, f2],
        }
        (base / "data.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

        result = self.runner.invoke(
            self.cli, ["update", "--service", "server1", "--remove"]
        )
        assert result.exit_code == 0
        assert "removed and files updated." in result.output

        data_after = json.loads(
            (base / "data.json").read_text(encoding="utf-8")
        )
        services_after = data_after.get("compose", {}).get("services", [])
        envs_after = data_after.get("envs", [])
        service_files_after = data_after.get("service_files", [])
        assert all(s.get("name") != "server1" for s in services_after)
        assert all(e.get("CONTAINER_NAME") != "server1" for e in envs_after)
        assert all(f.get("name") != "server1" for f in service_files_after)

    def test_update_add(
        self, isolate_cwd: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        base = isolate_cwd

        data: dicts = {
            "compose": {"services": [s1], "network": ["network"]},
            "envs": [e1],
            "service_files": [f1],
        }
        (base / "data.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

        from src.cli.builder import Builder

        monkeypatch.setattr(
            Builder,
            "_Builder__get_data",
            lambda self, menu, name=None: (s2, e2, f2),  # type: ignore
        )

        result = self.runner.invoke(
            self.cli, ["update", "--service", "new", "--add"]
        )
        assert result.exit_code == 0

        data_after = json.loads(
            (base / "data.json").read_text(encoding="utf-8")
        )
        assert data_after is not None

        services_after = data_after.get("compose", {}).get("services", [])
        envs_after = data_after.get("envs", [])
        service_files_after = data_after.get("service_files", [])

        service_names = [s.get("name") for s in services_after]
        assert "new" in service_names
        env_names = [e.get("CONTAINER_NAME") for e in envs_after]
        assert "new" in env_names
        service_files_names = [f.get("name") for f in service_files_after]
        assert "new" in service_files_names

    def test_update_change(
        self, isolate_cwd: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        base = isolate_cwd

        data: dicts = {
            "compose": {"services": [s1], "network": ["network"]},
            "envs": [e1],
            "service_files": [f1],
        }
        (base / "data.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

        changed_service = s2
        changed_service["name"] = s1["name"]
        changed_env = e2
        changed_env["CONTAINER_NAME"] = e1["CONTAINER_NAME"]
        changed_svc_files = f2
        changed_svc_files["name"] = f1["name"]

        from src.cli.builder import Builder

        monkeypatch.setattr(
            Builder,
            "_Builder__get_data",
            lambda self, menu, name=None: (changed_service, changed_env, changed_svc_files)  # type: ignore
        )

        result = self.runner.invoke(
            self.cli, ["update", "--service", "server1", "--change"]
        )
        assert result.exit_code == 0

        data_after = json.loads(
            (base / "data.json").read_text(encoding="utf-8")
        )
        assert data_after is not None

        services_after = data_after.get("compose", {}).get("services", [])
        assert len(services_after) == 1
        assert services_after[0] == changed_service

        networks_after = data_after.get("compose", {}).get("networks", [])
        assert len(networks_after) == 0

        envs_after = data_after.get("envs", [])
        assert len(envs_after) == 1
        assert envs_after[0] == changed_env

        service_files_after = data_after.get("service_files", [])
        assert len(service_files_after) == 1
        assert service_files_after[0] == changed_svc_files

    def test_build_errors(self, isolate_cwd: Path) -> None:
        base = isolate_cwd
        if (base / "data.json").exists():
            (base / "data.json").unlink()

        result = self.runner.invoke(self.cli, ["build"])
        assert result.exit_code != 0
        assert (
            "ERROR: Missing JSON file for services. Use 'create' first."
            in result.output
        )

        (base / "data.json").write_text(data="")
        result = self.runner.invoke(self.cli, ["build"])
        assert result.exit_code != 0
        print(result.output)
        assert "ERROR: JSON file is empty. Use 'create' first." in result.output

    def test_build(self, isolate_cwd: Path) -> None:
        base = isolate_cwd

        root = Path(__file__).resolve().parent.parent
        template = root / "src" / "assets" / "templates" / "template.json"
        with open(template, "r", encoding="utf-8") as f:
            data = json.load(f)

        (base / "data.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

        result = self.runner.invoke(self.cli, ["build"])
        assert result.exit_code == 0
        assert "Files saved!" in result.output

        assert (base / "docker-compose.yml").exists()
        assert (base / "servers" / "server" / ".env").exists()
        assert (base / "servers" / "server" / "Dockerfile").exists()
        assert (base / "servers" / "server" / "run.sh").exists()
        assert (base / "servers" / "server" / "data" / "eula.txt").exists()

    def __render_template(self, data: dicts, template_name: str) -> str:
        import jinja2

        root = Path(__file__).resolve().parent.parent
        template_dir = root / "src" / "assets" / "templates"
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir.__str__()),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(template_name)
        return template.render(**data)
