import sys
import os
sys.path.insert(0, 'src')

from modules.build_manager.build_manager import BuildManager
from init_dependencies import init_app
from core.app_config import AppConfig

app = init_app()

def install_system(distro, release, arch, method='clean_install', force_reinstall=False, interactive=False):
    AppConfig.project_meta.distro = distro
    AppConfig.project_meta.release = release
    AppConfig.project_meta.arch = arch
    AppConfig.project_meta.method = method
    AppConfig.project_meta.force_reinstall = force_reinstall
    AppConfig.project_meta.interactive = interactive
    
    if method == 'clean_install':
        if distro == 'ubuntu':
            AppConfig.project_meta.installer = 'debootstrap'
            AppConfig.project_meta.package_manager = 'apt'

            build_manager = BuildManager()
            build_manager.install_system()
            
            build_manager.init_system()
            build_manager.system_setup.install_packages()
            build_manager.system_setup.create_user(username='admin', password='123', sudo=True)

            #build_manager.prepare_usb()
            build_manager.prepare_pxe()

def test():
    print(AppConfig.storage.project_root)
    print(AppConfig.package_config.get_packages('base'))
    print(AppConfig.package_config.get_all_categories())

if __name__ == "__main__":
    install_system('ubuntu', 'noble', 'amd64', 
                   method='clean_install', force_reinstall=False, interactive=False)