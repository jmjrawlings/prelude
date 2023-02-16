# ========================================================
# key arguments
# ========================================================
ARG PYTHON_VERSION=3.10
ARG PYTHON_VENV=/opt/venv
ARG NODE_VERSION=19
ARG GH_CLI_VERSION=0.23.0
ARG DAGGER_VERSION=0.3.10
ARG USER_NAME=harken
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG USER_HOME=/home/$USER_NAME
ARG DISTRO=debian
ARG DISTRO_VERSION=bullseye

# ========================================================
# distro-base
# ========================================================
FROM ${DISTRO}:${DISTRO_VERSION} as distro-base

ARG DEBIAN_FRONTEND=noninteractive

# Install core packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    openssh-client \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ========================================================
# dagger-base
# ========================================================
FROM distro-base as dagger-base

ARG DAGGER_VERSION
WORKDIR /usr/local
RUN curl -sfL https://releases.dagger.io/dagger/install.sh | sh \
    && echo ${DAGGER_VERSION}

# ========================================================
# gh-base
# ========================================================
FROM distro-base as gh-base

ARG GH_CLI_VERSION
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt update \
    && apt install gh -y \
    && rm -rf /var/lib/apt/lists/* \
    && echo "$GH_CLI_VERSION"

# ========================================================
# node-base
# ========================================================
FROM node:${NODE_VERSION} as node-base

ARG DEBIAN_FRONTEND=noninteractive
RUN npm install -g @devcontainers/cli

# ========================================================
# python-base
# ========================================================
FROM python:${PYTHON_VERSION}-slim as python-base

ARG PYTHON_VENV
ARG DEBIAN_FRONTEND=noninteractive
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create the python virtual environment
RUN python -m venv ${PYTHON_VENV}
ENV PATH="$PYTHON_VENV/bin:$PATH"

# Install pip-tools
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install pip-tools

# ********************************************************
# * Base
# ********************************************************
FROM python:${PYTHON_VERSION}-slim AS base

ARG USER_GID
ARG USER_UID
ARG USER_HOME
ARG USER_NAME

ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_CACHE_DIR=1

ARG DEBIAN_FRONTEND=noninteractive

# Add a non-root user
RUN groupadd --gid ${USER_GID} ${USER_NAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USER_NAME} \
    && apt-get update \
    && apt-get install -y sudo \
    && echo ${USER_NAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER_NAME} \
    && chmod 0440 /etc/sudoers.d/${USER_NAME}


# ========================================================
# python-test
# ========================================================
FROM python-base as python-dev

COPY requirements/dev.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip-sync ./requirements.txt \
    && rm ./requirements.txt

# ========================================================
# Dev
#
# Devcontainer
# ========================================================
FROM base AS dev

ARG PYTHON_VENV
ARG USER_NAME
ARG USER_GID
ARG USER_UID
ARG USER_HOME=/home/$USER_NAME
ARG REQUIREMENTS_TXT
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=$PYTHON_VENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Enable keeping apt packages so we can use docker caching
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' \
    | tee /etc/apt/apt.conf.d/keep-cache

# Install core packages
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    autojump \
    curl \
    fonts-powerline \
    git \    
    gnupg2 \
    htop \                                                  
    inotify-tools \
    less \
    locales \
    lsb-release \
    micro \
    openssh-client \
    tree \
    wget \
    zsh \    
    && rm -rf /var/lib/apt/lists/*

# Install Docker CE CLI
RUN --mount=type=cache,target=/var/cache/apt \
    curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose
RUN LATEST_COMPOSE_VERSION=$(curl -sSL "https://api.github.com/repos/docker/compose/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")') \
    && curl -sSL "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Install Docker Buildx
COPY --from=docker/buildx-bin:latest /buildx /usr/libexec/docker/cli-plugins/docker-buildx

# Use docker buildx as default
RUN docker buildx install    

# Give Docker access to the non-root user
RUN groupadd docker \
    && usermod -aG docker ${USER_NAME}

# Install oh-my-zsh and Powerlevel10k
USER ${USER_NAME}
WORKDIR ${USER_HOME}
COPY .devcontainer/.p10k.zsh .p10k.zsh
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.3/zsh-in-docker.sh)" -- \
    -p git \
    -p docker \
    -p autojump \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions && \
    echo "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh" >> ~/.zshrc && \
    .oh-my-zsh/custom/themes/powerlevel10k/gitstatus/install

# Install Node
COPY --from=node-base /usr/lib /usr/lib
COPY --from=node-base /usr/local/share /usr/local/share
COPY --from=node-base /usr/local/lib /usr/local/lib
COPY --from=node-base /usr/local/include /usr/local/include
COPY --from=node-base /usr/local/bin /usr/local/bin

# Install GH
COPY --from=gh-base /usr/bin/gh /usr/local/bin/gh

# Install dagger
COPY --from=dagger-base /usr/local/bin/dagger /usr/local/bin/dagger

# Install Python dependencies
COPY --from=python-dev \
    --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV} \
    ${PYTHON_VENV}

CMD zsh


# ========================================================
# python-test
# ========================================================
FROM python-base as python-test

COPY requirements/test.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip-sync ./requirements.txt \
    && rm ./requirements.txt

# ========================================================
# Test 
#
# This target contains python source code, testing code 
# and all dependencies required to run the test suite.
# ========================================================
FROM base as test

ARG USER_NAME
ARG USER_GID
ARG USER_UID
ARG USER_HOME
ARG APP_DIR=$USER_HOME/app
ARG PYTHON_VENV

USER ${USER_NAME}

RUN mkdir $APP_DIR
WORKDIR $APP_DIR

COPY src src
COPY tests tests 
COPY pytest.ini .

# Install Python dependencies
COPY --from=python-test \
    --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV}\
    ${PYTHON_VENV}

ENV VIRTUAL_ENV=$PYTHON_VENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

ENTRYPOINT pytest

# ========================================================
# python-prod 
# ========================================================
FROM python-base as python-prod

COPY requirements/prod.txt ./requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip-sync ./requirements.txt \
    && rm ./requirements.txt

# ========================================================
# Prod 
# 
# This target contains only the python source code and 
# packages required to run the app.
# 
# The goal here is the smallest and fastest image possible
# ========================================================
FROM base as prod

ARG USER_NAME
ARG USER_GID
ARG USER_UID
ARG USER_HOME
ARG APP_DIR=$USER_HOME/app
ENV PYTHONOPTIMIZE=2
ENV PYTHONDONTWRITEBYTECODE=0
ARG PYTHON_VENV

USER ${USER_NAME}

RUN mkdir $APP_DIR
WORKDIR ${APP_PATH}

COPY ./src .

# Install Python dependencies
COPY --from=python-prod \
    --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV} \
    ${PYTHON_VENV}

ENV VIRTUAL_ENV=$PYTHON_VENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"