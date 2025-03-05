import os
import shutil
import datetime
import time
from rich.console import Console
from rich.table import Table
from modules.command_executor import CommandExecutor

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
    
    def list_disks(self):
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
    
    def prepare_usb(self, disk):
        confirm = console.input(f'[bold red]Выбран диск {disk}. Все данные будут удалены! Продолжить? (yes/no): [/bold red]')
        if confirm.lower() != 'yes':
            console.print('[yellow]Отмена операции.[yellow]')
            return False
        
        
        console.print(f'[yellow]Отмонтирование разделов на {disk}...[/yellow]')
        partitions = executer.run(f'lsblk -lno NAME,MOUNTPOINT | grep "^$(basename {disk})[0-9]" | awk "{{print $1}}"')

        if partitions:
            for part in partitions.splitlines():
                part_path = f'/dev/{part}'
                executer.run(f'umount {part_path}', show_err=False)
                console.print(f'[green]Отмонтирован:[/green] {part_path}')
        else:
            console.print(f'[yellow]Разделы не были смонтированы.[/yellow]')


        
        console.print('[cyan]Шаг 1: Очистка флешки и создание GPT-разметки[/cyan]')
        executer.run(f'parted -s {disk} mklabel gpt')

        console.print('[cyan]Шаг 2: Создание разделов[/cyan]')
        executer.run(f'parted -s {disk} mkpart bios_grub 1MiB 2MiB')
        executer.run(f'parted -s {disk} set 1 bios_grub on')
        executer.run('partprobe')
        time.sleep(1)

        executer.run(f'parted -s {disk} mkpart primary fat32 2MiB 514MiB')
        executer.run('partprobe')
        time.sleep(1)
        executer.run(f'parted -s {disk} set 2 esp on')

        executer.run(f'parted -s {disk} mkpart primary ext4 514MiB 100%')

        console.print('[cyan]Шаг 3: Форматирование разделов[/cyan]')
        executer.run('partprobe')
        time.sleep(2)
        executer.run(f'mkfs.vfat -I -F32 {disk}2 -n EFI')
        executer.run(f'mkfs.ext4 -F {disk}3 -L LIVE_USB')

        console.print('[bold green]Флешка успешно подготовлена![/bold green]')
        return True
    
    def copy_to_usb(self, disk, usb_mount_point):
        if not self.rootfs_path:
            raise ValueError('Сначала вызови copy_system или create_build_directory!')
        
        console.print('[cyan]Монитирование разделов...[/cyan]')

        live_usb = f'{disk}3'
        efi_part = f'{disk}2'

        executer.run(f'mkdir -p {usb_mount_point}')
        executer.run(f'mount {live_usb} {usb_mount_point}')
        executer.run(f'mkdir -p {usb_mount_point}/boot/efi')
        executer.run(f'mkdir -p {usb_mount_point}/boot/grub')
        executer.run(f'mount {efi_part} {usb_mount_point}/boot/efi')
        console.print('[bold green] Флешка успешно смонтирована![/bold green]')
        
        console.print(f'[cyan]Копирую систему на флешку {usb_mount_point}...[/cyan]')
        executer.run(f'rsync -aAXv --progress {self.rootfs_path}/ {usb_mount_point}/', capture_output=False)

        console.print('[bold green]Система успешно скопирована![/bold green]')