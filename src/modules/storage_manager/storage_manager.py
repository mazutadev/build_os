import os
import shutil
import datetime
import time
from rich.console import Console
from rich.table import Table
from modules.command_executor import CommandExecutor
from modules.storage_manager.usb_manager import USBManager
from modules.system_builder.system_builder import SystemBuilder
from modules.storage_manager.copy_manager import CopyManager

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

class StorageManager:
    def __init__(self, project_root=None):
        self.project_root = project_root or self.find_project_root()
        self.build_dir = None
        self.rootfs_path = None

    def find_project_root(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while current_dir != '/':
            if os.path.exists(os.path.join(current_dir, 'main.py')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        raise RuntimeError('Не удалось определить корневую директорию проекта.')
    
    def create_build_directory(self, distro, release, mode):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        build_name = f'{distro}_{release}_{date_str}_{mode}'
        self.build_dir = os.path.join(self.project_root, 'build', build_name)

        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)
            console.print(f'[green]Создана директория сборки: {self.build_dir}[/green]')
        else:
            console.print(f'[yellow]Директория {self.build_dir} уже существует.[/yellow]')

        return self.build_dir
    
    def copy_system(self, source='/', exclude=None):
        if not self.build_dir:
            raise ValueError('Сначала вызови create_build_directory!')
        
        self.rootfs_path = os.path.join(self.build_dir, 'root_fs')
        exclude_args = ' '.join([f'--exclude={e}' for e in exclude]) if exclude else ''
        exclude_args += f' --exclude={self.project_root}'

        console.print(f'[cyan]Копирую систему в {self.rootfs_path}...[/cyan]')
        executer.run(f'rsync -aAXv /* --progress {self.rootfs_path} {exclude_args}', capture_output=False)

        copy_files = ['passwd', 'shadow', 'group', 'gshadow']

        for file in copy_files:
            executer.run(f'cp -p /etc/{file} {self.rootfs_path}/etc/', capture_output=False)

        executer.run(f'cp -p --remove-destination /etc/resolv.conf {self.rootfs_path}/etc/', capture_output=False)

        console.print(f'[green]Система успешно скопирована в {self.rootfs_path}[/green]')

        return self.rootfs_path
    
    def _list_disks(self):
        console.print('[cyan]Доступные диски:[/cyan]')
        output = executer.run('lsblk -o NAME,SIZE,TYPE,MOUNTPOINT -d -n')

        if not output:
            console.print('[red]Не удалось получить список дисков![/red]')
            return
    
        table = Table(title='Список доступных дисков')
        table.add_column('Устройство', justify='left', style='green')
        table.add_column('Размер', justify='right', style='yellow')
        table.add_column('Тип', justify='left', style='cyan')

        for line in output.splitlines():
            cols = line.split()
            if "disk" in cols:
                table.add_row(f'/dev/{cols[0]}', cols[1], cols[2])

        console.print(table)
    
    def deploy_system_to_usb(self, mount_point, deploy: bool):
        if not self.rootfs_path:
            raise ValueError('Сначала вызови copy_system или create_build_directory!')
        
        self._list_disks()
        disk = input('Введите устройсво (например, /dev/sdb):').strip()
        
        usb_manager = USBManager(disk, mount_point)

        if deploy:
            if usb_manager.prepare_usb():
                usb_manager.mount_partition()
                usb_manager.copy_to_usb(self.rootfs_path)

                system_builder = SystemBuilder(rootfs_path=mount_point)

                essential_packages = [
                        'grub-efi', 'grub-pc', 'grub-pc-bin',
                        'grub-efi-amd64-bin', 'grub-efi-amd64', 'grub-common', 'grub2-common'
                    ]

                system_builder.install_packages(essential_packages)
                system_builder.install_grub(disk)
                system_builder.config_grub(mount_point, self.project_root)
                system_builder.config_fstab()
        else:
            usb_manager.mount_partition()
            system_builder = SystemBuilder(rootfs_path=mount_point)

            essential_packages = [
                    'grub-efi', 'grub-pc', 'grub-pc-bin',
                    'grub-efi-amd64-bin', 'grub-efi-amd64', 'grub-common', 'grub2-common'
                ]

            system_builder.install_packages(essential_packages)
            system_builder.install_grub(disk)
            system_builder.config_grub(mount_point, self.project_root)
            system_builder.config_fstab()