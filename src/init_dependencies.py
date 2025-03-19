import os
import sys

sys.path.insert(0, 'src')
from core.di import DIContainer
from core.app_config import AppConfig
from modules.command_executor import CommandExecutor
from rich.console import Console


def _find_project_root():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while current_dir != '/':
            if os.path.exists(os.path.join(current_dir, 'main.py')):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        raise RuntimeError('Не удалось определить корневую директорию проекта.')
        return current_dir

def _init_dependencies():
     DIContainer.register('executer', CommandExecutor(use_sudo=True, debug=True))
     DIContainer.register('console', Console())

def _init_storage():
     AppConfig.storage.project_root = _find_project_root()
     AppConfig.load_packages()

def init_app():
     _init_storage()
     _init_dependencies()