import os
import shutil
from rich.console import Console

from modules.command_executor import CommandExecutor

class FileManager:
    def __init__(self, executer: CommandExecutor = None, 
                 console: Console = None, project_root: str = None, 
                 rootfs_path: str = None, squashfs_path = None, live_iso_path=None):
        self.executer = executer if executer else CommandExecutor(use_sudo=True, debug=True)
        self.console = console if console else Console()
        self.project_root = project_root
        self.rootfs_path = rootfs_path
        self.squashfs_path = squashfs_path
        self.live_iso_path = live_iso_path
        self.usb_manager = None

        if not project_root:
            raise RuntimeError('Не могу определить путь к директории проекта')
        if not rootfs_path:
            raise RuntimeError('Не могу определить путь к директории RootFS сборки')
        
        self._find_files_paths()
        
    def _find_files_paths(self):
        self.boot_dir_path = os.path.join(self.rootfs_path, 'boot')
        self.rootfs_squash_path = os.path.join(self.squashfs_path, 'filesystem.squashfs')
        self.vmlinuz_path = vmlinuz_path = os.path.join(self.boot_dir_path,'vmlinuz')
        self.initrd_path = os.path.join(self.boot_dir_path,'initrd.img')
        self.grub_i386_path = os.path.join(self.rootfs_path, '/usr/lib/grub/i386-pc')
        self.grub_x86_64_efi = os.path.join(self.rootfs_path, '/usr/lib/grub/x86_64-efi')
        
    def make_squashfs_root(self):
        if not self.project_root:
            raise RuntimeError('Не могу определить путь к директории проекта')
        if not self.squashfs_path:
            raise RuntimeError('Не могу определить путь к директории сборки squashfs')
        if not self.rootfs_path:
            raise RuntimeError('Не могу определить путь к директории RootFS сборки')
        
        exclude_dirs = ['proc', 'sys', 'dev', 'run', 'mnt', 'media', 'tmp', 'var/tmp']
        exclude_flags = " ".join([f'-e {d}' for d in exclude_dirs])

        self.console.print(f'[cyan]Создаю Squashfs из директории: {self.squashfs_path}')

        self.executer.run(f'mksquashfs {self.rootfs_path} {self.squashfs_path}/filesystem.squashfs -comp xz -Xbcj x86 -processors $(nproc) -all-root', capture_output=False)

    def make_iso_file(self):
        bios_boot = os.path.join(self.live_iso_path, 'boot/grub/i386-pc')
        uefi_boot = os.path.join(self.live_iso_path, 'EFI/BOOT')

        os.makedirs(bios_boot, exist_ok=True)
        os.makedirs(uefi_boot, exist_ok=True)

        # 📌 Создаем grub.cfg для BIOS и UEFI
        grub_config_content = '''
set timeout=5
set default=0

menuentry "Live System" {
    linux /live/vmlinuz boot=live toram
    initrd /live/initrd.img
}
'''

        for cfg_path in [os.path.join(uefi_boot, 'grub.cfg'), os.path.join(self.live_iso_path, 'boot/grub/grub.cfg')]:
            with open(cfg_path, 'w') as grub_file:
                grub_file.write(grub_config_content)

        # 📌 Копируем файлы системы
        os.makedirs(f'{self.live_iso_path}/live', exist_ok=True)
        shutil.copy2(self.rootfs_squash_path, f'{self.live_iso_path}/live/filesystem.squashfs')
        shutil.copy2(self.vmlinuz_path, f'{self.live_iso_path}/live/vmlinuz')
        shutil.copy2(self.initrd_path, f'{self.live_iso_path}/live/initrd.img')

        self.executer.run(f'cp {self.grub_i386_path}/* {self.live_iso_path}/boot/grub/i386-pc/')

        # 📌 Генерируем UEFI-загрузчик
        self.executer.run(f'grub-mkimage -o {uefi_boot}/BOOTX64.EFI --format=x86_64-efi --prefix="/boot/grub" part_gpt part_msdos fat iso9660 normal linux configfile search search_fs_file echo test all_video gfxterm font terminal')

        # 📌 Генерируем ISO
        self.executer.run(f'grub-mkrescue -o {self.live_iso_path}/livecd.iso {self.live_iso_path} --xorriso=/usr/bin/xorriso --grub-mkimage=/usr/bin/grub-mkimage --modules="linux normal iso9660 search search_label search_fs_uuid search_fs_file multiboot"')


    def copy_live_system_to_usb(self, usb_mount_path):

        self.executer.run(f'mkdir -p {usb_mount_path}/live')

        shutil.copy2(self.rootfs_squash_path, f'{usb_mount_path}/live')
        shutil.copy2(self.vmlinuz_path, f'{usb_mount_path}/live')
        shutil.copy2(self.initrd_path, f'{usb_mount_path}/live')

        self.console.print(f'[cyan]Копирую систему на флешку {usb_mount_path}...[/cyan]')

        self.console.print('[bold green]Система успешно скопирована![/bold green]')