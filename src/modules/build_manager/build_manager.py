from modules.storage_manager.storage_manager import StorageManager
from modules.chroot_manager.chroot_manager import ChrootManager
from modules.build_manager.system_installer import SystemInstaller
from modules.build_manager.system_setup import SystemSetup
from modules.storage_manager.usb_manager import USBManager
from modules.build_manager.grub_installer import GrubInstaller
from core.app_config import AppConfig
from core.di import DIContainer


class BuildManager:
    def __init__(self):
        self.console = DIContainer.resolve('console')
        self.executer = DIContainer.resolve('executer')
        self.method = AppConfig.project_meta.method
        self.distro = AppConfig.project_meta.distro
        self.release = AppConfig.project_meta.release
        self.arch = AppConfig.project_meta.arch
        self.ready_to_setup = False
        self.build_dir = None
        self.usb_manager = None
        self.grub_installer = None
        
        self.storage_manager: StorageManager = StorageManager()
        
    def install_system(self):
        try:
            self.installer = SystemInstaller()
            
            self.ready_to_setup = self.installer.install()

        except Exception as e:
            self.console.print(f'[bold red]При установке системы методом: '
                               f'{AppConfig.project_meta.installer} произошла ошибка: '
                               f'{e}[/bold red]')
            return

    def init_system(self):
        self.chroot_manager = ChrootManager()
        DIContainer.register('chroot_manager', self.chroot_manager)
        self.system_setup = SystemSetup(hostname='PXE-OS', timezone='Europe/Moscow')
        
        if self.ready_to_setup:
            self.system_setup.init_system()

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
