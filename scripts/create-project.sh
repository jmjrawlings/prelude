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

check_gum_installed() {
    if [ ! -x "$(command -v gum)" ]
    then
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
        --width 50 \
        "Prelude" \
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

    if [[ ! $PROJECT_NAME ]] 
    then

        if [[ "$BRANCH_NAME" == "master" ]]
        then
            DEFAULT="my-project"
        else
            DEFAULT="my-$BRANCH_NAME-project"
        fi

        printf "Enter a %s\n" \
            "$(gum style 'Project Name:')"
        PROJECT_NAME=$(gum input --placeholder "$DEFAULT") 
    fi

    if [[ ! $PROJECT_NAME ]]
    then
        printf 'Error: No project name was provided.'
        exit 1
    fi

    printf "%s\n\n" \
        "$(gum style --foreground "$FG" "$PROJECT_NAME")"
}

select_project_folder() {
    FG="3"
    PROJECT_DIR="$PARENT_DIR/$PROJECT_NAME"

    printf "Project will be created at:%s\n\n\n" \
        "$(gum style --foreground "$FG" "$PROJECT_DIR")"
}

confirm_creation() {
    gum confirm
}

do_create() {

    # gum spin --spinner dot \
    #          --title "Cloning Project Template" \
    #          -- \
    git clone \
        --depth=1 \
        --single-branch \
        --branch "$BRANCH_NAME" \
        "$REPO_DIR" \
        "$PROJECT_DIR"

    cd "$PROJECT_DIR"
    rm -rf .git
    rm ./scripts/create-project.sh
    git init
    printf "Success!\n"
}

clear
check_gum_installed
show_title
select_branch_name
select_project_name
select_project_folder
confirm_creation
do_create