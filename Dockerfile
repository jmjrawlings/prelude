# ********************************************************
# * Key Arguments
# ********************************************************
ARG PYTHON_VERSION=3.10
ARG PYTHON_VENV=/opt/venv
ARG NODE_VERSION=19
ARG USER_NAME=harken
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG USER_HOME=/home/$USER_NAME
ARG DEBIAN_FRONTEND=noninteractive

# ********************************************************
# * Node Base
# ********************************************************
FROM node:${NODE_VERSION} as node-base
RUN npm install -g @devcontainers/cli

# ********************************************************
# * Python Base
# ********************************************************
FROM python:${PYTHON_VERSION}-slim as python-base

ARG PYTHON_VENV
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=$PYTHON_VENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Create the python virtual environment
RUN python -m venv ${PYTHON_VENV}

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip-tools
RUN --mount=type=cache,target=/root/.cache/pip \
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

# Add a non-root user
RUN groupadd --gid ${USER_GID} ${USER_NAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USER_NAME} \
    && apt-get update \
    && apt-get install -y sudo \
    && echo ${USER_NAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER_NAME} \
    && chmod 0440 /etc/sudoers.d/${USER_NAME}

# ********************************************************
# * Devcontainer
# ********************************************************
FROM python-base as python-dev

COPY requirements/requirements-dev.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip-sync ./requirements.txt \
    && rm ./requirements.txt

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
    curl \
    gnupg2 \
    locales \
    lsb-release \
    wget \
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

# Give Docker access to the non-root user
RUN groupadd docker \
    && usermod -aG docker ${USER_NAME}

# Install Github CLI
RUN --mount=type=cache,target=/var/cache/apt \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt update \
    && apt install gh -y \
    && rm -rf /var/lib/apt/lists/*

# Install Developer packages
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    autojump \
    fonts-powerline \
    openssh-client \
    micro \
    less \
    inotify-tools \
    htop \                                                  
    git \    
    tree \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Install gum.sh
RUN --mount=type=cache,target=/var/cache/apt \
    echo 'deb [trusted=yes] https://repo.charm.sh/apt/ /' | tee /etc/apt/sources.list.d/charm.list \
    && apt-get update \
    && apt-get install -y gum \
    && rm -rf /var/lib/apt/lists/*

# Install Dagger - TODO: pin version, should be refreshed to due to ARG
ARG DAGGER_VERSION
RUN curl -sfL https://releases.dagger.io/dagger/install.sh | sh \
    && mv ./bin/dagger /usr/local/bin \
    && echo ${DAGGER_VERSION}

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

# Install Python dependencies
COPY --from=python-dev \
    --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV} \
    ${PYTHON_VENV}

CMD zsh


# ********************************************************
# * Test 
# *
# * This target contains python source code, testing code 
# * and all dependencies required to run the test suite.
# ********************************************************
FROM python-base as python-test

COPY requirements/requirements-test.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip-sync ./requirements.txt \
    && rm ./requirements.txt

FROM base as test

ARG USER_NAME
ARG USER_GID
ARG USER_UID
ARG USER_HOME
ARG APP_DIR=$USER_HOME/app
ARG PIP_NO_CACHE_DIR=1

USER ${USER_NAME}

# Copy source code
RUN mkdir $APP_DIR
WORKDIR $APP_DIR
COPY ./src .
COPY ./tests .
COPY ./pytest.ini .

# Install Python and dependencies
COPY --from=python-test \
    --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV}\
    ${PYTHON_VENV}

CMD pytest

# ********************************************************
# * Prod 
# * 
# * This target contains only the python source code and 
# * packages required to run the app.
# * 
# * The goal here is the smallest and fastest image possible
# ********************************************************
FROM python-base as python-prod

COPY requirements/requirements-prod.txt ./requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip-sync ./requirements.txt \
    && rm ./requirements.txt

FROM base as prod

ARG USER_NAME
ARG USER_GID
ARG USER_UID
ARG USER_HOME
ARG APP_DIR=$USER_HOME/app
ARG PIP_NO_CACHE_DIR=1
ENV PYTHONOPTIMIZE=2
ENV PYTHONDONTWRITEBYTECODE=0

# Copy source code
USER ${USER_NAME}
RUN mkdir $APP_DIR
WORKDIR ${APP_PATH}
COPY ./src .

# Install Python and dependencies
COPY --from=python-prod \
    --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV} \
    ${PYTHON_VENV}
