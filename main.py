import sys
import os
sys.path.insert(0, 'src')

from modules.storage_manager.storage_manager import StorageManager
from modules.build_manager.build_manager import BuildManager
from modules.utils import Utils

def install_system(distro, release, arch, method='clean_install', force_reinstall=False, interactive=False):
    
    if method == 'clean_install':
        if distro == 'ubuntu':
            build_manager = BuildManager(use_sudo=True, debug=True, distro=distro,
                                        release=release, arch=arch, method=method)

            build_manager.install_system(method='debootstrap', force_reinstall=force_reinstall)
            
            build_manager.init_system(interactive=interactive)
            #build_manager.system_setup.install_packages()
            #build_manager.system_setup.create_user(username='admin', password='123', sudo=True)

            #build_manager.prepare_usb()
            build_manager.prepare_pxe()


def test_func():
    build_manager = BuildManager(distro='test', release='my_release', method='test', arch='amd64')


if __name__ == "__main__":
    install_system('ubuntu', 'noble', 'amd64', 
                   method='clean_install', force_reinstall=False, interactive=False)