#!/usr/bin/env bash
# ==================================================
# == Create Project ================================
# ==================================================
#
# An interactive script to help generate a new 
# project folder from one of the examples in this
# repository.
#
# Usage: create-project
#
# ================================================

set -eu -o pipefail

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
REPO_DIR=$(dirname "$SCRIPT_DIR")
PARENT_DIR=$(dirname "$REPO_DIR")
BRANCH_NAME=""
PROJECT_NAME=""
PROJECT_DIR=""

install_gum() {
    if [ -x "$(command -v gum)" ]
    then :
    elif [ "$EUID" -ne 0 ]
    then echo "gum.sh is required - please rerun as sudo so it can be installed" && exit
    else
    echo "gum.sh is required - installing"
    echo 'deb [trusted=yes] https://repo.charm.sh/apt/ /' | sudo tee /etc/apt/sources.list.d/charm.list
    apt update && apt install gum
    fi
}

show_title() {
    gum style \
        --border double \
        --margin "1" \
        --padding "1 2" \
        --align center \
        --width 40 \
        "Create Project"
}


select_branch_name() {
    FG="5"

    if [[ ! $BRANCH_NAME ]]
    then
        printf "Select a %s\\n" "$(gum style 'Project Template:')"
        BRANCH_NAME=$(git branch --format='%(refname:short)' | gum choose)
    fi

    if [[ ! $BRANCH_NAME ]]
    then
        printf 'Error: No template was selected.'
        exit 1
    fi

    printf "%s\n\n" "$(gum style --foreground "$FG" "$BRANCH_NAME")";
    
}

select_project_name() {
    FG="2"

    if [[ "$BRANCH_NAME" == "master" ]]
    then
        DEFAULT="my-project"
    else
        DEFAULT="my-$BRANCH_NAME-project"
    fi
    
    printf "Enter a %s\n" \
        "$(gum style 'Project Name:')"
    PROJECT_NAME=$(gum input --placeholder "$DEFAULT")
    PROJECT_NAME=${PROJECT_NAME:=$DEFAULT}
    printf "%s\n\n" \
        "$(gum style --foreground "$FG" "$PROJECT_NAME")"
}

select_project_folder() {
    FG="3"
    PROJECT_DIR="$PARENT_DIR/$PROJECT_NAME"

    printf "Project will be created at:\n%s\n" \
        "$(gum style --foreground "$FG" "$PROJECT_DIR")"
}

confirm_creation() {
    # "$(gum style --border normal --margin "1" --padding "1 2" --align left 
    gum confirm "Continue?"
}


create_project() {
    git clone \
        --quiet \
        --single-branch \
        --branch "$BRANCH_NAME" \
        "$REPO_DIR" \
        "$PROJECT_DIR"

    cd "$PROJECT_DIR"
    rm -rf .git
    rm ./scripts/create-project.sh
    git init --quiet
    printf "\nProject was created successfuly\n"
}

open_project() {
    if 
        [ ! -x "$(command -v code)" ]
    then 
        :
    elif 
        [ "$(gum confirm "Open in VSCode?" )" ]
    then
         :
    elif 
        [ -x "$(command -v devcontainer)" ]
    then 
        devcontainer build "$PROJECT_DIR"
        #TODO: devcontainer open doesnt work
        code "$PROJECT_DIR"
    else 
        code "$PROJECT_DIR"
    fi
}


clear
install_gum
show_title
select_branch_name
select_project_name
select_project_folder
confirm_creation
create_project
open_project