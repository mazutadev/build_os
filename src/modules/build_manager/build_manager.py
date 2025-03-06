import os
import datetime
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.storage_manager.storage_manager import StorageManager

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

class BuildManager:
    def __init__(self, operation_type: str, use_sudo=True, debug=True):
        self.console = Console()
        self.executer = CommandExecutor(use_sudo, debug)
        self.storage_manager = StorageManager()
        self.storage_manager.find_project_root()
        self.storage_manager.create_build_directory('ubuntu', 'noble', operation_type)