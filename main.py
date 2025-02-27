import sys
sys.path.insert(0, 'src')

from modules.prepare_usb import list_disks, prepare_usb, unmount_partitions

def main():
    print('USB Live Creator')
    list_disks()
    disk = input('Введите устройсво (например, /dev/sdb):').strip()
    unmount_partitions(disk)
    prepare_usb(disk)



if __name__ == "__main__":
    main()