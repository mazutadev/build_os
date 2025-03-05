import os
import shutil
import datetime
import time
from rich.console import Console
from rich.table import Table
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

class USBManager:
    def __init__(self, disk, usb_mount_point: str):
        self.disk = disk
        self.usb_mount_point = usb_mount_point

    def wipe_usb(self):
        console.print(f'[red]Полное удаление всех разделов на {self.disk}[/red]')
        executer.run(f'wipefs --all --force {self.disk}')
        executer.run(f'sgdisk --zap-all {self.disk}')
        executer.run(f'dd if=/dev/zero of={self.disk} bs=1M count=10')
        console.print(f'[green]Флешка {self.disk} очищена![/green]')

    def prepare_usb(self):
        confirm = console.input(f'[bold red]Выбран диск {self.disk}. Все данные будут удалены! Продолжить? (yes/no): [/bold red]')
        if confirm.lower() != 'yes':
            console.print('[yellow]Отмена операции.[yellow]')
            return False
        
        
        console.print(f'[yellow]Отмонтирование разделов на {self.disk}...[/yellow]')
        partitions = executer.run(f'lsblk -lno NAME,MOUNTPOINT | grep "^$(basename {self.disk})[0-9]" | awk "{{print $1}}"')

        if partitions:
            for part in partitions.splitlines():
                part_path = f'/dev/{part}'
                executer.run(f'umount {part_path}', show_err=False)
                console.print(f'[green]Отмонтирован:[/green] {part_path}')
        else:
            console.print(f'[yellow]Разделы не были смонтированы.[/yellow]')

        self.wipe_usb()

        console.print('[cyan]Шаг 1: Очистка флешки и создание GPT-разметки[/cyan]')
        executer.run(f'parted -s {self.disk} mklabel gpt')

        console.print('[cyan]Шаг 2: Создание разделов[/cyan]')
        executer.run(f'parted -s {self.disk} mkpart bios_grub 1MiB 2MiB')
        executer.run(f'parted -s {self.disk} set 1 bios_grub on')
        executer.run('partprobe')
        time.sleep(1)

        executer.run(f'parted -s {self.disk} mkpart primary fat32 2MiB 514MiB')
        executer.run('partprobe')
        time.sleep(1)
        executer.run(f'parted -s {self.disk} set 2 esp on')

        executer.run(f'parted -s {self.disk} mkpart primary ext4 514MiB 100%')

        console.print('[cyan]Шаг 3: Форматирование разделов[/cyan]')
        executer.run('partprobe')
        time.sleep(2)
        executer.run(f'mkfs.vfat -I -F32 {self.disk}2 -n EFI')
        executer.run(f'mkfs.ext4 -F {self.disk}3 -L LIVE_USB')

        console.print('[bold green]Флешка успешно подготовлена![/bold green]')
        return True
    
    def copy_to_usb(self, rootfs_path:str):        
        
        console.print(f'[cyan]Копирую систему на флешку {self.usb_mount_point}...[/cyan]')
        executer.run(f'rsync -aAXv --progress {rootfs_path}/ {self.usb_mount_point}/', capture_output=False)

        console.print('[bold green]Система успешно скопирована![/bold green]')

    def mount_partition(self):
        console.print('[cyan]Монитирование разделов...[/cyan]')

        live_usb = f'{self.disk}3'
        efi_part = f'{self.disk}2'

        executer.run(f'mkdir -p {self.usb_mount_point}')
        executer.run(f'mount {live_usb} {self.usb_mount_point}')
        executer.run(f'mkdir -p {self.usb_mount_point}/boot/efi')
        executer.run(f'mkdir -p {self.usb_mount_point}/boot/grub')
        executer.run(f'mount {efi_part} {self.usb_mount_point}/boot/efi')
        console.print('[bold green] Флешка успешно смонтирована![/bold green]')