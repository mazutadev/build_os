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


class BuildManager:
    def __init__(self, distro, release, arch, method, use_sudo=True, debug=True):
        self.console = Console()
        self.executer = CommandExecutor(use_sudo, debug)
        self.storage_manager = StorageManager(executer=self.executer)
        self.project_root = None
        self.rootfs_path = None
        self.build_dir = None
        self.ready_to_setup = False
        self.method = method
        self.distro = distro
        self.release = release
        self.arch = arch
        
    def init_workspace(self):
        self.storage_manager.find_project_root()

        self.build_dir = self.storage_manager.create_build_directory(
            distro=self.distro, release=self.release, method=self.method)
        self.rootfs_path = self.storage_manager.rootfs_path
        self.project_root = self.storage_manager.project_root
        
        
    def install_system(self, method=None, force_reinstall=False):
        self.installer = SystemInstaller(method=method, executer=self.executer, console=self.console, 
                                         project_root=self.project_root, rootfs_path=self.rootfs_path, 
                                         distro=self.distro, release=self.release, arch=self.arch)
        

        self.ready_to_setup = self.installer.install(force_reinstall=force_reinstall)
        
    def init_system(self, interactive):
        self.chroot_manager = ChrootManager(executer=self.executer, console=self.console, chroot_destination=self.rootfs_path)
        self.system_setup = SystemSetup(executer=self.executer, console=self.console, 
                                        rootfs_path=self.rootfs_path, project_root=self.project_root, 
                                        chroot_manager=self.chroot_manager, distro=self.distro, release=self.release, 
                                        arch=self.arch)
        
        if self.ready_to_setup:
            self.system_setup.init_system(interactive=interactive)

    def install_packages(self):
        self.system_setup.install_packages()

    def prepare_usb(self):
        storage_manager = StorageManager()
        storage_manager._list_disks()
        usb_manager = USBManager(console=self.console, executer=self.executer)
        usb_manager.prepare_usb()
        #usb_manager.umount_partitions()
