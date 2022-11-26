#!/usr/bin/env bash

set -eo pipefail

SCRIPT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
REQ=$(dirname "$SCRIPT")/requirements

for ENV in prod test dev
do
  start_time=$SECONDS
  input_file="$REQ/requirements-$ENV.in"
  output_file="$REQ/requirements-$ENV.txt"
  
  echo -n "Compiling $ENV requirements ... "
    
  pip-compile \
    --resolver=backtracking  \
    --output-file "$output_file" \
    --pip-args "--no-binary shapely geos" \
    $input_file 
    # \    2>/dev/null

  end_time=$SECONDS
  count=$(grep -c "^[a-Z]" ${output_file})
  elapsed="$(( end_time - start_time ))"
    
  echo "${count} packages in ${elapsed}s"
done

start_time=$SECONDS
echo "Syncing environment ... "
pip-sync "$REQ/requirements-dev.txt"
end_time=$SECONDS
elapsed="$(( end_time - start_time ))"
echo "Syncing environment took ${elapsed}s"
