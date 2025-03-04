from rich.console import Console
import os
import datetime
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=False)

def get_project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

def get_distro_name():
    try:
        result = executer.run('lsb_release -isrc', capture_output=True)
        if result:
            return result.lower().split()
        else:
            return ["unknown"]

    except FileNotFoundError as e:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release') as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.strip().split('=')[1].replace('"', '').lower()
        return ["unknown"]

def get_current_date() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")