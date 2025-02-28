import sys
sys.path.insert(0, 'src')

from modules.prepare_usb import list_disks, prepare_usb, unmount_partitions
from modules.copy_system import mount_usb, copy_system
from modules.config_system import install_grub, config_fstab, install_casper, create_grub_cfg

def main():
    print('USB Live Creator')
    list_disks()
    disk = input('Введите устройсво (например, /dev/sdb):').strip()
    unmount_partitions(disk)

    if prepare_usb(disk):
        mount_usb(disk)
        copy_system()

        install_casper()
        install_grub()
        create_grub_cfg()
        config_fstab()

def install():
    install_casper()
    install_grub()
    create_grub_cfg()
    config_fstab()



if __name__ == "__main__":
    install()