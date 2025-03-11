import sys
import os
sys.path.insert(0, 'src')

from modules.storage_manager.storage_manager import StorageManager
from modules.build_manager.build_manager import BuildManager

storage_manager = StorageManager()

def make_usb(mount_point: str = '/mnt/usb'):
    exclude = ['/mnt', '/dev', '/proc', '/sys', 
            '/tmp', '/run', '/media', '/lost+found', 
            '/swap.img', '/var/swap.img', '/boot/efi/EFI', 
            '/boot/grub', '/etc/default/grub', '/etc/grub.d']
    
    storage_manager.find_project_root()
    storage_manager.create_build_directory('ubuntu', 'noble', 'copy')
    storage_manager.copy_system(exclude=exclude)

    storage_manager.deploy_system_to_usb(mount_point, deploy=False)

def install_system(distro, release, arch, method='clean_install', force_reinstall=False, interactive=False):
    
    if method == 'clean_install':
        if distro == 'ubuntu':
            build_manager = BuildManager(use_sudo=True, debug=True, distro=distro,
                                        release=release, arch=arch, method=method)
            build_manager.init_workspace()
            build_manager.install_system(method='debootstrap', force_reinstall=force_reinstall)
            
            build_manager.init_system(interactive=interactive)
            build_manager.system_setup.install_packages()
            build_manager.system_setup.create_user(username='admin', password='123', sudo=True)
            build_manager.storage_manager.file_manager.make_squashfs_root()

            build_manager.prepare_usb()
            

def test_func():
    build_manager = BuildManager(use_sudo=True, debug=True, distro='ubuntu',
                                        release='release', arch='arch', method='method')
    build_manager.prepare_usb()


if __name__ == "__main__":
    install_system('ubuntu', 'noble', 'amd64', 
                   method='clean_install', force_reinstall=False, interactive=False)
