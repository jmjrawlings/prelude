#!/usr/bin/env bash

set -eo pipefail

SCRIPT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
REQ=$(dirname "$SCRIPT")/requirements

for ENV in prod test dev
do
  start_time=$SECONDS
  input_file="$REQ/requirements-$ENV.in"
  output_file="$REQ/requirements-$ENV.txt"
  
  echo -n "Compiling $ENV requirements ..."
    
  pip-compile \
    --resolver=backtracking  \
    --output-file "$output_file" \
    $input_file \
    2>/dev/null

  end_time=$SECONDS
  count=$(grep -c "^[a-Z]" ${output_file})
  elapsed="$(( end_time - start_time ))"
    
  echo "\r${count} packages in ${elapsed}s"
done
