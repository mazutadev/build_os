import os
from rich.console import Console
from modules.command_executor import CommandExecutor

class ChrootManager:
    def __init__(self, chroot_destination: str, executer=None, console=None):
        self.destination = chroot_destination
        self.mount_points = ['/proc', '/sys', '/dev', '/run', '/tmp', '/mnt']
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)
        self.console = console or Console

    def mount(self):
        self.console.print(f'[cyan]Монтирую системные каталоги в {self.destination}[/cyan]')

        for mount_point in self.mount_points:
            target_path = os.path.join(self.destination, mount_point.lstrip('/'))
            os.makedirs(target_path, exist_ok=True)

            if mount_point == '/dev':
                self.executer.run(f'mount --bind {mount_point} {target_path}')
            else:
                self.executer.run(f'mount --bind {mount_point} {target_path}')

        self.console.print('[green]Все системные каталоги смонтированы![/green]')

    def umount(self):
        self.console.print(f'[yellow]Отмонтирую системные каталоги из {self.destination}...[/yellow]')

        for mount_point in reversed(self.mount_points):
            target_path = os.path.join(self.destination, mount_point.lstrip('/'))
            self.executer.run(f'umount -lf {target_path}')

        self.console.print('[green]Все каталоги успешно отмонтированы.[/green]')

    def run_command(self, command):
        self.console.print(f'[blue]▶️ Выполняю команду в chroot:[/blue] [italic]{command}[/italic]')

        try:
            return self.executer.run(f'chroot {self.destination} {command}', capture_output=False)
        except Exception as e:
            self.console.print(f'[red]{e}[/red]')

    def __enter__(self):
        self.mount()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.umount()