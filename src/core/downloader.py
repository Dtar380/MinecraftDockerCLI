#################################################
# IMPORTS
#################################################
from __future__ import annotations

from pathlib import Path
from shutil import copyfileobj
from typing import Any

from requests.sessions import Session  # type: ignore

#################################################
# CODE
#################################################
dicts = dict[str, Any]


class Downloader:

    def __init__(self, api: str, headers: dicts | None = None) -> None:
        self.session = Session()

        if headers:
            self.session.headers.update(headers)

        self.api = api.rstrip("/")

    def __build_url(self, endpoint: str) -> str:
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.api}/{endpoint.lstrip('/').rstrip('/')}"

    def get(self, endpoint: str, **kwargs: dict[str, Any]) -> Any:
        url = self.__build_url(endpoint)
        response = self.session.get(url, **kwargs)  # type: ignore
        response.raise_for_status()
        return response.json()

    def download_latest(
        self,
        endpoint: str,
        path: Path,
        jar_file: str,
        version: str | None = None,
    ) -> None:
        versions = self.get(endpoint)
        if not versions:
            return
        try:
            if not version:
                version = list(versions.get("versions").values())[0][0]
            endpoint += f"/versions/{version}"
        except Exception:
            return

        builds = self.get(endpoint)
        if not builds:
            return
        try:
            build = list(builds.get("builds"))[0]
            endpoint += f"/builds/{build}"
        except Exception:
            return

        final = self.get(endpoint)
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
        out_path = path.joinpath(jar_file)
        self.__download_file(download_url, out_path)

    def __download_file(self, endpoint: str, path: Path) -> None:
        url = self.__build_url(endpoint)

        with self.session.get(url, stream=True) as response:
            response.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                copyfileobj(response.raw, f)
