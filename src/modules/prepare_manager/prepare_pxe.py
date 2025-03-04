from rich.console import Console
import os
from modules.command_executor import CommandExecutor
from modules.utils import get_project_root, get_distro_name, get_current_date
from modules.system_builder.copy_system import copy_system
from modules.chroot_manager.chroot_manager import ChrootManager


console = Console()
executer = CommandExecutor(use_sudo=True, debug=False)

def _create_build_dir() -> str:
    distro: list = get_distro_name()
    date: str = get_current_date()
    root_path: str = get_project_root()

    if len(distro) > 1:
        path = f'{root_path}/build/{distro[0]}_{distro[1]}_{date}/root_fs'
    else:
        path = f'{root_path}/build/{distro[0]}_{date}/raw_root_fs'
        
    executer.run(f'mkdir -p {path}')
    executer.run(f'mkdir -p {path}/../root_squashfs')
    executer.run(f'mkdir -p {path}/../boot')

    return path

def _create_squashfs(destination_copy: str):
    if not os.path.exists(destination_copy):
        console.print(f'[bold red]Ошибка, директории: {destination_copy} не существует![/bold red]')
        return False
    console.print(f'[cyan]Создаю Squashfs из директории: {destination_copy}')

    exlude_dirs = ['proc', 'sys', 'dev', 'run', 'mnt', 'media', 'tmp', 'var/tmp']
    exlude_flags = " ".join([f'-e {d}' for d in exlude_dirs])

    executer.run(f'mksquashfs {destination_copy} {destination_copy}/../root_squashfs/rootfs.squashfs -comp xz -Xbcj x86 -processors $(nproc) -all-root {exlude_flags}', capture_output=False)

def _get_boot(destination_copy: str):
    if not os.path.exists(destination_copy):
        console.print(f'[bold red]Ошибка, директории: {destination_copy} не существует![/bold red]')
        return False
    console.print(f'[cyan]Копирую vmlinuz и initrd из директории: {destination_copy}/boot/')

    executer.run(f'cp {destination_copy}/boot/vmlinuz {destination_copy}/../boot/' )
    executer.run(f'cp {destination_copy}/boot/initrd.img {destination_copy}/../boot/' )

def prepare_pxe():
    destination_path = _create_build_dir()

    copy_system(rootfs='/*', destination_copy=destination_path)
    

    try:
        with ChrootManager(destination_path) as chroot:
            #chroot.run_command('/bin/bash')
            chroot.run_command('apt update -y')
            chroot.run_command('apt install -y casper live-boot')
            chroot.run_command('apt install -y neofetch')
            chroot.run_command('neofetch')
    except Exception as e:
        print(e)

    _get_boot(destination_copy=destination_path)
    _create_squashfs(destination_copy=destination_path)