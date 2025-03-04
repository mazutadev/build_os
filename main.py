import sys
sys.path.insert(0, 'src')

from modules.prepare_manager.prepare_usb import list_disks, prepare_usb, unmount_partitions
from modules.prepare_manager.prepare_pxe import prepare_pxe
from modules.system_builder.copy_system import mount_usb, copy_system
from modules.system_builder.config_system import install_grub, config_fstab, copy_grub_cfg

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
   main()