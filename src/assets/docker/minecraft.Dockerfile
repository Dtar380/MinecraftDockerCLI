FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache bash vim

# Create the runtime user first so we can chown copied files to them.
RUN adduser -D -h /home/serverUser -s /bin/bash serverUser

# Set SERVER_DIR and switch WORKDIR before copying application data
ENV SERVER_DIR=/home/serverUser
WORKDIR $SERVER_DIR

# Copy server data into the user's server directory
COPY ./data .

# Install entrypoint and normalize line endings
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh
RUN sed -i 's/\r$//' /usr/local/bin/run.sh

# Ensure logs and server dir are owned by the non-root user
RUN mkdir -p /logs $SERVER_DIR && chown -R serverUser:serverUser /logs $SERVER_DIR
USER serverUser

SHELL ["/bin/bash", "-c"]
CMD ["/bin/bash"]

ENTRYPOINT ["/usr/local/bin/run.sh"]
