import os
import datetime
from rich.console import Console
from modules.command_executor import CommandExecutor, CommandResult
from modules.storage_manager.file_manager import FileManager


class StorageManager:
    def __init__(self, project_root=None, executer=None, 
                 console=None, distro=None, release=None, method=None):
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)
        self.console = console or Console()
        self.project_root = project_root or self._find_project_root()
        self.distro = distro
        self.release = release
        self.method = method
        self.build_dir = None
        self.rootfs_path = None
        self.squashfs_path = None
        self.file_manager = None
        self._create_build_directory()
        
    def _find_project_root(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while current_dir != '/':
            if os.path.exists(os.path.join(current_dir, 'main.py')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        raise RuntimeError('Не удалось определить корневую директорию проекта.')
    
    def _create_file_manager(self):
        self.file_manager = FileManager(executer=self.executer, console=self.console, 
                                        project_root=self.project_root, rootfs_path=self.rootfs_path, 
                                        squashfs_path=self.squashfs_path, live_iso_path=self.live_os_path)
    
    def _create_build_directory(self):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        build_name = f'{self.distro}_{self.release}_{date_str}_{self.method}'
        self.build_dir = os.path.join(self.project_root, 'build', build_name)

        # Определяем нужные директории
        directories = {
            'root_fs': os.path.join(self.build_dir, 'root_fs'),
            'squashfs': os.path.join(self.build_dir, 'squashfs'),
            'live_iso': os.path.join(self.build_dir, 'live_iso'),
            'boot': os.path.join(self.build_dir, 'boot'),
            'boot_efi': os.path.join(self.build_dir, 'boot', 'efi')
        }

        # Создаем директории
        for key, path in directories.items():
            self._create_directory(path, f"{key.replace('_', ' ').title()}")

        # Специальные поддиректории для live_iso
        if os.path.exists(directories['live_iso']):
            for subdir in ['live', 'isolinux', 'boot/grub']:
                if not os.path.exists(os.path.join(directories['live_iso'], subdir)):
                    os.makedirs(os.path.join(directories['live_iso'], subdir))
                    self.console.print(f'[green]Созданы поддиректории Live ISO.[/green]')

        self.rootfs_path = directories['root_fs']
        self.squashfs_path = directories['squashfs']
        self.live_os_path = directories['live_iso']
        self.boot_dir = directories['boot']
        self.boot_dir_efi = directories['boot_efi']

        if self.squashfs_path:
            self._create_file_manager()

        return self.build_dir
    
    def _create_directory(self, path, description):
        if not os.path.exists(path):
            os.makedirs(path)
            self.console.print(f'[green]Создана директория {description}: {path}[/green]')
        else:
            self.console.print(f'[yellow]Директория {description}: {path} уже существует.[/yellow]')