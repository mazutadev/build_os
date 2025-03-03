#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"


print_info() {
    echo -e "\e[34m$1\e[0m"
}

print_success() {
    echo -e "\e[32m$1\e[0m"
}

print_warning() {
    echo -e "\e[33m$1\e[0m"
}

print_error() {
    echo -e "\e[31m$1\e[0m"
}


echo $PROJECT_DIR
echo $VENV_DIR
echo $REQUIREMENTS_FILE