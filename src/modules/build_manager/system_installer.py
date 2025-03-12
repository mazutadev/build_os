from modules.build_manager.debootstrap_installer import DebootStrapInstaller
from rich.console import Console
from modules.command_executor import CommandExecutor

class SystemInstaller:
    def __init__(self, distro, release, arch, method="debootstrap", executer=None, console=None, 
                 project_root=None, rootfs_path=None):
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)
        self.console = console or Console()
        if not project_root:
            raise RuntimeError('Не могу получить путь корневой директории проекта.')
        if not rootfs_path:
            raise RuntimeError('Не могу получить путь к rootfs устанавливаемой системы')
        
        self.project_root = project_root
        self.rootfs_path = rootfs_path
        self.distro = distro
        self.release = release
        self.arch = arch
        self.method = method
        self.installer = None
        
        if self.method == "debootstrap":
            self.installer = DebootStrapInstaller(console=self.console, executer=self.executer, 
                                                  project_root=self.project_root, rootfs_path=self.rootfs_path, 
                                                  distro=self.distro, release=self.release, arch=self.arch)
        else:
            raise ValueError(f'Метод установки "{self.method}" не поддерживается')
        
    def install(self, force_reinstall=False):
        if self.installer:
            return self.installer.install(force_reinstall=force_reinstall)
        else:
            raise RuntimeError('Не выбран метод установки!')