#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

echo $PROJECT_DIR
echo $VENV_DIR
echo $REQUIREMENTS_FILE


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


if ! command -v python3 &>/dev/null; then
    print_error "Python3 не найден! Установите Python и запустите скрипт снова."
    exit 1
else
    PYTHON_BIN=$(command -v python3)
    print_success "Python найден: $PYTHON_BIN"
fi

if ! $PYTHON_BIN -c "import venv" &>/dev/null; then
    print_error "Virtualenv не найден. Установите его: pip install virtualenv"
    exit 1
else
    print_success "Virtualenv доступен"
fi

if [ ! -d "$VENV_DIR" ]; then
    print_warning "Виртуальное окружение не найдено. Создаю в $VENV_DIR..."
    $PYTHON_BIN -m venv "$VENV_DIR"
    print_success "Виртуальное окружение создано."
else
    print_success "Виртуальное окружение уже существует."
fi

if [ -f "$REQUIREMENTS_FILE" ]; then
    print_info "Устанавливаю зависимости из requirements.txt..."
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/python" -m pip install -r "$REQUIREMENTS_FILE"
    print_success "Все зависмости установлены."
else
    print_warning "Файл requirements.txt не найден. Пропускаю установку зависимостей."
fi