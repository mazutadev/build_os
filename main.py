import sys
sys.path.insert(0, 'src')

from modules.storage_manager.storage_manager import StorageManager

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

if __name__ == "__main__":
    make_usb()
