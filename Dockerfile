# ********************************************************
# * Key Arguments
# ********************************************************
ARG PYTHON_VERSION=3.10
ARG PYTHON_VENV=/opt/venv
ARG NODE_VERSION=19
ARG APP_PATH=/app
ARG USER_NAME=harken
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG OPT_PATH=/opt
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
ENV PIP_NO_CACHE_DIR=1
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

RUN pip install pip-tools

WORKDIR ${PYTHON_VENV}


# ********************************************************
# * Base Layer
# *
# * Dependencies and environment variables used
# * by other targets.
# ********************************************************
FROM python:${PYTHON_VERSION}-slim

ARG PYTHON_VENV
ARG USER_NAME
ARG USER_GID
ARG USER_UID
ARG APP_PATH
ARG OPT_PATH
ARG MINIZINC_HOME

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=$PYTHON_VENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Add a non-root user
RUN groupadd --gid ${USER_GID} ${USER_NAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USER_NAME} \
    && apt-get update \
    && apt-get install -y sudo \
    && echo ${USER_NAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER_NAME} \
    && chmod 0440 /etc/sudoers.d/${USER_NAME}

# Create an assign app path
RUN mkdir $APP_PATH && chown -R $USER_NAME $APP_PATH

# Install core packages
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

# Give Docker access to the non-root user
RUN groupadd docker \
    && usermod -aG docker ${USER_NAME}

# Install Github CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && sudo apt update \
    && sudo apt install gh -y \
    && rm -rf /var/lib/apt/lists/*

# Install Developer packages
RUN apt-get update \
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
RUN echo 'deb [trusted=yes] https://repo.charm.sh/apt/ /' | tee /etc/apt/sources.list.d/charm.list \
    && apt-get update \
    && apt-get install -y gum \
    && rm -rf /var/lib/apt/lists/*

# Install zsh & oh-my-zsh
USER ${USER_NAME}
WORKDIR /home/$USER_NAME
COPY .devcontainer/.p10k.zsh .p10k.zsh
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.3/zsh-in-docker.sh)" -- \
    -p git \
    -p docker \
    -p autojump \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions && \
    echo "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh" >> ~/.zshrc && \
    .oh-my-zsh/custom/themes/powerlevel10k/gitstatus/install

# Install NodeJS
COPY --from=node-base /usr/lib /usr/lib
COPY --from=node-base /usr/local/share /usr/local/share
COPY --from=node-base /usr/local/lib /usr/local/lib
COPY --from=node-base /usr/local/include /usr/local/include
COPY --from=node-base /usr/local/bin /usr/local/bin

# Install Python dependencies
COPY --from=python-base --chown=${USER_UID}:${USER_GID} ${PYTHON_VENV} ${PYTHON_VENV}
COPY requirements.txt ./requirements.txt
RUN pip-sync ./requirements.txt && rm ./requirements.txt

CMD zsh