import os
import time
from rich.console import Console
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

def mount_usb(disk):
    console.print('[cyan]Монитирование разделов...[/cyan]')

    live_usb = f'{disk}2'
    efi_part = f'{disk}1'

    executer.run('mkdir -p /mnt/usb')

    executer.run(f'mount {live_usb} /mnt/usb')

    executer.run(f'mkdir -p /mnt/usb/boot/efi')

    executer.run(f'mount {efi_part} /mnt/usb/boot/efi')

    console.print('[bold green] Флешка успешно смонтирована![/bold green]')

def copy_system():
    console.print('[cyan]Копирование системы на флешку...[/cyan]')

    rsync_cmd = (
        "rsync -aAXv --progress /* /mnt/usb "
        "--exclude /mnt --exclude /mnt/usb --exclude /dev --exclude /proc --exclude /sys --exclude /tmp --exclude /run --exclude /media --exclude /lost+found --exclude /home/dev-pc/work/build --exclude /home/dev-pc/Downloads --exclude /snap --exclude /srv --exclude /var/www --exclude /var/cache --exclude /swap.img --exclude /var/swap.img"
    )

    executer.run(rsync_cmd, capture_output=False)
    console.print('[bold green]Система успешно скопирована![/bold green]')