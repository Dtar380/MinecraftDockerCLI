#################################################
# IMPORTS
#################################################
from __future__ import annotations

from os import name, system
from time import sleep

from InquirerPy import inquirer  # type: ignore

#################################################
# CODE
#################################################
# Global flags controlled by the CLI
VERBOSE = False
NO_CONFIRM = False


def set_verbose(v: bool) -> None:
    """Enable or disable verbose mode (avoids clears)."""
    global VERBOSE
    VERBOSE = bool(v)  # type: ignore


def set_no_confirm(v: bool) -> None:
    """Enable or disable interactive confirmations."""
    global NO_CONFIRM
    NO_CONFIRM = bool(v)  # type: ignore


def clear(t: float) -> None:
    """
    Sleep t seconds and clear the console, unless verbose mode is enabled.
    """
    if VERBOSE:
        return
    sleep(t)
    system("cls" if name == "nt" else "clear")


def confirm(msg: str, default: bool = True) -> bool:
    """
    Ask for confirmation with custom message and default value.

    If `NO_CONFIRM` is enabled the function will bypass the prompt and
    return `True` (assume yes) so the CLI can run non-interactively.
    """
    if NO_CONFIRM:
        return True
    return inquirer.confirm(  # type: ignore
        message=msg, default=default
    ).execute()
