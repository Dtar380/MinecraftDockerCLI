from __future__ import annotations

from typing import Any

dicts = dict[str, Any]

s1: dicts = {
    "name": "server1",
    "build": {"context": "./servers/server1/"},
    "env_file": "./servers/server1/.env",
    "ports": ["25565:25565"],
    "expose": [],
    "resources": {
        "limits": {"cpus": 1, "memory": "1g"},
        "reservations": {"cpus": 1, "memory": "1g"},
    },
}

s2: dicts = {
    "name": "server2",
    "build": {"context": "./servers/server2/"},
    "env_file": "./servers/server2/.env",
    "ports": ["25565:25565"],
    "expose": [],
    "resources": {
        "limits": {"cpus": 1, "memory": "1g"},
        "reservations": {"cpus": 1, "memory": "1g"},
    },
}

e1: dicts = {
    "CONTAINER_NAME": "server1",
    "SERVER_JAR": "server.jar",
    "JAVA_ARGS": "",
    "MIN_HEAP_SIZE": "256M",
    "MAX_HEAP_SIZE": "1024M",
    "HOST_PORTS": {"HOST_PORT": 25565},
}

e2: dicts = {
    "CONTAINER_NAME": "server2",
    "SERVER_JAR": "server.jar",
    "JAVA_ARGS": "",
    "MIN_HEAP_SIZE": "256M",
    "MAX_HEAP_SIZE": "1024M",
    "HOST_PORTS": {"HOST_PORT": 25565},
}

f1: dicts = {
    "name": "server1",
    "server": {"jar_file": "server.jar", "type": "paper", "version": "1.20.1"},
}

f2: dicts = {
    "name": "server2",
    "server": {"jar_file": "server.jar", "type": "paper", "version": "1.20.1"},
}
