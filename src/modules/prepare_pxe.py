from rich.console import Console
import shutil
import os
import datetime
from modules.command_executor import CommandExecutor
from modules.utils import get_project_root, get_distro_name, get_current_date

console = Console()
executer = CommandExecutor(use_sudo=True, debug=False)

def create_build_dir() -> str:
    distro: list = get_distro_name()
    date: str = get_current_date()
    root_path: str = get_project_root()

    if len(distro) > 1:
        path = f'{root_path}/build/{distro[0]}_{distro[1]}_{date}/root_fs'
    else:
        path = f'{root_path}/build/{distro[0]}_{date}/root_fs'
        
    executer.run(f'mkdir -p {path}', capture_output=True)
    return path