<!-- omit in toc -->
# Manager
The command in the manager command group are:
- [Up](#up)
- [Down](#down)
- [Start](#start)
- [Stop](#stop)
- [Backup](#backup)

## Up
The Up command is the one you should use to start the services for the first time or after updating the host files.<br>
This command takes up to 2 arguments:
- `--attached`: Flag to run containers in attached mode.
- `--detach-keys`: Combination of keys to detach from the container terminal.

## Down
The Down command is the one you should use to delete the docker containers.<br>
This command take up to one argument:
- `--rm-volumes`: Flag to remove the volumes attached to the containers.
```{warning}
Running down will more than likely make you loose the files inside the containers, its recommended to run a backup always.
```

## Start
The start command is the one you should use to start the containers when they have already been built.

## Stop
The stop command is the one you should use to stop the containers without removing the containers.
```{warning}
Running stop will more than likely make you loose the files of containers that run without volumes, its recommended to run a backup always.
```

## Backup
The backup command is the one you should use to create backup files of the files inside the containers.<br>
This command will save a `.tar` file of every minecraft server and if theres a database running it will save it to a `.sql` file.
```{note}
For running backup command the containers must be up and running
```

## Open
The open command is the one you should use to open the running terminal of your minecraft server.<br>
THis command takes two argument:
- `--server`: Name of the server to attach the terminal to.
- `--detach-keys`: Combination of keys to detach from the container terminal.
