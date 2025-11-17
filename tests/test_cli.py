from __future__ import annotations

from click import Context
from click.testing import CliRunner  # type: ignore
import pytest  # type: ignore


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
