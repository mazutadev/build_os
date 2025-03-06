import os
import time
from rich.console import Console
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

class CopyManager:
    def __init__(self, excludes: list, project_root: str, build_dir: str, root_fs: str):
        self.project_root = project_root
        self.build_dir = build_dir
        self.excludes = excludes
        self.build_root_fs_path = None
        
    def copy_system_to_build_root(self, source='/', exclude=None):
        if not self.build_dir:
            raise ValueError('Сначала вызови create_build_directory!')
        
        self.build_root_fs_path = os.path.join(self.build_dir, 'root_fs')
        exclude_args = ' '.join([f'--exclude={e}' for e in exclude]) if exclude else ''
        exclude_args += f' --exclude={self.project_root}'

        console.print(f'[cyan]Копирую систему в {self.build_root_fs_path}...[/cyan]')
        executer.run(f'rsync -aAXv {source}* --progress {self.build_root_fs_path} {exclude_args}', capture_output=False)

        copy_files = ['passwd', 'shadow', 'group', 'gshadow']

        for file in copy_files:
            executer.run(f'cp -p {source}etc/{file} {self.build_root_fs_path}/etc/', capture_output=False)

        executer.run(f'cp -p --remove-destination {source}etc/resolv.conf {self.build_root_fs_path}/etc/', capture_output=False)

        console.print(f'[green]Система успешно скопирована в {self.build_root_fs_path}[/green]')

        return self.build_root_fs_path

    