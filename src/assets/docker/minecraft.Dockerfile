FROM eclipse-temurin:21-jre-alpine

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR $SERVER_DIR
COPY ./data .

COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

RUN useradd --create-home serverUser
USER serverUser

ENTRYPOINT ["/usr/local/bin/run.sh"]
