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

        grub_config_content = f'''
set timeout=5
set default=0

menuentry "Live System" {{
    linux /live/vmlinuz boot=live
    initrd /live/initrd.img
        }}
        '''

        uefi_grub_cfg = os.path.join(uefi_boot, 'grub.cfg')
        with open(uefi_grub_cfg, 'w') as grub_file:
            grub_file.write(grub_config_content)

        grub_config_path = os.path.join(self.live_iso_path, 'boot/grub/grub.cfg')
        with open(grub_config_path, 'w') as grub_file:
            grub_file.write(grub_config_content)

        shutil.copy2(self.rootfs_squash_path, f'{self.live_iso_path}/live')
        shutil.copy2(self.vmlinuz_path, f'{self.live_iso_path}/live')
        shutil.copy2(self.initrd_path, f'{self.live_iso_path}/live')

        self.executer.run(f'grub-mkimage -o {os.path.join(uefi_boot, "BOOTx64.EFI")} -O '
                  'x86_64-efi --prefix=/boot/grub '
                  'iso9660 part_gpt part_msdos ext2 normal linux search search_label search_fs_uuid search_fs_file '
                  'gfxterm gfxmenu all_video efi_gop efi_uga')
        
        bios_img = os.path.join(bios_boot, 'eltorito.img')
        self.executer.run(f'grub-mkimage -o {bios_img} -O i386-pc --prefix=/boot/grub '
                  'biosdisk iso9660 part_msdos ext2 normal linux search '
                  'search_fs_uuid search_fs_file multiboot')
        
        self.executer.run(f'xorriso -as mkisofs '
                  '-iso-level 3 -full-iso9660-filenames '
                  '-volid "LIVE_SYSTEM" '
                  '-eltorito-boot boot/grub/i386-pc/eltorito.img '
                  '-no-emul-boot -boot-load-size 4 -boot-info-table '
                  '-eltorito-platform x86 '
                  '-eltorito-alt-boot '
                  '-eltorito-platform efi --efi-boot EFI/BOOT/BOOTx64.EFI '
                  '-no-emul-boot '
                  '-isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin '
                  '-partition_offset 16 '
                  f'-o {self.live_iso_path}/live_system.iso {self.live_iso_path}')

    def copy_live_system_to_usb(self, usb_mount_path):

        self.executer.run(f'mkdir -p {usb_mount_path}/live')

        shutil.copy2(self.rootfs_squash_path, f'{usb_mount_path}/live')
        shutil.copy2(self.vmlinuz_path, f'{usb_mount_path}/live')
        shutil.copy2(self.initrd_path, f'{usb_mount_path}/live')

        self.console.print(f'[cyan]Копирую систему на флешку {usb_mount_path}...[/cyan]')

        self.console.print('[bold green]Система успешно скопирована![/bold green]')