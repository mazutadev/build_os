import os
import shutil
from core.di import DIContainer
from core.app_config import AppConfig

class FileManager:
    def __init__(self):
        self.executer = DIContainer.resolve('executer')
        self.console = DIContainer.resolve('console')
        self.project_root = AppConfig.storage.project_root
        self.rootfs_path = AppConfig.storage.rootfs_path
        self.squashfs_path = AppConfig.storage.squashfs_path
        self.live_os_path = AppConfig.storage.live_os_path
        self.usb_manager = None
        
        self._find_files_paths()
        
    def _find_files_paths(self):
        self.boot_dir_path = os.path.join(self.rootfs_path, 'boot')
        self.rootfs_squash_path = os.path.join(self.squashfs_path, 'filesystem.squashfs')
        self.vmlinuz_path = os.path.join(self.boot_dir_path,'vmlinuz')
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
        bios_boot_live = os.path.join(self.live_os_path, 'boot/grub/i386-pc')
        uefi_boot_live = os.path.join(self.live_os_path, 'EFI/BOOT')

        os.makedirs(bios_boot_live, exist_ok=True)
        os.makedirs(uefi_boot_live, exist_ok=True)

        AppConfig.storage.bios_boot_live = bios_boot_live
        AppConfig.storage.uefi_boot_live = uefi_boot_live

        # 📌 Создаем grub.cfg для BIOS и UEFI
        grub_config_content = f'''
set timeout=5
set default=0

menuentry "{AppConfig.project_meta.build_name}" {{
    linux /live/vmlinuz boot=live toram 
    initrd /live/initrd.img
}}
'''

        for cfg_path in [os.path.join(uefi_boot_live, 'grub.cfg'), os.path.join(self.live_os_path, 'boot/grub/grub.cfg')]:
            with open(cfg_path, 'w') as grub_file:
                grub_file.write(grub_config_content)

        # 📌 Копируем файлы системы
        os.makedirs(f'{self.live_os_path}/live', exist_ok=True)
        shutil.copy2(self.rootfs_squash_path, f'{self.live_os_path}/live/filesystem.squashfs')
        shutil.copy2(self.vmlinuz_path, f'{self.live_os_path}/live/vmlinuz')
        shutil.copy2(self.initrd_path, f'{self.live_os_path}/live/initrd.img')

        self.executer.run(f'cp {self.grub_i386_path}/* {self.live_os_path}/boot/grub/i386-pc/')

        # 📌 Генерируем UEFI-загрузчик
        self.executer.run(f'grub-mkimage -o {uefi_boot_live}/BOOTX64.EFI --format=x86_64-efi --prefix="/boot/grub" part_gpt part_msdos fat iso9660 normal linux configfile search search_fs_file echo test all_video gfxterm font terminal')

        # 📌 Генерируем ISO
        self.executer.run(f'grub-mkrescue -o {self.live_os_path}/livecd.iso {self.live_os_path} --xorriso=/usr/bin/xorriso --grub-mkimage=/usr/bin/grub-mkimage --modules="linux normal iso9660 search search_label search_fs_uuid search_fs_file multiboot"')


    def copy_live_system_to_usb(self, usb_mount_path):

        self.executer.run(f'mkdir -p {usb_mount_path}/live')

        shutil.copy2(self.rootfs_squash_path, f'{usb_mount_path}/live')
        shutil.copy2(self.vmlinuz_path, f'{usb_mount_path}/live')
        shutil.copy2(self.initrd_path, f'{usb_mount_path}/live')

        self.console.print(f'[cyan]Копирую систему на флешку {usb_mount_path}...[/cyan]')

        self.console.print('[bold green]Система успешно скопирована![/bold green]')