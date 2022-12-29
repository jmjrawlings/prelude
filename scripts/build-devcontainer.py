"""
Execute a command
"""

import sys

import anyio

import dagger



async def build():
    config = dagger.Config(log_output=sys.stderr)
    async with dagger.Connection(config) as client:
        
        a = client.directory()


        python = client \
            .container() \
            .from_("node:19") \
            .with_directory()
            .with_exec(["python", "-V"])

        # execute
        version = await python.stdout()

    print(f"Hello from Dagger and {version}")


if __name__ == "__main__":
    anyio.run(build)