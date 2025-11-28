<!-- omit in toc -->
# Editing data manualy
Since the data is stored in a `data.json`, you can edit it manually once the file has been created.<br>
The `data.json` file has the following structure:
- compose
  - [Servers](#servers)
  - [Database](#database)
  - [Web](#web)
- [Envs](#envs)
- [Server_files](#server-files)

## Servers
A server object is composed of:
- name: name of the container.
- build:
  - context: path where the container will build.
- env_file: path to the `.env` file.
- ports: list of ports opened to the host.
- exposed: list of ports exposed to the containers network.
- resources: The CPUs and RAM allocations and limits for the container.

## Database
The database object can be empty or composed of:
- user: username of the database.
- password: password of the database, used to access it.
- db: the name of the database.

## Web
This object can be true or false, its used to know if a web server will be used, the web server is always built the same way so there are no variables to take into account.

## Envs
A env object is composed of:
- CONTAINER_NAME: name of the container.
- SERVER_JAR: name of the jar file the server will execute.
- JAVA_ARGS: string of java arguments to run along the jar file.
- MIN and MAX heap sizes: Heap sizes used to run along the jar file.
- HOST_PORTS: Dictionary where keys are specified names and the values are ports.

## Server Files
A server files object is composed of:
- name: name of the container.
- server:
  - jar_file: name of the jar file the server will execute.
  - type: Type of server to download (velocity, folia, paper).
  - version: Version of the sever type to download.
