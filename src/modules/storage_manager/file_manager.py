import os
import shutil
from rich.console import Console
from rich.table import Table

from modules.command_executor import CommandExecutor

class FileManager:
    def __init__(self, executer: CommandExecutor = None, 
                 console: Console = None, project_root: str = None, 
                 rootfs_path: str = None):
        self.executer = executer if executer else CommandExecutor(use_sudo=True, debug=True)
        self.console = console if console else Console()
        self.project_root = project_root
        self.rootfs_path = rootfs_path

        if not project_root:
            raise RuntimeError('Не могу опередлить путь к директории проекта')
        if not rootfs_path:
            raise RuntimeError('Не могу определить путь к директории RootFS сборки')
        
        
        
        def make_squashfs_root(self, squash_dir: str):
            if not project_root:
                raise RuntimeError('Не могу опередлить путь к директории проекта')
            if not squash_dir:
                raise RuntimeError('Не могу определить путь к директории сборки')
            if not self.rootfs_path:
                raise RuntimeError('Не могу определить путь к директории RootFS сборки')
            
            exlude_dirs = ['proc', 'sys', 'dev', 'run', 'mnt', 'media', 'tmp', 'var/tmp']
            exlude_flags = " ".join([f'-e {d}' for d in exlude_dirs])

            self.executer.run(f'mksquashfs {self.rootfs_path} {squash_dir}/rootfs.squashfs'
                               '-comp xz -Xbcj x86 -processors $(nproc) -all-root {exlude_flags}', 
                               capture_output=False)