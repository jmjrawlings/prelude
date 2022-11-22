#!/usr/bin/env bash

set -eo pipefail

SCRIPT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
REQ=$(dirname "$SCRIPT")/requirements

for ENV in prod test dev
do
  start_time=$SECONDS
  echo -n "Compiling $ENV requirements ..."
  pip-compile \
    "$REQ/requirements-$ENV.in" \
    --resolver=backtracking  \
    --output-file "$REQ/requirements-$ENV.txt" \
    2>/dev/null
  end_time=$SECONDS
  elapsed="$(( end_time - start_time ))"
  echo " ${elapsed}s"
done
