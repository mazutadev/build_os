import os
from core.di import DIContainer
from core.app_config import AppConfig

class DebootStrapInstaller:
    def __init__(self):
        self.console = DIContainer.resolve('console')
        self.executer = DIContainer.resolve('executer')
        
        self.project_root = AppConfig.storage.project_root
        self.rootfs_path = AppConfig.storage.rootfs_path
        self.distro = AppConfig.project_meta.distro
        self.release = AppConfig.project_meta.release
        self.arch = AppConfig.project_meta.arch

        self.console.print('[cyan]Проверка debootstrap...[/cyan]')
        self.executer.run('dpkg -s debootstrap || apt install -y debootstrap', capture_output=False)

    def _is_system_installed(self):
        required_dirs = ['bin', 'sbin', 'lib', 'etc']
        os_release_file = os.path.join(self.rootfs_path, 'etc', 'os-release')

        if not os.path.exists(self.rootfs_path) or not all(os.path.exists(os.path.join(self.rootfs_path, d)) for d in required_dirs):
            return False
        
        return os.path.exists(os_release_file)

    def install(self):
        if self._is_system_installed():
            self.console.print(f'[bold yellow]Система уже установлена в {self.rootfs_path}[/bold yellow]')

            if not AppConfig.project_meta.force_reinstall:
                self.console.print('[bold green]Переход к настройке существующей системы...[/bold green]')
                return True
            self.console.print('[bold red]Перезаписываю систему![/bold red]')
            self.executer.run(f'rm -rf {self.rootfs_path}')

        self.console.print(f'[cyan]Запуск debootstrap: {self.distro} {self.release} ({self.arch}) {self.rootfs_path}[/cyan]')
        os.makedirs(self.rootfs_path, exist_ok=True)

        cmd = f'debootstrap --arch={self.arch} {self.release} {self.rootfs_path} http://archive.ubuntu.com/ubuntu'
        self.executer.run(cmd, capture_output=False)

        self.console.print('[green]Debootstrap завершен![/green]')
        
        if self._is_system_installed():
            return True
        else:
            return False