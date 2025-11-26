#################################################
# IMPORTS
#################################################
from __future__ import annotations

import re
from typing import Any

from click import ParamType


#################################################
# CODE
#################################################
class DetachKeysType(ParamType):
    """Click param type for `--detach-keys`.

    Accepts one or more key-pairs joined with `,`, where each pair is two
    key tokens joined by `-`. Examples:

    - `ctrl-p`
    - `ctrl-p,ctrl-q`

    The value is returned unchanged as a string when valid.
    """

    name = "detach-keys"

    # Key token: anything but comma, dash and whitespace (at least one char)
    _pair_re = re.compile(r"^[^-\s,]+-[^-\s,]+(?:,[^-\s,]+-[^-\s,]+)*$")

    # Human-friendly help message (can be used when building option help)
    help = (
        "One or more key pairs separated by commas. Each pair uses '-' to join two keys,"
        " e.g. 'ctrl-p' or 'ctrl-p,ctrl-q'."
    )

    def get_metavar(self, param: Any, ctx: Any = None) -> str:
        """Return a short metavar for use in option help text."""
        return "KEY-KEY[,KEY-KEY]"

    def convert(self, value: Any, param: Any, ctx: Any) -> Any:
        if value is None:
            return value

        if not isinstance(value, str):
            self.fail("detach-keys must be a string", param, ctx)

        v = value.strip()
        if not v:
            self.fail("detach-keys cannot be empty", param, ctx)

        if not self._pair_re.fullmatch(v):
            self.fail(
                "Invalid detach-keys format. Use pairs like 'ctrl-p' and separate multiple pairs with commas, e.g. 'ctrl-p,ctrl-q'",
                param,
                ctx,
            )

        # Return the original (trimmed) string so callers get the same representation
        return v


# Reusable instance
DETACH_KEYS = DetachKeysType()
# attach help string on the instance as well
DETACH_KEYS.help = DetachKeysType.help  # type: ignore[attr-defined]


class ServerType(ParamType):
    """ParamType for server names used by `CustomGroup`.

    This type can be constructed without choices and later populated with
    `set_choices()`. The convert method will validate that the provided
    value is one of the known choices when choices have been set.
    """

    name = "server-type"

    # Generic help message; can be enriched with available choices at runtime
    help = "Server name. If available, valid choices will be listed in the help message."

    def get_metavar(self, param: Any, ctx: Any = None) -> str:
        return "SERVER"

    def __init__(self, choices: list[str] | None = None) -> None:
        self.choices: list[str] = choices or []

    def set_choices(self, choices: list[str]) -> None:
        self.choices = [str(c) for c in choices]

    def convert(self, value: Any, param: Any, ctx: Any) -> Any:
        if value is None:
            return value
        if not isinstance(value, str):
            self.fail("server type must be a string", param, ctx)
        if self.choices and value not in self.choices:
            self.fail(
                f"Invalid server '{value}'. Available: {', '.join(self.choices)}",
                param,
                ctx,
            )
        return value


# Reusable empty instance (can be populated later)
SERVER_TYPE = ServerType()
SERVER_TYPE.help = ServerType.help  # type: ignore[attr-defined]
