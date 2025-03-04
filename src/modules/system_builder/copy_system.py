import os
import time
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.utils import get_project_root

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

def mount_usb(disk):
    console.print('[cyan]Монитирование разделов...[/cyan]')

    live_usb = f'{disk}3'
    efi_part = f'{disk}2'

    executer.run('mkdir -p /mnt/usb')
    executer.run(f'mount {live_usb} /mnt/usb')
    executer.run(f'mkdir -p /mnt/usb/boot/efi')
    executer.run(f'mkdir -p /mnt/usb/boot/grub')
    executer.run(f'mount {efi_part} /mnt/usb/boot/efi')
    console.print('[bold green] Флешка успешно смонтирована![/bold green]')

def copy_system(rootfs: str, destination_copy: str):
    console.print('[cyan]Копирование системы на флешку...[/cyan]')

    project_root = get_project_root()

    rsync_cmd = (
        f"rsync -aAXv --progress {rootfs} {destination_copy} "
        f"--exclude /mnt --exclude /mnt/usb --exclude /dev --exclude /proc --exclude /sys --exclude /tmp --exclude /run --exclude /media --exclude /lost+found --exclude /swap.img --exclude /var/swap.img --exclude /boot/efi/EFI --exclude /boot/grub --exclude /etc/default/grub --exclude /etc/grub.d --exclude {project_root}"
    )

    executer.run(rsync_cmd, capture_output=False)

    copy_files = ['passwd', 'shadow', 'group', 'gshadow']

    for file in copy_files:
        executer.run(f'cp -p /etc/{file} {destination_copy}/etc/', capture_output=False)

    executer.run(f'cp -p --remove-destination /etc/resolv.conf {destination_copy}/etc/', capture_output=False)

    console.print('[bold green]Система успешно скопирована![/bold green]')