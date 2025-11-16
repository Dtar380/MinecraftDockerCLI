FROM eclipse-temurin:21-jdk-jammy

ENV CONTAINER_NAME=""
ENV SERVER_DIR=""
ENV SERVER_JAR=""
ENV JAVA_ARGS=""
ENV MIN_HEAP_SIZE=""
ENV MAX_HEAP_SIZE=""

WORKDIR $SERVER_DIR

COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

ENTRYPOINT ["/usr/local/bin/run.sh"]
