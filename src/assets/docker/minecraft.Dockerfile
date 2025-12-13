FROM eclipse-temurin:21-jre-alpine

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    vim \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR $SERVER_DIR
COPY ./data .

COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

RUN useradd --create-home serverUser
USER serverUser

SHELL ["/bin/bash", "-c"]
CMD ["/bin/bash"]
RUN chsh -s /bin/bash serverUser

ENTRYPOINT ["/usr/local/bin/run.sh"]
