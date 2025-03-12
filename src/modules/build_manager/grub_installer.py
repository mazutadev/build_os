import os
import shutil
from rich.console import Console
from modules.command_executor import CommandResult, CommandExecutor
from modules.chroot_manager.chroot_manager import ChrootManager
from modules.storage_manager.usb_manager import USBManager

class GrubInstaller:
    def __init__(self, usb_manager, console=None, executer=None, chroot_manager: ChrootManager=None):
        self.executer = executer if executer else CommandExecutor(use_sudo=True, debug=True)
        self.console = console if console else Console()
        self.chroot_manager = chroot_manager
        self.usb_manager: USBManager = usb_manager

        if not chroot_manager:
            raise RuntimeError('Не определен объект ChrootManager()')
        
    def install(self):
        pakages = ['grub-efi', 'grub-pc-bin', 'grub-efi-amd64-bin',
                     'grub-efi-amd64', 'grub-common', 'grub2-common']

        self.console.print('[cyan]Установка GRUB...[/cyan]')
        with self.chroot_manager as chroot:
            self.usb_manager.mount_partition()
            chroot.run_command('/bin/bash')
            for pkg in pakages:
                chroot.run_command(f'apt install {pkg} -y')

            chroot.run_command(f'grub-install --target=x86_64-efi --efi-directory={self.usb_manager.usb_mount_path}/boot/efi --boot-directory={self.usb_manager.usb_mount_path}/boot --removable --recheck')
            chroot.run_command(f'grub-install --target=i386-pc --boot-directory={self.usb_manager.usb_mount_path}/boot --recheck {self.usb_manager.disk}')
            #self._config_fstab()
            self.usb_manager.umount_partitions()
        self.console.print('[bold green]GRUB установлен![/bold green]')

    def config(self, project_root):
        self.console.print('[cyan]Копирование конфигурации GRUB[/cyan]')
        self.usb_manager.mount_partition()

        self.executer.run(f'mkdir -p {self.usb_manager.usb_mount_path}/boot/efi/boot/grub')

        src_grub_cfg = f'{project_root}/src/configs/grub.cfg'
        src_grub_efi_cfg = f'{project_root}/src/configs/efi_grub.cfg'
        dest_grub_cfg = os.path.join(self.usb_manager.usb_mount_path, 'boot/grub/grub.cfg')
        dest_efi_grug_cfg = os.path.join(self.usb_manager.usb_mount_path, 'boot/efi/boot/grub/grub.cfg')
        
        self.console.print(f'[cyan]Копирование {src_grub_cfg} в {dest_grub_cfg}[/cyan]')
        shutil.copy2(src_grub_cfg,dest_grub_cfg)

        self.console.print(f'[cyan]Копирование {src_grub_efi_cfg} в {dest_efi_grug_cfg}[/cyan]')
        shutil.copy2(src_grub_efi_cfg,dest_efi_grug_cfg)
        
        self.usb_manager.umount_partitions()
        self.console.print('[bold green]grub.cfg скопированы![/bold green]')

    def _config_fstab(self):
        self.console.print('[cyan]Настройка fstab...[/cyan]')

        fstab = """
tmpfs / tmpfs rw,relatime 0 0
"""

        with open(f'{self.usb_manager.usb_mount_path}/etc/fstab', 'w') as f:
            f.write(fstab)

        self.console.print('[bold green]fstab настроен[/bold green]')
