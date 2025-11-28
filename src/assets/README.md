 __  __ _____ _   _ ______ _____ _____            ______ _______   _____   ____   _____ _  ________ _____     _____ _      _____
|  \/  |_   _| \ | |  ____/ ____|  __ \     /\   |  ____|__   __| |  __ \ / __ \ / ____| |/ /  ____|  __ \   / ____| |    |_   _|
| \  / | | | |  \| | |__ | |    | |__) |   /  \  | |__     | |    | |  | | |  | | |    | ' /| |__  | |__) | | |    | |      | |
| |\/| | | | | . ` |  __|| |    |  _  /   / /\ \ |  __|    | |    | |  | | |  | | |    |  < |  __| |  _  /  | |    | |      | |
| |  | |_| |_| |\  | |___| |____| | \ \  / ____ \| |       | |    | |__| | |__| | |____| . \| |____| | \ \  | |____| |____ _| |_
|_|  |_|_____|_| \_|______\_____|_|  \_\/_/    \_\_|       |_|    |_____/ \____/ \_____|_|\_\______|_|  \_\  \_____|______|_____|

**READ BEFORE USING THE APP.**

# START
If this file is in your Current Working Directory (CWD), it means your files built correctly, you should still check if your project has the following structure:
+---docker-compose.yml
+---README.md
+---data.json
\---backup
\---servers
|    \---`server name`
|       +---.env
|       +---.dockerignore
|       +---Dockerfile
|       +---run.sh
|       \---data
|           +---eula.txt
|           +---`.jar` file
\---web
    \---backend
    |   +---.dockerignore
    |   +---Dockerfile
    \---frontend
        +---.dockerignore
        +---Dockerfile

# Minecraft Configs
If you didnt setup a network, you will have a one and only container, you can always configure it running it on your host inside the data folder, and then up the container once you finished configuring

If you setup creating a network you need to know the following things:
- The proxy will be done inside the velocity config like this:<br>
  `{server_name} = {service_name}:port`<br>
  Where:
  - server_name: is anything you want.
  - service_name: is the docker container service name.
  - port: is the minecraft port you exposed on the container.
- To connect a database you will set it up like: `database:5432`
- Your host machine should have forwarded the port you added to your proxy.
- To connect to the server you will need to use the public IP of the host and the port you assigned to your proxy.