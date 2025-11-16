#!/bin/bash
set -e

# Get the total Ram amount on the container
TOTAL_MEMORY_MB=$(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024))
if [ -f /sys/fs/cgroup/memory.max ] && [ "$(cat /sys/fs/cgroup/memory.max)" != "max" ]; then
    TOTAL_MEM_MB=$(($(cat /sys/fs/cgroup/memory.max) / 1024 / 1024))
fi

MIN_RAM=${MIN_HEAP_SIZE:-256} # Defaulted to 256 MB
MAX_RAM=${MAX_HEAP_SIZE:-TOTAL_MEM_MB} # Defaulted to total ram on the container

# Ascii art to give admins a peek at what happens
echo "─╤═════════╡ *** MINECRAFT SERVER *** ╞══════════─"
echo " │"
echo " ├─ SERVER NAME: ${CONTAINER_NAME}"
echo " ├─ TOTAL RAM: ${TOTAL_MEM_MB}MB"
echo " ├─ ALLOCATED RAM: -Xmx${MAX_RAM} -Xms${MIN_RAM}"
echo " └─ JAVA ARGS: ${JAVA_ARGS}"
echo ""

# Look for server jar file
if [ ! -f "${SERVER_JAR}" ]; then
    echo ""
    echo "WARNING: ${SERVER_JAR} was not found in ${SERVER_DIR}"
    echo "Mount a server jar or change the current one name to ${SERVER_JAR}"
    echo ""
    exit 1
fi

# Run minecraft with the designated flags
exec java -Xmx${MAX_RAM} -Xms${MIN_RAM} ${JAVA_ARGS} -jar ${SERVER_JAR} nogui
