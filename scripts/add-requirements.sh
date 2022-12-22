#!/usr/bin/env bash
set -o pipefail

PROD=1
DEV=2
TEST=3
ENV=PROD

help() { 
    echo "Usage: $0 [--dev] [--prod] [--test]" 1>&2
}

PARSED_ARGS=$(getopt -a -n add-requirements -o pdt --long prod,dev,test -- "$@")
VALID_ARGS=$?
if [ "$VALID_ARGS" != "0" ]; then
  help
fi

eval set -- "$PARSED_ARGS"
echo "$PARSED_ARGS"

while :
do
  case "$1" in
    -p | --prod) ENV=PROD ; shift ;;
    -d | --dev)  ENV=DEV  ; shift ;;
    -t | --test) ENV=TEST ; shift ;;
    -- ) shift;  break          ;;
    *  ) echo "Unhandled option: $1"; help ;;
  esac
done

REQ_FILE=""
case $ENV in
  PROD) REQ_FILE="requirements/requirements-prod.in";;
  DEV)  REQ_FILE="requirements/requirements-dev.in";;
  TEST) REQ_FILE="requirements/requirements-test.in";;
esac

echo "$REQ_FILE"


add_package () {
    pkg=$1
    echo "Adding package $pkg"

    # Try and match the whole package as a word
    unconstrained=$(grep -x $pkg $REQ_FILE)

    # Try and match the package plus version specifiation
    constrained=$(grep $pkg== $REQ_FILE)
                        
    if [[ $unconstrained ]]
    then
      echo $unconstrained
    elif [[ $constrained ]]
    then 
      echo $constrained
    else
      echo "$pkg does not exist"
    fi

}

# For each package specified
for pkg in "$@"; do add_package $pkg; done
