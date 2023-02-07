"""
build.py

Build steps defined using dagger-io
"""

import sys
import anyio
import dagger
from dagger import Client, Config, Container
from pathlib import Path
from typing import Union, Optional

client: Client

home = Path(__file__).parent.parent.resolve()
src = home / 'src'
tests = home / 'tests'
docs = home / 'docs'


async def build_container(target: str):
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
    container = await build_container('dev')

    devcon_version = await container.with_exec(['devcontainer', '--version']).stdout()
    print(f"Devcontainer={devcon_version}")

    docker_version = await container.with_exec(['docker', '--version']).stdout()
    print(f"Docker={docker_version}")


async def build_prod_container():
    return await build_container('prod')


async def build_test_container():
    return await build_container('test')    


async def build_containers():
    await build_dev_container()
    await build_prod_container()
    await build_test_container()

       
import typer
app = typer.Typer()



from functools import wraps
import asyncio

def typer_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@typer_async
async def main(cmd: Optional[str] = typer.Argument(None)):
    global client
    config = dagger.Config(log_output=sys.stderr)
    async with dagger.Connection(config) as client:
        client = client
        
        await build_containers()

if __name__ == "__main__":
    typer.run(main)
    