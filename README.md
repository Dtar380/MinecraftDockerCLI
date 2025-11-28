<!-- omit in toc -->
# MinecraftDockerCLI
<!-- omit in toc -->
## Set up your Minecraft network blazingly fast

<div align="center">
    <img alt="license" title="License" src="https://custom-icon-badges.demolab.com/github/license/Dtar380/MinecraftDockerCLI?style=for-the-badge&logo=law&logoColor=white&labelColor=1155BA&color=236AD3" height=30>
    <img alt="stars" title="stars" src="https://custom-icon-badges.demolab.com/github/stars/Dtar380/MinecraftDockerCLI?style=for-the-badge&logo=star&logoColor=white&label=STARS&labelColor=9133D4&color=A444E0" height=30>
    <img alt="downloads" title="downloads" src="https://img.shields.io/pypi/dm/MinecraftDockerCLI?style=for-the-badge&logo=download&logoColor=white&label=Downloads&labelColor=488207&color=55960C" height=30>
    <img alt="Visitors" title="Visitors" src="https://viewcounterpython.onrender.com/Dtar380/MinecraftDockerCLI">
    <img alt="open issues" title="open issues" src="https://custom-icon-badges.demolab.com/github/issues/Dtar380/MinecraftDockerCLI?style=for-the-badge&logo=issue-opened&logoColor=white&label=open%20issues&labelColor=CE4630&color=E05D44" height=30>
</div>

**MinecraftDockerCLI** is a python CLI application to allow minecraft server admins to set up in a fast and easy way a server or a network using docker containers.
**MinecraftDockerCLI** is orientated towards minecraft server admins that administrate networks, since a single server cannot fully use the advantages of Docker containers. Docker containers make minecraft networks easier and cleaner because of how docker containers work and intercomunicate on the same machine.

<!-- omit in toc -->
## :bookmark_tabs: **Table of Contents**
- [:blue\_heart: **Main Feautures**](#blue_heart-main-feautures)
- [:arrow\_down: **Installation**](#arrow_down-installation)
- [:wrench: **Tips \& Troubleshooting**](#wrench-tips--troubleshooting)
- [:memo:  **Working On**](#memo--working-on)
- [:open\_file\_folder: **Kown Issues**](#open_file_folder-kown-issues)
- [:scroll: **License**](#scroll-license)
- [:money\_with\_wings: **Sponsorship**](#money_with_wings-sponsorship)

## :blue_heart: **Main Feautures**
- **Full Minecraft servers Containerization**
- **Prompt based data input**
- **Up/Down, Start/Stop docker commands implementation**
- **SQL database compatibility**
- **Web servers compatibility**
- **Backups for Minecraft Servers and Databases**

## :arrow_down: **Installation**

**Prerequisites:**
- Docker Engine (Docker Desktop on Windows) running and configured.
- Docker Compose (bundled with modern Docker Desktop installations).
- Python 3.13+ and `pip`.

**Recommended Installation:**

```shell
# Create a Virtual Environment
python3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the python package
pip install MinecraftDockerCLI
```
<br>

**Clone repo:**

Extra requirement: `Poetry`.

```shell
# Clone the repository
git clone https://github.com/Dtar380/Minecraft-Dockerfile-CLI.git
cd Minecraft-Dockerfile-CLI

poetry install
```

> [!NOTE]
> When running the program you would need to be using the poetry environment and run it like `poetry run MinecraftDockerCLI`

## :wrench: **Tips & Troubleshooting**
- Ensure Docker Desktop is running and you can run `docker ps` without errors before invoking the CLI.
- On Windows, run PowerShell as Administrator or ensure your user has permissions for Docker.
- If `data.json` is missing, run `builder create` first to scaffold services.

## :memo:  **Working On**
Currently resolving issues and developing the unit tests for future updates.

Already Planned releases
| VERSION | INCLUDES                      |
|---------|-------------------------------|
| 1.0.0   | First release (Do full tests) |

Feel free to open Feature Requests at [issues](https://github.com/Dtar380/WorkspaceAutomation/issues/new/choose).

## :open_file_folder: **Kown Issues**
There is no known issues on the project, you can submit yours to [issues](https://github.com/Dtar380/MinecraftDockerCLI/issues/new/choose).

## :scroll: **License**
This project is distributed under the MIT license.
See the [LICENSE](LICENSE).

## :money_with_wings: **Sponsorship**
You can support me and the project with a donation to my Ko-Fi.
