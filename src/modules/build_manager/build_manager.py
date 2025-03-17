import os
import datetime
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.storage_manager.storage_manager import StorageManager
from modules.chroot_manager.chroot_manager import ChrootManager
from modules.build_manager.system_installer import SystemInstaller
from modules.build_manager.system_setup import SystemSetup
from modules.storage_manager.file_manager import FileManager
from modules.storage_manager.usb_manager import USBManager
from modules.build_manager.grub_installer import GrubInstaller
from modules.utils import Utils


class BuildManager:
    def __init__(self, distro, release, arch, method, use_sudo=True, debug=True):
        self.console = Console()
        self.executer = CommandExecutor(use_sudo, debug)
        self.method = method
        self.distro = distro
        self.release = release
        self.arch = arch
        self.ready_to_setup = False
        self.build_dir = None
        self.usb_manager = None
        self.grub_installer = None
        
        self.storage_manager: StorageManager = StorageManager(executer=self.executer, 
                                                              console=self.console, distro=distro, 
                                                              release=release, method=method)
        
        self.rootfs_path = self.storage_manager.rootfs_path
        self.project_root = self.storage_manager.project_root
        
    def install_system(self, method=None, force_reinstall=False):
        try:
            self.installer = SystemInstaller(method=method, executer=self.executer, console=self.console, 
                                            project_root=self.project_root, rootfs_path=self.rootfs_path, 
                                            distro=self.distro, release=self.release, arch=self.arch)
            
            self.ready_to_setup = self.installer.install(force_reinstall=force_reinstall)

        except Exception as e:
            self.console.print(f'[bold red]При установке системы методом: {method} произошла ошибка: {e}[/bold red]')
            return

    def init_system(self, interactive):
        self.chroot_manager = ChrootManager(executer=self.executer, console=self.console, chroot_destination=self.rootfs_path)
        self.system_setup = SystemSetup(executer=self.executer, console=self.console, 
                                        rootfs_path=self.rootfs_path, project_root=self.project_root, 
                                        chroot_manager=self.chroot_manager, distro=self.distro, release=self.release, 
                                        arch=self.arch, hostname='PXE-OS', timezone='Europe/Moscow')
        
        if self.ready_to_setup:
            self.system_setup.init_system(interactive=interactive)

    def install_packages(self):
        self.system_setup.install_packages()

    def prepare_pxe(self):
        self.storage_manager.file_manager.make_squashfs_root()
        self.storage_manager.file_manager.make_iso_file()

    def prepare_usb(self):
        self.usb_manager = USBManager(console=self.console, executer=self.executer)
        self.usb_manager.prepare_usb()
        self.usb_manager.umount_partitions()

        self.grub_installer = GrubInstaller(usb_manager=self.usb_manager, 
                                       console=self.console, executer=self.executer, 
                                       chroot_manager=self.chroot_manager)

        self.grub_installer.install()
        self.grub_installer.config(project_root=self.storage_manager.project_root)

        self.usb_manager.mount_partition()
        self.storage_manager.file_manager.make_squashfs_root()
        self.storage_manager.file_manager.copy_live_system_to_usb(usb_mount_path=self.usb_manager.usb_mount_path)
        
        #usb_manager.umount_partitions()
