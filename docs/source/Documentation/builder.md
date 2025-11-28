<!-- omit in toc -->
# Builder
The commands in the builder command group are:
- [Create](#create)
- [Update](#update)
- [Build](#build)

## Create
The create command is the one you should use when starting a project, it will give an error if a data.json is found in the CWD to prevent overwritting existing projects.<br>
This command will ask you for prompts you must fill out to write the data to a json file.<br>
This command takes one argument:
- --network: Flag to state the creation of a network, this will force to create a porxy server and at least one extra server.

## Update
The update command is the one you should use to remove, add or change the data in the data.json. You must need to run create before using this command or you will be prompted an error.<br>
This command takes four arguments:
- `--add`: Flag to use when
- `--remove`: Flag to use when removing a service.
- `--change`: Flag to use the change mode of prompts, where prompts will be defaulted to the values in the `data.json` file.
- `--service`: Parameter to specify the name of the service to edit
```{note}
`--service` parameter does not work with `--add` since `--service` only accepts names of existing services.
```

## Build
The build command is the one you should use in case the create or update commands failed building all the resources for the project.
