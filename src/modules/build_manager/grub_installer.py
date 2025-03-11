import os
import shutil
from rich.console import Console
from modules.command_executor import CommandResult, CommandExecutor
from modules.chroot_manager.chroot_manager import ChrootManager

class GrubInstaller:
    def __init__(self, console=None, executer=None, chroot_manager: ChrootManager=None):
        self.executer = executer if executer else CommandExecutor(use_sudo=True, debug=True)
        self.console = console if console else Console()
        self.chroot_manager = chroot_manager

        if not chroot_manager:
            raise RuntimeError('Не определен объект ChrootManager()')
        
    def install(self):
        pakages = ['grub-efi', 'grub-pc-bin', 'grub-efi-amd64-bin',
                     'grub-efi-amd64', 'grub-common', 'grub2-common']
        
        self.console.print('[cyan]Установка GRUB...[/cyan]')
        with self.chroot_manager as chroot:
            for pkg in pakages:
                chroot.run_command(f'apt install {pkg} -y')

            chroot.run_command('grub-install --target=x86_64-efi --efi-directory=/boot/efi --boot-directory=/boot --removable --recheck')
            chroot.run_command(f'grub-install --target=i386-pc --boot-directory=/boot --recheck {self.disk}')
        self.console.print('[bold green]GRUB установлен![/bold green]')
