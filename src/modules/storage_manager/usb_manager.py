import os
import shutil
import datetime
import time
from rich.console import Console
from rich.table import Table
from modules.command_executor import CommandExecutor, CommandResult
from modules.utils import Utils

class USBManager:
    def __init__(self, usb_mount_path='/mnt/usb', console=None, executer=None):
        self.executer = executer if executer else CommandExecutor(use_sudo=True, debug=True)
        self.console = console if console else Console()
        self.usb_mount_path = self._make_usb_mount_point(usb_mount_path=usb_mount_path)
        Utils.list_disks()
        self.disk = self._disk_init()

    def prepare_usb(self):
        if self._confirm():

            self.umount_partitions()
            self._wipe_usb()
            self._create_partitions()
            self._format_partitions()
            self.console.print('[bold green]Флешка успешно подготовлена![/bold green]')
            
            return True
    
    def _confirm(self):
        confirm = self.console.input(f'[bold red]Выбран диск {self.disk}. Все данные будут удалены! Продолжить? (yes/no): [/bold red]')
        if confirm.lower() != 'yes':
            self.console.print('[yellow]Отмена операции.[yellow]')
            return False
        return True

    def _make_usb_mount_point(self, usb_mount_path):
        self.executer.run(f'mkdir -p {usb_mount_path}')
        return usb_mount_path

    def _disk_init(self):
        return input('Введите устройсво (например, /dev/sdb):').strip()

    def _wipe_usb(self):
        self.console.print(f'[red]Полное удаление всех разделов на {self.disk}[/red]')
        self.executer.run(f'wipefs --all --force {self.disk}')
        self.executer.run(f'sgdisk --zap-all {self.disk}')
        self.executer.run(f'dd if=/dev/zero of={self.disk} bs=1M count=10')
        self.console.print(f'[green]Флешка {self.disk} очищена![/green]')

    def _create_partitions(self):
        self.console.print('[cyan]Шаг 1: Очистка флешки и создание GPT-разметки[/cyan]')
        self.executer.run(f'parted -s {self.disk} mklabel gpt')

        self.console.print('[cyan]Шаг 2: Создание разделов[/cyan]')
        self.executer.run(f'parted -s {self.disk} mkpart bios_grub 1MiB 2MiB')
        self.executer.run(f'parted -s {self.disk} set 1 bios_grub on')
        self.executer.run('partprobe')
        time.sleep(1)

        self.executer.run(f'parted -s {self.disk} mkpart primary fat32 2MiB 514MiB')
        self.executer.run('partprobe')
        time.sleep(1)
        self.executer.run(f'parted -s {self.disk} set 2 esp on')

        self.executer.run(f'parted -s {self.disk} mkpart primary ext4 514MiB 100%')

    def mount_partition(self):
        self.console.print('[cyan]Монитирование разделов...[/cyan]')

        live_usb = f'{self.disk}3'
        efi_part = f'{self.disk}2'

        self.executer.run(f'mount {live_usb} {self.usb_mount_path}')
        self.executer.run(f'mkdir -p {self.usb_mount_path}/boot/efi')
        self.executer.run(f'mkdir -p {self.usb_mount_path}/boot/grub')
        self.executer.run(f'mount {efi_part} {self.usb_mount_path}/boot/efi')
        self.console.print('[bold green] Флешка успешно смонтирована![/bold green]')

    def _format_partitions(self):
        self.console.print('[cyan]Шаг 3: Форматирование разделов[/cyan]')
        self.executer.run('partprobe')
        time.sleep(2)
        self.executer.run(f'mkfs.vfat -I -F32 {self.disk}2 -n EFI')
        self.executer.run(f'mkfs.ext4 -F {self.disk}3 -L LIVE_USB')

    def umount_partitions(self):
        self.console.print(f'[yellow]Отмонтирование разделов на {self.disk}...[/yellow]')
        partitions: CommandResult = self.executer.run(f'lsblk -lno NAME,MOUNTPOINT | grep "^$(basename {self.disk})[0-9]" | awk "{{print $1}}"')

        if partitions:
            for part in partitions.stdout.splitlines():
                part_path = f'/dev/{part}'
                self.executer.run(f'umount {part_path}', show_err=False)
                self.console.print(f'[green]Отмонтирован:[/green] {part_path}')
        else:
            self.console.print(f'[yellow]Разделы не были смонтированы.[/yellow]')

    def copy_to_usb(self, rootfs_path:str):        
        
        self.console.print(f'[cyan]Копирую систему на флешку {self.usb_mount_path}...[/cyan]')
        self.executer.run(f'rsync -aAXv --progress {rootfs_path}/ {self.usb_mount_path}/', capture_output=False)

        self.console.print('[bold green]Система успешно скопирована![/bold green]')

    