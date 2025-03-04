import sys
sys.path.insert(0, 'src')

from modules.prepare_usb import list_disks, prepare_usb, unmount_partitions
from modules.prepare_pxe import create_build_dir
from modules.copy_system import mount_usb, copy_system
from modules.config_system import install_grub, config_fstab, install_casper, copy_grub_cfg
from modules.utils import get_project_root, get_current_date, get_distro_name

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
    destination_path = create_build_dir()
    copy_system(rootfs='/*', destination_copy=destination_path)

def install():
    disk = input('Введите устройсво (например, /dev/sdb):').strip()
    install_grub(disk)
    copy_grub_cfg('/mnt/usb')
    config_fstab()


if __name__ == "__main__":
   make_pxe()