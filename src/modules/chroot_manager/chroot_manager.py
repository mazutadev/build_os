from rich.console import Console
import os
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=False)

class ChrootManager:
    def __init__(self, chroot_destination: str):
        self.destination = chroot_destination
        self.mount_points = ['/proc', '/sys', '/dev', '/run', '/tmp']

    def mount(self):
        console.print(f'[cyan]Монтирую системные каталоги в {self.destination}[/cyan]')

        for mount_point in self.mount_points:
            target_path = os.path.join(self.destination, mount_point.lstrip('/'))
            os.makedirs(target_path, exist_ok=True)

            if mount_point == '/dev':
                executer.run(f'mount --bind {mount_point} {target_path}')
            else:
                executer.run(f'mount --bind {mount_point} {target_path}')

        console.print('[green]Все системные каталоги смонтированы![/green]')

    def umount(self):
        console.print(f'[yellow]Отмонтирую системные каталоги из {self.destination}...[/yellow]')

        for mount_point in reversed(self.mount_points):
            target_path = os.path.join(self.destination, mount_point.lstrip('/'))
            executer.run(f'umount -lf {target_path}')

        console.print('[green]Все каталоги успешно отмонтированы.[/green]')

    def run_command(self, command):
        console.print(f'[blue]▶️ Выполняю команду в chroot:[/blue] [italic]{command}[/italic]')

        executer.run(f'chroot {self.destination} {command}', capture_output=False)

    def __enter__(self):
        self.mount()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.umount()