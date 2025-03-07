import os
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.chroot_manager.chroot_manager import ChrootManager

class SystemSetup:
    def __init__(self, executer=None, console=None, rootfs_path=None, project_root=None, chroot_manager=None):
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)
        self.console = console or Console()

        if not project_root:
            raise RuntimeError('Не могу получить путь корневой директории проекта.')
        if not rootfs_path:
            raise RuntimeError('Не могу получить путь к rootfs устанавливаемой системы')
        
        self.project_root = project_root
        self.rootfs_path = rootfs_path
        
        self.chroot_manager = chroot_manager or ChrootManager(chroot_destination=self.rootfs_path,
                                                               executer=self.executer, console=self.console)

    def system_init(self, interactive:False):
        source_list = os.path.join(self.rootfs_path, 'etc/apt/sources.list.d/ubuntu.sources')
        mirrors = '''
Types: deb
URIs: http://archive.ubuntu.com/ubuntu/
Suites: noble noble-updates noble-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb
URIs: http://security.ubuntu.com/ubuntu/
Suites: noble-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
'''
        with open(source_list, 'w') as f:
            f.write(mirrors)

        with self.chroot_manager as chroot:
            if interactive:
                chroot.run_command('/bin/bash')
            else:
                chroot.run_command('apt update -y')
                chroot.run_command('apt upgrade -y')
                chroot.run_command('apt install neofetch -y')
                chroot.run_command('neofetch')