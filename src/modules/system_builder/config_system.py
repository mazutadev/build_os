from rich.console import Console
import shutil
import os
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

def install_grub(disk):
    console.print('[cyan]Установка GRUB...[/cyan]')
    make_dirs()
    mount_dirs()
    try:
        executer.run('chroot /mnt/usb apt update', capture_output=False)
        executer.run('chroot /mnt/usb apt install grub-efi grub-pc-bin grub-efi-amd64-bin grub-efi-amd64 grub-common grub2-common -y', capture_output=False)

        executer.run('chroot /mnt/usb grub-install --target=x86_64-efi --efi-directory=/boot/efi --boot-directory=/boot --removable --recheck', capture_output=False)
        executer.run(f'chroot /mnt/usb grub-install --target=i386-pc --boot-directory=/boot --recheck {disk}', capture_output=False)
        console.print('[bold green]GRUB установлен![/bold green]')
    finally:
        umount_dirs()


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

def make_dirs():
    dirs = ['dev', 'proc', 'sys', 'run', 'tmp', 'mnt', 'media']

    for dir in dirs:
        executer.run(f'mkdir -p /mnt/usb/{dir}')

    executer.run('chmod 1777 /mnt/usb/tmp')

def mount_dirs():
    dirs = ['dev', 'proc', 'sys', 'run']

    for dir in dirs:
        executer.run(f'mount --bind /{dir} /mnt/usb/{dir}')


def umount_dirs():
    dirs = ['dev', 'proc', 'sys', 'run']

    for dir in dirs:
        executer.run(f'umount /mnt/usb/{dir}')
    

def install_casper():
    make_dirs()
    mount_dirs()
    console.print('[cyan]Установка casper в Live-систему...[/cyan]')
    try:
        executer.run('chroot /mnt/usb apt update', capture_output=False)
        executer.run('chroot /mnt/usb apt install -y casper', capture_output=False)
        console.print('[bold green]casper установлен![/bold green]')
    finally:
        umount_dirs()