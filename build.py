"""
build.py

Build steps defined using dagger-io
"""

import sys
import anyio
import dagger
from dagger import Client, Config, Container
from pathlib import Path
from typing import Union

client: Client

home = Path(__file__).parent.resolve()


async def build_docker_image(target):
    """
    Build the docker image for the given target
    """

    
    root = (
        client
        .host()
        .directory(str(home))
    )
        
    container = (
        client
        .container()
        .build(root, target=target)
    )

    python_version = await container.with_exec(['python', '--version']).stdout()
    print(f"{target} container python={python_version}")
    return container

async def build_dev_container():
    global client
    container = await build_docker_image('dev')

    devcon_version = await container.with_exec(['devcontainer', '--version']).stdout()
    print(f"Devcontainer={devcon_version}")

    docker_version = await container.with_exec(['docker', '--version']).stdout()
    print(f"Docker={docker_version}")

    

async def main():
    global client
    config = dagger.Config(log_output=sys.stderr)
    async with dagger.Connection(config) as client:
        client = client
        await build_dev_container()
        await build_docker_image('prod')
        await build_docker_image('test')
       

if __name__ == "__main__":
    anyio.run(main)