ARG AA_DOCKER_TAG
FROM $AA_DOCKER_TAG

WORKDIR ${AUTH_HOME}

COPY /conf/requirements.txt requirements.txt
RUN --mount=type=cache,target=~/.cache \
    pip install -r requirements.txt
