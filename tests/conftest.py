from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypeVar

import pytest  # type: ignore

# Type variable for decorator-preserving callable
T = TypeVar("T", bound=Callable[..., Any])


@pytest.fixture(autouse=True)
def disable_yaspin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable yaspin spinners/colors during tests by replacing the
    `yaspin.yaspin` decorator with a no-op decorator.
    """
    try:
        import yaspin as _yaspin  # type: ignore

        def _noop_yaspin(*args: Any, **kwargs: Any) -> Callable[[T], T]:
            def _decorator(func: T) -> T:
                return func

            return _decorator

        monkeypatch.setattr(_yaspin, "yaspin", _noop_yaspin, raising=False)
    except Exception:
        # If yaspin is not available or patching fails, silently continue
        pass


@pytest.fixture()
def isolate_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect CLI file operations to a temporary directory."""
    # Ensure core classes write into tmp_path instead of real cwd
    # Try to obtain the runtime instances created at import time and
    # patch their underlying classes so existing instances use tmp_path.
    import importlib

    try:
        import src as _src
    except Exception:
        _src = importlib.import_module("src")

    # builder instance is created in src.__main__ and exported on package
    builder_inst = getattr(_src, "builder", None)
    if builder_inst is None:
        mod = importlib.import_module("src.__main__")
        builder_inst = getattr(mod, "builder", None)

    if builder_inst is not None:
        # CustomGroup is the base class of Builder (mro[1])
        cg_cls = builder_inst.__class__.__mro__[1]
        monkeypatch.setattr(cg_cls, "cwd", tmp_path, raising=False)

        # Patch FileManager and ComposeManager classes used by the instance
        if hasattr(builder_inst, "file_manager"):
            fm_cls = builder_inst.file_manager.__class__
            monkeypatch.setattr(fm_cls, "cwd", tmp_path, raising=False)
        if hasattr(builder_inst, "compose_manager"):
            cm_cls = builder_inst.compose_manager.__class__
            monkeypatch.setattr(cm_cls, "cwd", tmp_path, raising=False)
    else:
        # Fallback: import modules directly
        import src.cli.custom_group as _cg
        import src.core.docker as _docker
        import src.core.files as _files

        monkeypatch.setattr(_cg.CustomGroup, "cwd", tmp_path, raising=False)
        monkeypatch.setattr(_files.FileManager, "cwd", tmp_path, raising=False)
        monkeypatch.setattr(
            _docker.ComposeManager, "cwd", tmp_path, raising=False
        )
    return tmp_path


@pytest.fixture()
def no_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent ComposeManager from calling docker on import/usage.

    Mocks `get_services` to return an empty list so the CLI doesn't
    try to call `docker compose` during construction.
    """
    import src.core.docker as _docker

    monkeypatch.setattr(
        _docker.ComposeManager, "get_services", lambda self: [], raising=False  # type: ignore
    )
