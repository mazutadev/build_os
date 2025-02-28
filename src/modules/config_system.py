from rich.console import Console
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

def install_grub():
    console.print('[cyan]Установка GRUB...[/cyan]')
    executer.run('grub-install --target=x86_64-efi --efi-directory=/mnt/usb/boot/efi --boot-directory=/mnt/usb/boot --removable', capture_output=False)
    console.print('[bold green]GRUB установлен![/bold green]')

def create_grub_cfg():
    console.print('[cyan]Создание конфигурации GRUB[/cyan]')

    grub_cfg = """
set timeout=5
set default=0

menyentry "Live Copy OS" {
  search --no-floppy --set=root --label LIVE_USB
  linux /boot/vmlinuz boot=casper root=LABEL=LIVE_USB ro quiet spalsh toram
  initrd /boot/initrd.img
}
"""
    with open('/mnt/usb/boot/grub/grub.cfg', 'w') as f:
        f.write(grub_cfg)
    
    console.print('[bold green]grub.cfg создан![/bold green]')

def config_fstab():
    console.print('[cyan]Настройка fstab...[/cyan]')

    fstab = """
LABEL=LIVE_USB / ext4 defaults,noatime,ro 0 1
tmpfs /tmp tmpfs default,nosuid,nodev 0 0
"""

    with open('/mnt/usb/etc/fstab', 'w') as f:
        f.write(fstab)

    console.print('[bold green]fstab настроен[/bold green]')

def install_casper():
    console.print('[cyan]Установка casper в Live-систему...[/cyan]')

    executer.run('mkdir -p /mnt/usb/dev')
    executer.run('mkdir -p /mnt/usb/proc')
    executer.run('mkdir -p /mnt/usb/sys')
    executer.run('mkdir -p /mnt/usb/run')
    executer.run('mkdir -p /mnt/usb/tmp')
    executer.run('mkdir -p /mnt/usb/mnt')
    executer.run('mkdir -p /mnt/usb/media')
    executer.run('chmod 1777 /mnt/usb/tmp')

    executer.run('mount --bind /dev /mnt/usb/dev')
    executer.run('mount --bind /proc /mnt/usb/proc')
    executer.run('mount --bind /sys /mnt/usb/sys')
    executer.run('mount --bind /run /mnt/usb/run')

    try:
        executer.run('chroot /mnt/usb apt update', capture_output=False)
        executer.run('chroot /mnt/usb apt install -y casper', capture_output=False)
        console.print('[bold green]casper установлен![/bold green]')
    finally:
        executer.run('umount /mnt/usb/dev')
        executer.run('umount /mnt/usb/proc')
        executer.run('umount /mnt/usb/sys')
        executer.run('umount /mnt/usb/run')