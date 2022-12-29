import sys
import anyio
import dagger
from pathlib import Path

home = Path(__file__).parent
home = str(home.absolute())
print(home)


def install_packages(container: dagger.Container, *args):
    command = "apt-get update && apt-get install -y -no-install-recommends"
    command += " ".join(args)
    command += " && rm -rf /var/lib/apt/lists/*"
    return container.with_exec([command])

async def build():
    config = dagger.Config(log_output=sys.stderr)
    
    async with dagger.Connection(config) as client:
        root = (
            client
            .host()
            .directory(home)
        )
        
        container = (
            client
            .container()
            .build(root)
            .with_mounted_directory('/app', root)
            .with_workdir('/app')
        )
        
        devcon_version = await container.with_exec(['devcontainer', '--version']).stdout()
        docker_version = await container.with_exec(['docker', '--version']).stdout()

    print(f"Docker={docker_version} and Devcontainer={devcon_version}")


if __name__ == "__main__":
    anyio.run(build)