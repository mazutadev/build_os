import subprocess
from typing import Optional, List
from rich.console import Console

console = Console()

class CommandResult:
    def __init__(self, stdout, stderr, returncode):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

class CommandExecutor:
    def __init__(self, use_sudo: bool = False, debug: bool = False):
        self.use_sudo = use_sudo
        self.debug = debug

    def run(self, command: str, capture_output: bool = True, show_err: bool = True) -> Optional[str]:
        full_command = f'sudo {command}' if self.use_sudo else command

        if self.debug:
            console.print(f'[blue]▶️ Выполняю команду:[/blue] {full_command}')
        
        result = subprocess.run(full_command, shell=True, 
                                text=True, 
                                capture_output=capture_output, 
                                check=False)

        command_result = CommandResult(
            stdout=result.stdout.strip() if result.stdout else None,
            stderr=result.stderr.strip() if result.stderr else None,
            returncode=result.returncode
        )

        if result.returncode != 0 and show_err:
            console.print(f'[red]× Ошибка при выполнении команды:[/red] {full_command} [bold yellow]returncode: {result.returncode}[/bold yellow]')
            if command_result.stderr:
                console.print(f'[red]Ошибка:[/red] {command_result.stderr}')
                raise RuntimeError(f'Возникла ошибка: {command_result.stderr}')
                
            
        return command_result
