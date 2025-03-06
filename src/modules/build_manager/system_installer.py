from modules.build_manager.debootstrap_installer import DebootStrapInstaller
from rich.console import Console
from modules.command_executor import CommandExecutor

class SystemInstaller:
    def __init__(self, method="debootstrap", executer=None, console=None):
        self.method = method
        self.installer = None
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)
        self.console = console or Console()

        if method == "debootstrap":
            self.installer = DebootStrapInstaller(console=self.console, executer=self.executer)
        else:
            raise ValueError(f'Метод установки "{method}" не поддерживается')
        
    def install(self, rootfs_path, distro, release, arch, force_reinstall=False):
        if self.installer:
            return self.installer.install(rootfs_path=rootfs_path, distro=distro, 
                                   release=release, arch=arch, force_reinstall=force_reinstall)
        else:
            raise RuntimeError('Не выбран метод установки!')