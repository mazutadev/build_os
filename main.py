import sys
sys.path.insert(0, 'src')

from modules.prepare_manager.prepare_usb import list_disks, prepare_usb, unmount_partitions
from modules.prepare_manager.prepare_pxe import prepare_pxe
from modules.system_builder.copy_system import mount_usb, copy_system
from modules.system_builder.config_system import install_grub, config_fstab, copy_grub_cfg
from modules.storage_manager.storage_manager import StorageManager
from modules.system_builder.system_builder import SystemBuilder

storage_manager = StorageManager()

def main():
    print('USB Live Creator')
    list_disks()
    disk = input('Введите устройсво (например, /dev/sdb):').strip()
    unmount_partitions(disk)

    if prepare_usb(disk):
        mount_usb(disk)
        copy_system('/*', '/mnt/usb')
        install_grub(disk)
        copy_grub_cfg('/mnt/usb')
        config_fstab()

def make_pxe():
    prepare_pxe()

def install():
    disk = input('Введите устройсво (например, /dev/sdb):').strip()
    install_grub(disk)
    copy_grub_cfg('/mnt/usb')
    config_fstab()


if __name__ == "__main__":
    exclude = ['/mnt', '/dev', '/proc', '/sys', 
            '/tmp', '/run', '/media', '/lost+found', 
            '/swap.img', '/var/swap.img', '/boot/efi/EFI', 
            '/boot/grub', '/etc/default/grub', '/etc/grub.d']
   
    project_root = storage_manager.find_project_root()
    storage_manager.create_build_directory('ubuntu', 'noble', 'copy')
    rootfs_path = storage_manager.copy_system(exclude=exclude)

    system_bulder = SystemBuilder('/mnt/usb')
    
    storage_manager.list_disks()
    disk = input('Введите устройсво (например, /dev/sdb):').strip()
    if storage_manager.prepare_usb(disk):
        storage_manager.copy_to_usb(disk, '/mnt/usb')
        system_bulder.install_packages()
        system_bulder.install_grub(disk)
        system_bulder.config_grub('/mnt/usb', project_root)
        system_bulder.config_fstab()