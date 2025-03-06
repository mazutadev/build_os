import os
import datetime
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.storage_manager.storage_manager import StorageManager
from modules.chroot_manager.chroot_manager import ChrootManager
from modules.build_manager.system_installer import SystemInstaller
from modules.build_manager.system_setup import SystemSetup


class BuildManager:
    def __init__(self, use_sudo=True, debug=True):
        self.console = Console()
        self.executer = CommandExecutor(use_sudo, debug)
        self.storage_manager = StorageManager(executer=self.executer)
        self.rootfs_path = None
        self.ready_to_install = False
        
    def init_workspace(self, project_type: str):
        self.storage_manager.find_project_root()
        self.storage_manager.create_build_directory('ubuntu', '24.04', project_type)
        self.rootfs_path = self.storage_manager.rootfs_path
        
        
    def install_system(self, distro, release, arch, method='debootstrap', force_reinstall=False):
        self.installer = SystemInstaller(method=method, executer=self.executer, console=self.console)
        self.ready_to_install = self.installer.install(rootfs_path=self.rootfs_path, distro=distro, 
                               release=release, arch=arch, force_reinstall=force_reinstall)
        
    def init_system(self, interactive):
        self.chroot_manager = ChrootManager(chroot_destination=self.rootfs_path, 
                                            executer=self.executer, console=self.console)
        self.system_setup = SystemSetup(executer=self.executer, console=self.console, 
                                        rootfs_path=self.rootfs_path, chroot_manager=self.chroot_manager)
        
        if self.ready_to_install:
            self.system_setup.system_init(interactive=interactive)
