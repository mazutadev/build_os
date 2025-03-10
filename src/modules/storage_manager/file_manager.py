import os
import shutil
from rich.console import Console
from rich.table import Table

from modules.command_executor import CommandExecutor
from modules.storage_manager.usb_manager import USBManager

class FileManager:
    def __init__(self, executer: CommandExecutor = None, 
                 console: Console = None, project_root: str = None, 
                 rootfs_path: str = None, squashfs_path = None):
        self.executer = executer if executer else CommandExecutor(use_sudo=True, debug=True)
        self.console = console if console else Console()
        self.project_root = project_root
        self.rootfs_path = rootfs_path
        self.squashfs_path = squashfs_path
        self.usb_manager = None

        if not project_root:
            raise RuntimeError('Не могу определить путь к директории проекта')
        if not rootfs_path:
            raise RuntimeError('Не могу определить путь к директории RootFS сборки')
        
        
    def make_squashfs_root(self):
        if not self.project_root:
            raise RuntimeError('Не могу определить путь к директории проекта')
        if not self.squashfs_path:
            raise RuntimeError('Не могу определить путь к директории сборки squashfs')
        if not self.rootfs_path:
            raise RuntimeError('Не могу определить путь к директории RootFS сборки')
        
        exclude_dirs = ['proc', 'sys', 'dev', 'run', 'mnt', 'media', 'tmp', 'var/tmp']
        exclude_flags = " ".join([f'-e {d}' for d in exclude_dirs])

        self.console.print(f'[cyan]Создаю Squashfs из директории: {self.squashfs_path}')

        self.executer.run(f'mksquashfs {self.rootfs_path} {self.squashfs_path}/rootfs.squashfs -comp xz -Xbcj x86 -processors $(nproc) -all-root {exclude_flags}', capture_output=False)

    def prepare_usb(self, disk=None, usb_mount_point=None):
        if not disk:
            raise RuntimeError('Не указан диск для подготовки к записи системы')
        if not usb_mount_point:
            raise RuntimeError('Не указан точка монтирования диска для подготовки к записи системы')
        
        usb_manager = USBManager(disk=disk, usb_mount_point=usb_mount_point)