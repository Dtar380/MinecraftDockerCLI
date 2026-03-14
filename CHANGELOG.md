# CHANGELOG

All released versions changes will be tracked and documented in this file.

## [1.0.0](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/1.0.0) - 15th March 2026

First official release.
The package passed all implementation tests and it has the planned functionality.
The package has also been tested in a real enviroment and proven succesfull.

## [0.11.0](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.11.0) - 22nd December 2025

Implemented --version flare to show on the CLI the installed version of the app.

### Added

- --version flare

## [0.10.0](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.10.1) - 14st December 2025

Implemented restart command.
Changed Dockerfiles to be more optimised and lightweight.
Fixed some minor bugs.

### Added

- Restart command to the CLI tool.

### Changed

- Dockerfiles

## [0.8](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.8.1) - 29th November 2025

Implemented update web and database functionality

### Changed

- Menu class
- Builder class
- Tests
- Docs

## [0.7](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.7.1) - 28th November 2025

Added a readthedocs documentation. Did a more thorough README.md documentation on assets inside the source.

### Changed

- README.md

### Added

- docs

## [0.6](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.6.0) - 25th November 2025

Added support for web server (python backend, nodejs frontend) and PostgreSQL server.

### Changed

- Builder class
- Manager class
- Menus class
- ComposeManager class
- FileManager class

## [0.5](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.5.2) - 25th November 2025

Changed prompts to be more intuitive and more direct.
Added --verbose flag to avoid console clears.
Added --no-confirm flag to avoid asking for user confirmation.
Added --detach-keys to `up` and `open` commands.

### Changed

- Builder class
- Manager class
- Menus class
- ComposeManager class
- Utils
- Main

### Added

- ParamTypes classes

## [0.4](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.4.0) - 23th November 2025

Added functionality to change a service data having default values on prompts
with the current data as a flag for the update command.

### Changed

- Builder class
- Menus class

## [0.3](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.3.1) - 23th November 2025

Added functionality to download a server.jar using official PaperMC API.
You can download either folia, paper or velocity servers.

### Added

- Downloader class

### Changed

- template.json
- Builder class
- Menus class
- FileManager class

## [0.2](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.2.0) - 23th November 2025

This release implemented unit tests

## [0.1](https://github.com/Dtar380/MinecraftDockerCLI/releases/tag/0.1.7) - 15th November 2025

This is the first release of the MinecraftDockerCLI app.
This release packs all 0.1.X releases, since all releases here are just fixes from the 0.1.0 release.

### Added

- Menus class
- CustomGroup class
- Builder class
- Manager class
- Core functionality
- Utils
- Asset files
