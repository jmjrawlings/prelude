"""
Execute a command
"""

import sys
import anyio
import dagger
from pathlib import Path

home = Path(__file__).parent.parent
home = str(home.absolute())


async def build():
    config = dagger.Config(log_output=sys.stderr)
    
    async with dagger.Connection(config) as client:
        root = client.host().directory(home)
        container = (
            client 
            .container() 
            .from_("node:19") 
            .with_exec(["npm", "install", "-g", "@devcontainers/cli"])
            # .with_exec([f'''
            #     # Install Docker CE CLI
            #     RUN curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
            #     && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
            #     && apt-get update && apt-get install -y --no-install-recommends \
            #     docker-ce-cli \
            #     && rm -rf /var/lib/apt/lists/*
            #     '''])
            .with_exec(["curl -fsSL https://get.docker.com | sh"])
            .with_mounted_directory('/app', root)
            .with_workdir('/app')
            # .with_exec(["devcontainer", "build", "--workspace-folder", "/app"])
        )

        devcon_version = await container.with_exec(['devcontainer', '--version']).stdout()
        docker_version = await container.with_exec(['docker', '--version']).stdout()

    print(f"Docker={docker_version} and Devcontainer={devcon_version}")


if __name__ == "__main__":
    anyio.run(build)