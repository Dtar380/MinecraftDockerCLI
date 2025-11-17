FROM eclipse-temurin:21-jdk-jammy

ENV CONTAINER_NAME=""
ENV SERVER_DIR=/server
ENV SERVER_JAR=""
ENV JAVA_ARGS=""
ENV MIN_HEAP_SIZE=""
ENV MAX_HEAP_SIZE=""

COPY ./data /server
WORKDIR /server

COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

ENTRYPOINT ["/usr/local/bin/run.sh"]
