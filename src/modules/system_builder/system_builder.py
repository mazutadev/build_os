import os
import shutil
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.chroot_manager.chroot_manager import ChrootManager

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

class SystemBuilder:
    def __init__(self, rootfs_path: str, distro='ubuntu', release='noble', arch='amd64'):
        self.rootfs_path = rootfs_path
        self.distro = distro
        self.release = release
        self.arch = arch
        self.chroot_manager = ChrootManager(rootfs_path)

    def prepare_environment(self):
        console.print('[cyan]Проверка необходимых пакетов...[/cyan]')
        required_packages = ['debootstrap', 'binfmt-support', 'qemu-user-static']

        for pkg in required_packages:
            executer.run(f'dpkgs -s {pkg} || apt install -y {pkg}')

    def run_debootstrap(self):
        console.print('[cyan]Выполняю debootstrap для {self.distro} {self.realease} ({self.arch})[/cyan]')
        executer.run(f'debootstrap --arch={self.arch} {self.release} {self.rootfs_path} http://archive.ubuntu.com/ubuntu/')

    def install_packages(self):
        console.print('[cyan]Устанавливаю необходимые пакеты в chroot[/cyan]')
        essential_packages = [
            'grub-efi', 'grub-pc', 'grub-pc-bin',
            'grub-efi-amd64-bin', 'grub-efi-amd64', 'grub-common', 'grub2-common'
        ]

        packages = ' '.join(essential_packages)

        with self.chroot_manager as chroot:
            #chroot.run_command('/bin/bash')
            chroot.run_command(f'apt update')

            for pkg in essential_packages:
                chroot.run_command(f'apt install -y {pkg}')

    def install_grub(self, disk):
        console.print('[cyan]Настраиваю GRUB в chroot[/cyan]')
        with self.chroot_manager as chroot:
            chroot.run_command('grub-install --target=x86_64-efi --efi-directory=/boot/efi --boot-directory=/boot --removable --recheck')
            chroot.run_command(f'grub-install --target=i386-pc --boot-directory=/boot --recheck {disk}')
            
    def config_grub(self, usb_mount_path, project_root):
        console.print('[cyan]Копирование конфигурации GRUB[/cyan]')

        executer.run(f'mkdir -p {usb_mount_path}/boot/efi/boot/grub')

        print(project_root)

        src_grub_cfg = f'{project_root}/src/configs/grub.cfg'
        src_grub_efi_cfg = f'{project_root}/src/configs/efi_grub.cfg'
        dest_grub_cfg = os.path.join(usb_mount_path, 'boot/grub/grub.cfg')
        dest_efi_grug_cfg = os.path.join(usb_mount_path, 'boot/efi/boot/grub/grub.cfg')
        
        console.print(f'[cyan]Копирование {src_grub_cfg} в {dest_grub_cfg}[/cyan]')
        shutil.copy2(src_grub_cfg,dest_grub_cfg)

        console.print(f'[cyan]Копирование {src_grub_efi_cfg} в {dest_efi_grug_cfg}[/cyan]')
        shutil.copy2(src_grub_efi_cfg,dest_efi_grug_cfg)
        

        console.print('[bold green]grub.cfg скопированы![/bold green]')

    def config_fstab(self):
        console.print('[cyan]Настройка fstab...[/cyan]')

        fstab = """
LABEL=LIVE_USB / ext4 defaults 0 1
tmpfs /tmp tmpfs defaults 0 0
"""

        with open('/mnt/usb/etc/fstab', 'w') as f:
            f.write(fstab)

        console.print('[bold green]fstab настроен[/bold green]')


    def configure_initrd(self):
        console.print('[cyan]Генерирую initrd внутри chroot...[/cyan]')

        with self.chroot_manager as chroot:
            chroot.run_command(f'update-initramfs -c -k all')

    def build(self):
        self.prepare_environment()
        self.run_debootstrap()
        self.install_packages()
        self.configure_initrd()
        self.print('[bold green]Система успешна собрана![/bold green]')