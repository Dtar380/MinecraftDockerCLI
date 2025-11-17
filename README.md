# MinecraftDockerCLI
## Set up your Minecraft network blazingly fast

<div align="center">
    <img alt="license" title="License" src="https://custom-icon-badges.demolab.com/github/license/Dtar380/MinecraftDockerCLI?style=for-the-badge&logo=law&logoColor=white&labelColor=1155BA&color=236AD3" height=30>
    <img alt="stars" title="stars" src="https://custom-icon-badges.demolab.com/github/stars/Dtar380/MinecraftDockerCLI?style=for-the-badge&logo=star&logoColor=white&label=STARS&labelColor=9133D4&color=A444E0" height=30>
    <img alt="downloads" title="downloads" src="https://custom-icon-badges.demolab.com/pypi/dm/MinecraftDockerCLI?style=for-the-badge&logo=download&logoColor=white&label=Downloads&labelColor=488207&color=55960C" height=30>
    <img alt="Visitors" title="Visitors" src="https://viewcounterpython.onrender.com/Dtar380/MinecraftDockerCLI">
    <img alt="open issues" title="open issues" src="https://custom-icon-badges.demolab.com/github/issues/Dtar380/MinecraftDockerCLI?style=for-the-badge&logo=issue-opened&logoColor=white&label=open%20issues&labelColor=CE4630&color=E05D44" height=30>
</div>

**MinecraftDockerCLI** is a python CLI application to allow minecraft server admins to set up in a fast and easy way a server or a network using docker containers.
**MinecraftDockerCLI** is orientated towards minecraft server admins that administrate networks, since a single server cannot fully use the advantages of Docker containers. Docker containers make minecraft networks easier and cleaner because of how docker containers work and intercomunicate on the same machine.

## **Installation**

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

## **Usage**

To use this app you simply need to type `MinecraftDockerCLI` in your terminal followed by the command you want to execute and the options you want to use.

> [!WARNING]
> To ensure the app runs correctly, make sure the ENV you installed the app to is activated and that you are on the folder of your server project.

### **Builder commands**
Create:
- Help: Create all files for the containerization.
- Description: This command will ask the user with prompts everything to build a docker-compose.yml and .envs for all the services the user will run. Running this command on a existing project will overwrite the files.
- Arguments:
    - --network: Flag for creating network insteat of single server (required)

Update:
- Help: Update the contents of the containers.
- Description: This command will either delete a service or add a service with the same method as Create.
- Arguments:
    - --add: Flag to state the addition of a service.
    - --remove: Flag to state the removal of a service.
    - --service: Parameter to specify the name of the service.

Build:
- Help: Build the files for the containerization.
- Description: This command will build the files based on `data.json` in case they were not built when running create.

> [!NOTE]
> None of the Builder commands will build nor start the containers.

### **Manager commands**
Backup:
- Help: Create a backup of the containers.
- Description: This command will create a backup of every service in a tar file with the format `{service_name}_{date}.tar.gz` inside a `.backup` directory.

Up:
- Help: Build the containers and start them. (This will overwrite the data inside with the host data)
- Arguments:
    - --atached: Flag to run the containers in atached mode.

Down:
- Help: Stop the containers and delete them.
- Arguments:
    - --rm-volumes: Flag to remove volumes.

> [!WARNING]
> Running `Up` will overwrite the inside volumes of the container with host ones and down with --rm-files will remove the volumes inside the containers, make sure to create a backup and replace the files on host with the backups every time.

Start:
- Help: Start the containers.
- Description: This command will

Stop:
- Help: Stop the containers.
- Description: This command will

Open:
-

## **Tips & Troubleshooting**
- Ensure Docker Desktop is running and you can run `docker ps` without errors before invoking the CLI.
- On Windows, run PowerShell as Administrator or ensure your user has permissions for Docker.
- If `data.json` is missing, run `builder create` first to scaffold services.

## **Working On**
Currently resolving issues and developing the unit tests for future updates.

Already Planned releases
| VERSION | INCLUDES                                             |
|---------|------------------------------------------------------|
| 0.2.0   | Unit Tests implementation                            |
| 0.3.0   | Extra update functionality to change data.json data  |
| 0.4.0   | Add Paper, Vanilla, Fabric and Forge direct download |
| 1.0.0   | First release (refactor and extra docs)              |

Feel free to open Feature Requests [issues](https://github.com/Dtar380/WorkspaceAutomation/issues/new/choose) to request things related to this concepts such popular IDE's, popular Git services with REST API's (API needed for being able to give support), unwanted types of files and folders generated by WorkSpace creations, etc.

## **Kown Issues**
There is no known issues on the project, you can submit yours to [issues](https://github.com/Dtar380/MinecraftDockerCLI/issues/new/choose).

## **License**
This project is distributed under the MIT license.
See the [LICENSE](LICENSE).

## **Sponsorship**
You can support me and the project with a donation to my Ko-Fi.
