from rich.console import Console
import shutil
import os
from modules.command_executor import CommandExecutor
from modules.chroot_manager.chroot_manager import ChrootManager

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

def install_grub(disk):
    console.print('[cyan]Установка GRUB...[/cyan]')

    with ChrootManager('/mnt/usb') as chroot:
        chroot.run_command('apt update')
        chroot.run_command('apt install grub-efi grub-pc-bin grub-efi-amd64-bin grub-efi-amd64 grub-common grub2-common -y')
        chroot.run_command('chroot /mnt/usb grub-install --target=x86_64-efi --efi-directory=/boot/efi --boot-directory=/boot --removable --recheck')
        chroot.run_command(f'chroot /mnt/usb grub-install --target=i386-pc --boot-directory=/boot --recheck {disk}')

    console.print('[bold green]GRUB установлен![/bold green]')

def copy_grub_cfg(usb_mount_path):
    console.print('[cyan]Копирование конфигурации GRUB[/cyan]')

    executer.run(f'mkdir -p {usb_mount_path}/boot/efi/boot/grub')

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

    src_grub_cfg = os.path.join(project_root, 'src/configs/grub.cfg')
    src_grub_efi_cfg = os.path.join(project_root, 'src/configs/efi_grub.cfg')
    dest_grub_cfg = os.path.join(usb_mount_path, 'boot/grub/grub.cfg')
    dest_efi_grug_cfg = os.path.join(usb_mount_path, 'boot/efi/boot/grub/grub.cfg')
    
    console.print(f'[cyan]Копирование {src_grub_cfg} в {dest_grub_cfg}[/cyan]')
    shutil.copy2(src_grub_cfg,dest_grub_cfg)

    console.print(f'[cyan]Копирование {src_grub_efi_cfg} в {dest_efi_grug_cfg}[/cyan]')
    shutil.copy2(src_grub_efi_cfg,dest_efi_grug_cfg)
    

    console.print('[bold green]grub.cfg скопированы![/bold green]')

def config_fstab():
    console.print('[cyan]Настройка fstab...[/cyan]')

    fstab = """
LABEL=LIVE_USB / ext4 defaults 0 1
tmpfs /tmp tmpfs defaults 0 0
"""

    with open('/mnt/usb/etc/fstab', 'w') as f:
        f.write(fstab)

    console.print('[bold green]fstab настроен[/bold green]')