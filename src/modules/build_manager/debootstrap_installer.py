import os
from rich.console import Console
from modules.command_executor import CommandExecutor

class DebootStrapInstaller:
    def __init__(self, console=None, executer=None):
        self.console = console or Console()
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)

        self.console.print('[cyan]Проверка debootstrap...[/cyan]')
        self.executer.run('dpkg -s debootstrap || apt install -y debootstrap', capture_output=False)

    def _is_system_installed(self, rootfs_path):
        required_dirs = ['bin', 'sbin', 'lib', 'etc']
        os_release_file = os.path.join(rootfs_path, 'etc', 'os-release')

        if not os.path.exists(rootfs_path) or not all(os.path.exists(os.path.join(rootfs_path, d)) for d in required_dirs):
            return False
        
        return os.path.exists(os_release_file)

    def install(self, rootfs_path, distro, release, arch, force_reinstall=False):
        if self._is_system_installed(rootfs_path=rootfs_path):
            self.console.print(f'[bold yellow]Система уже установлена в {rootfs_path}[/bold yellow]')

            if not force_reinstall:
                self.console.print('[bold green]Переход к настройке существующей системы...[/bold green]')
                return True
            self.console.print('[bold red]Перезаписываю систему![/bold red]')
            self.executer.run(f'rm -rf {rootfs_path}')

        self.console.print(f'[cyan]Запуск debootstrap: {distro} {release} ({arch}) {rootfs_path}[/cyan]')
        os.makedirs(rootfs_path, exist_ok=True)

        cmd = f'debootstrap --arch={arch} {release} {rootfs_path} http://archive.ubuntu.com/ubuntu'
        self.executer.run(cmd, capture_output=False)

        self.console.print('[green]Debootstrap завершен![/green]')
        
        if self._is_system_installed(rootfs_path=rootfs_path):
            return True
        else:
            return False