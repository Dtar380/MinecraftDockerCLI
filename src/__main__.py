#################################################
# IMPORTS
#################################################
from __future__ import annotations

from click import Context, Group, group, option
from click.formatting import HelpFormatter

from .cli.builder import Builder
from .cli.manager import Manager
from .utils import cli as cli_utils


#################################################
# CODE
#################################################
class TopGroup(Group):

    def format_commands(self, ctx: Context, formatter: HelpFormatter) -> None:
        # Build a mapping source -> list[(name, help)]
        sections: dict[str, list[tuple[str, str]]] = {}
        for cmd_name in self.list_commands(ctx):
            cmd = self.get_command(ctx, cmd_name)
            if cmd is None:
                continue
            source = getattr(cmd, "source", "Other")
            sections.setdefault(source, []).append(
                (cmd_name, cmd.get_short_help_str())
            )

        # Write sections in a stable order (Builder, Manager, Other)
        order = ["Builder", "Manager"] + [
            s for s in sections.keys() if s not in ("Builder", "Manager")
        ]
        written_any = False
        for sec in order:
            entries = sections.get(sec)
            if not entries:
                continue
            written_any = True
            with formatter.section(sec):
                formatter.write_dl(entries)

        if not written_any:
            # Fallback to default behaviour
            super().format_commands(ctx, formatter)


# Create the main group for the CLI using custom Group class
@option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose output (avoid clears).",
)
@option(
    "-y",
    "--no-confirm",
    "no_confirm",
    is_flag=True,
    default=False,
    help="Do not ask for confirmations (assume yes).",
)
@group(cls=TopGroup)
def cli(verbose: bool = False, no_confirm: bool = False) -> None:
    # Apply global CLI flags to utility helpers
    try:
        cli_utils.set_verbose(verbose)
        cli_utils.set_no_confirm(no_confirm)
    except Exception:
        # If utils cannot be imported for some reason, continue silently
        pass


# Add the two command groups
builder = Builder()
manager = Manager()

for cmd in builder.commands.values():
    # annotate source so TopGroup can display grouped help
    setattr(cmd, "source", "Builder")
    cli.add_command(cmd)
for cmd in manager.commands.values():
    setattr(cmd, "source", "Manager")
    cli.add_command(cmd)


# Create the main entry point
def main() -> None:
    cli()


# Execute the program
if __name__ == "__main__":
    main()
