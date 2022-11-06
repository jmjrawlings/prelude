#!/usr/bin/env bash

set -eo pipefail

start_time=$SECONDS
SCRIPT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
REQ=$(dirname "$SCRIPT")/requirements

echo 'Compiling prod requirements..'
pip-compile "$REQ/requirements-prod.in" -o "$REQ/requirements-prod.txt"

echo 'Compiling test requirements..'
pip-compile "$REQ/requirements-test.in" -o "$REQ/requirements-test.txt"

echo 'Compiling dev requirements..'
pip-compile "$REQ/requirements-dev.in" -o "$REQ/requirements-dev.txt"

echo 'Syncing dev environment'
pip-sync "$REQ/requirements-dev.txt"

end_time=$SECONDS
elapsed="$(( end_time - start_time ))"

echo "Requirements updated in $elapsed seconds"
