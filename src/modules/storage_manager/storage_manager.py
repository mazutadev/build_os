import os
import datetime
from modules.storage_manager.file_manager import FileManager
from core.app_config import AppConfig
from core.di import DIContainer


class StorageManager:
    def __init__(self):
        self.executer = DIContainer.resolve('executer')
        self.console = DIContainer.resolve('console')
        self.project_root = AppConfig.storage.project_root
        self.distro = AppConfig.project_meta.distro
        self.release = AppConfig.project_meta.release
        self.method = AppConfig.project_meta.method
        self.build_dir = None
        self.rootfs_path = None
        self.squashfs_path = None
        self.file_manager = None
        self._create_build_directory()
            
    def _create_file_manager(self):
        self.file_manager = FileManager()
        DIContainer.register('file_manager', self.file_manager)
    
    def _create_build_directory(self):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        AppConfig.project_meta.build_date = date_str

        build_name = f'{self.distro}_{self.release}_{date_str}_{self.method}'
        AppConfig.project_meta.build_name = build_name

        self.build_dir = os.path.join(self.project_root, 'build', build_name)
        AppConfig.storage.build_dir = build_name

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
            for subdir in ['live', 'boot/grub', 'EFI']:
                if not os.path.exists(os.path.join(directories['live_iso'], subdir)):
                    os.makedirs(os.path.join(directories['live_iso'], subdir))
                    self.console.print(f'[green]Созданы поддиректории Live ISO.[/green]')

        self.rootfs_path = directories['root_fs']
        AppConfig.storage.rootfs_path = self.rootfs_path

        self.squashfs_path = directories['squashfs']
        AppConfig.storage.squashfs_path = self.squashfs_path
        
        self.live_os_path = directories['live_iso']
        AppConfig.storage.live_os_path = self.live_os_path

        self.boot_dir = directories['boot']
        AppConfig.storage.boot_dir = self.boot_dir

        self.boot_dir_efi = directories['boot_efi']
        AppConfig.storage.boot_dir_efi = self.boot_dir_efi

        if self.squashfs_path:
            self._create_file_manager()

        return self.build_dir
    
    def _create_directory(self, path, description):
        if not os.path.exists(path):
            os.makedirs(path)
            self.console.print(f'[green]Создана директория {description}: {path}[/green]')
        else:
            self.console.print(f'[yellow]Директория {description}: {path} уже существует.[/yellow]')