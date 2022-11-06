#!/usr/bin/env bash

# Start pytest-watch with the given arguments
pytest-watch --poll --runner "pytest $*"