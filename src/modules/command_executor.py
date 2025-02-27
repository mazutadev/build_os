import subprocess
from typing import Optional, List
from rich.console import Console

console = Console()

class CommandExecutor:
    def __init__(self, use_sudo: bool = False, debug: bool = False):
        self.use_sudo = use_sudo
        self.debug = debug

    def run(self, command: str, capture_output: bool = True) -> Optional[str]:
        full_command = f'sudo {command}' if self.use_sudo else command

        if self.debug:
            console.print(f'[blue]Выполняю команду:[/blue] {full_command}')
        
        try:
            result = subprocess.run(full_command, shell=True, 
                                    text=True, 
                                    capture_output=capture_output, 
                                    check=True)
            
            if capture_output:
                return result.stdout.strip()
            
            return None
        
        except subprocess.CalledProcessError as e:
            console.print(f'[red]Ошибка при выполнении команды:[/red] {full_command}')
            console.print(f'[red]Ошибка:[/red] {e.stderr.strip()}')
            return None
