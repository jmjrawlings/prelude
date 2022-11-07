# ********************************************************
# * Key Arguments
# ********************************************************
ARG PYTHON_VERSION=3.9
ARG DAGGER_VERSION=0.2.30
ARG PYTHON_VENV=/opt/venv
ARG APP_PATH=/app
ARG USER_NAME=jmjr
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG DEBIAN_FRONTEND=noninteractive

# ********************************************************
# * Python Builder
# ********************************************************
FROM python:${PYTHON_VERSION}-slim as python-builder
ARG PYTHON_VENV
RUN python -m venv ${PYTHON_VENV}


# ********************************************************
# * Base Layer
# *
# * Dependencies and environment variables used
# * by other targets.
# ********************************************************
FROM python:${PYTHON_VERSION}-slim as base

ARG PYTHON_VENV
ARG USER_NAME
ARG USER_GID
ARG USER_UID

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Add a non-root user
RUN groupadd --gid ${USER_GID} ${USER_NAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USER_NAME} \
    && apt-get update \
    && apt-get install -y sudo \
    && echo ${USER_NAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER_NAME} \
    && chmod 0440 /etc/sudoers.d/${USER_NAME}

# Install python virtual env
COPY --from=python-builder --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV} ${PYTHON_VENV}
ENV VIRTUAL_ENV=$PYTHON_VENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
RUN pip install pip-tools

# ********************************************************
# * Dev 
# * 
# * This target contains everything needed for a fully 
# * featured development environment.  It is intended to 
# * be used as a devcontainer via VSCode remote development
# * extension.
# * 
# * See https://code.visualstudio.com/docs/remote/containers
# ********************************************************
FROM base as dev

ARG PYTHON_VENV
ARG USER_NAME
ARG USER_UID
ARG USER_GID
ARG DEBIAN_FRONTEND

USER root

# Install packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        locales \
        lsb-release \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CE CLI
RUN curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose
RUN LATEST_COMPOSE_VERSION=$(curl -sSL "https://api.github.com/repos/docker/compose/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")') \
    && curl -sSL "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Give docker access to the non-root user
RUN groupadd docker \
    && usermod -aG docker ${USER_NAME}

# Install Dagger - TODO: pin version, should be refreshed to due to ARG
ARG DAGGER_VERSION
RUN curl -sfL https://releases.dagger.io/dagger/install.sh | sh \
    && mv ./bin/dagger /usr/local/bin \
    && echo ${DAGGER_VERSION}

# Install Developer packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fonts-powerline \
        openssh-client \
        micro \
        less \
        inotify-tools \
        htop \                                                  
        git \    
        zsh \
    && rm -rf /var/lib/apt/lists/*

# Install zsh & oh-my-zsh
USER ${USER_NAME}
COPY .devcontainer/.p10k.zsh /home/$USER_NAME/.p10k.zsh
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.3/zsh-in-docker.sh)" -- \
    -p git \
    -p docker \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions && \
    echo "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh" >> ~/.zshrc

# Install Python dependencies
COPY ./requirements/requirements-dev.txt ./requirements.txt
RUN pip-sync ./requirements.txt

CMD zsh


# ********************************************************
# * Test 
# *
# * This target contains python source code, testing code 
# * and all dependencies required to run the test suite.
# ********************************************************
FROM base as test

ARG APP_PATH
ARG USER_NAME
ARG USER_GID
ARG USER_UID
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

USER ${USER_NAME}
COPY ./src .
COPY ./tests .
COPY ./pytest.ini .
COPY ./requirements/requirements-test.txt ./requirements.txt
RUN pip-sync ./requirements.txt
CMD pytest


# ********************************************************
# * Prod 
# * 
# * This target contains only the python source code and 
# * packages required to run the app.
# * 
# * The goal here is the smallest and fastest image possible
# ********************************************************
FROM base as prod

ARG APP_PATH
ARG USER_NAME
ARG USER_GID
ARG USER_UID

ENV PYTHONOPTIMIZE=2
ENV PYTHONDONTWRITEBYTECODE=0

USER ${USER_NAME}
COPY ./src .
COPY ./requirements/requirements-prod.txt ./requirements.txt
RUN pip-sync ./requirements.txt