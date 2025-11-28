# Basic Usage
Once you've installed the program, run `MinecraftDockerCLI --help` to check its installed properly and that you can access it through your temrinal.
```{warning}
If you installed the APP on a Virtual Environment, you must activate the VEnv for it to work.
```

## Using create command
The first command you should use is the create command.<br>
This command one flag to activate network creation. The network creation pormpts will force the creation of a proxy server and will offer creating a database service and a web service with docker containers.<br>
To use this command simply type `MinecraftDockerCLI create` on the terminal and add `--network` if you want to create a network.<br>
After running the command you will have the next structure in your CWD (current working directory):
 - data.json
 - docker-compose.yml
 - README.md
 - backup/
 - servers/
   - `server name`/
     - .dockerignore
     - Dockerfile
     - run.sh
     - data/
       - server.jar (or specified name)
       - eula.txt
 - web/ (if selected)
   - frontend/
     - .dockerignore
     - Dockerfile
   - backend/
     - .dockerignore
     - Dockerfile

## Using docker commands
### Up command
After creating your services you can already run the containers.<br>
To do so follow the next steps:
 - Make sure docker engine and docker compose are running (Docker desktop in windows)
 - Open a terminal in your CWD and run `MinecraftDockerCLI up`
```{warning}
up command will overwrite existing data inside the containers
```

### Start and stop commands
If you've already uped once your containers, you can stop and start them with:
 - `MinecraftDockerCLI start`
 - `MinecraftDockerCLI stop`

### Backup command
To create backups of all service you can run: `MinecraftDockerCLI backup`
```{note}
This command will only run when the services are running, if they are stopped it won't work.
It's recommended to create a backup every time you stop the services
```

### Down command
If you want to remove the docker containers you can use: `MinecraftDockerCLI down`.<br>
This command accepts a `--rm-volumes` flag which will remove the volumes of the docker containers, erasing the data inside them.

## What's next?
This is everything you need to know to use the CLI app, you can read more thorough documentation on this ReadTheDocs.
