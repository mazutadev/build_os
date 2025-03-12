from rich.console import Console
from rich.table import Table
import os
import datetime
from modules.command_executor import CommandExecutor, CommandResult

class Utils:

    console = Console()
    executer = CommandExecutor(use_sudo=True, debug=True)

    @classmethod
    def list_disks(cls):
        cls.console.print('[cyan]Доступные диски:[/cyan]')
        try:
            output: CommandResult = cls.executer.run('lsblk -o NAME,SIZE,TYPE,MOUNTPOINT -d -n')
        except Exception as e:
            cls.console.print(f'[bold yellow]{e}[/bold yellow]')
            cls.console.print('[red]Не удалось получить список дисков![/red]')
            return            
    
        table = Table(title='Список доступных дисков')
        table.add_column('Устройство', justify='left', style='green')
        table.add_column('Размер', justify='right', style='yellow')
        table.add_column('Тип', justify='left', style='cyan')


        for line in output.stdout.splitlines():
            cols = line.split()
            if "disk" in cols:
                table.add_row(f'/dev/{cols[0]}', cols[1], cols[2])

        cls.console.print(table)