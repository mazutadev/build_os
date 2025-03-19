from modules.build_manager.debootstrap_installer import DebootStrapInstaller
from core.di import DIContainer
from core.app_config import AppConfig

class SystemInstaller:
    def __init__(self):
        self.executer = DIContainer.resolve('executer')
        self.console = DIContainer.resolve('console')
        
        self.project_root = AppConfig.storage.project_root
        self.rootfs_path = AppConfig.storage.rootfs_path
        self.distro = AppConfig.project_meta.distro
        self.release = AppConfig.project_meta.release
        self.arch = AppConfig.project_meta.arch
        self.installer = AppConfig.project_meta.installer
        
        if self.installer == "debootstrap":
            self.installer = DebootStrapInstaller()
        else:
            raise ValueError(f'Метод установки "{self.installer}" не поддерживается')
        
    def install(self):
        if self.installer:
            return self.installer.install()
        else:
            raise RuntimeError('Не выбран метод установки!')