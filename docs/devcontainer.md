# Devcontainer

Notes on the devcontainer implementation

- Heavy use of `pip` and `apt` caching in the [Dockerfile](../Dockerfile) using the [buildx cache](https://docs.docker.com/build/cache/)

- Heavy use of [targets](https://docs.docker.com/build/building/multi-stage/) in the [Dockerfile](../Dockerfile) to speed up builds

- Separate Dev/Prod/Tests images in the [Dockerfile](../Dockerfile)