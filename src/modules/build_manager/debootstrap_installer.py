import os
from rich.console import Console
from modules.command_executor import CommandExecutor

class DebootStrapInstaller:
    def __init__(self, console=None, executer=None, project_root=None, rootfs_path=None):
        self.console = console or Console()
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)

        if not project_root:
            raise RuntimeError('Не могу получить путь корневой директории проекта.')
        if not rootfs_path:
            raise RuntimeError('Не могу получить путь к rootfs устанавливаемой системы')
        
        self.project_root = project_root
        self.rootfs_path = rootfs_path

        self.console.print('[cyan]Проверка debootstrap...[/cyan]')
        self.executer.run('dpkg -s debootstrap || apt install -y debootstrap', capture_output=False)

    def _is_system_installed(self):
        required_dirs = ['bin', 'sbin', 'lib', 'etc']
        os_release_file = os.path.join(self.rootfs_path, 'etc', 'os-release')

        if not os.path.exists(self.rootfs_path) or not all(os.path.exists(os.path.join(self.rootfs_path, d)) for d in required_dirs):
            return False
        
        return os.path.exists(os_release_file)

    def install(self, distro, release, arch, force_reinstall=False):
        if self._is_system_installed():
            self.console.print(f'[bold yellow]Система уже установлена в {self.rootfs_path}[/bold yellow]')

            if not force_reinstall:
                self.console.print('[bold green]Переход к настройке существующей системы...[/bold green]')
                return True
            self.console.print('[bold red]Перезаписываю систему![/bold red]')
            self.executer.run(f'rm -rf {self.rootfs_path}')

        self.console.print(f'[cyan]Запуск debootstrap: {distro} {release} ({arch}) {self.rootfs_path}[/cyan]')
        os.makedirs(self.rootfs_path, exist_ok=True)

        cmd = f'debootstrap --arch={arch} {release} {self.rootfs_path} http://archive.ubuntu.com/ubuntu'
        self.executer.run(cmd, capture_output=False)

        self.console.print('[green]Debootstrap завершен![/green]')
        
        if self._is_system_installed():
            return True
        else:
            return False