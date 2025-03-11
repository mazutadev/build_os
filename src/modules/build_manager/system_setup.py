import os
import shutil
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.chroot_manager.chroot_manager import ChrootManager

class SystemSetup:
    def __init__(self, executer=None, console=None, rootfs_path=None, project_root=None, 
                 chroot_manager=None, distro=None, release=None, arch=None):
        
        self.executer = executer or CommandExecutor(use_sudo=True, debug=True)
        self.console = console or Console()
        if not project_root:
            raise RuntimeError('Не могу получить путь корневой директории проекта.')
        if not rootfs_path:
            raise RuntimeError('Не могу получить путь к rootfs устанавливаемой системы')
        
        self.project_root = project_root
        self.rootfs_path = rootfs_path
        self.distro = distro
        self.release = release
        self.arch = arch
        self.package_manager = None
        
        self.chroot_manager = chroot_manager or ChrootManager(chroot_destination=self.rootfs_path,
                                                               executer=self.executer, console=self.console)

    def init_system(self, interactive:False):
        if self.distro == 'ubuntu':
            self.package_manager = 'apt'

            if self.release == 'noble':
                source_list_dir = os.path.join(self.project_root, 'src/configs/mirrors/ubuntu/noble/ubuntu.sources')
                source_list_dir_dest = os.path.join(self.rootfs_path, 'etc/apt/sources.list.d/ubuntu.sources')

                self.console.print(f'[cyan]Копирование {source_list_dir} в {source_list_dir_dest}[/cyan]')
                shutil.copy2(source_list_dir, source_list_dir_dest)

        with self.chroot_manager as chroot:
            if interactive:
                chroot.run_command('/bin/bash')
            else:
                chroot.run_command(f'{self.package_manager} update -y')
                chroot.run_command(f'{self.package_manager} upgrade -y')
                chroot.run_command('locale-gen en_US.UTF-8')
                chroot.run_command('update-locale LANG=en_US.UTF-8')
                chroot.run_command(f'echo "export LC_ALL=en_US.UTF-8" >> {chroot.destination}/etc/environment')
                chroot.run_command(f'echo "export LANGUAGE=en_US.UTF-8" >> {chroot.destination}/etc/environment')

                self._install_kernel(chroot)

    def _user_exists(self, username, chroot):
        user_exists = chroot.run_command(f'id -u {username}')
        return user_exists.returncode == 0

    def create_user(self, username, password, sudo=False):
        with self.chroot_manager as chroot:
            if self._user_exists(username=username, chroot=chroot):
                self.console.print(f'[bold yellow]f"✅ Пользователь {username} уже существует. Пропускаем создание.[/bold yellow]')
                return
            
            self.console.print(f'[cyan]👤 Создаю пользователя[/cyan] [cyan]{username}[/cyan]')
            chroot.run_command(f'useradd -m -s /bin/bash {username}')
            chroot.run_command(f'bash -c "echo \'{username}:{password}\' | chpasswd"')

            self.console.print(f'[cyan]📂 Настраиваем домашнюю директорию...[/cyan]')
            home_dir = os.path.join('home', username)
            chroot.run_command(f'chown -R {username}:{username} {home_dir}')

            if sudo:
                chroot.run_command(f'usermod -aG sudo {username}')
                self.console.print(f'[green]👤 Пользователь {username} добавлен в sudo-группу[/green]')
            self.console.print(f'[green]👤 Пользователь {username} успешно создан![/green]')

            sudoers_line = f"{username} ALL=(ALL) NOPASSWD:ALL"
            chroot.run_command(f"bash -c 'echo \"{sudoers_line}\" > /etc/sudoers.d/{username}'")
            chroot.run_command(f"chmod 0440 /etc/sudoers.d/{username}")

            #self.console.print('💾 Устанавливаем Zsh и Oh My Zsh...')
            #self._install_zsh(username, chroot)

    def _install_kernel(self, chroot: ChrootManager):
        self.console.print(f'[green]🔄 Устанавливаем Ядро в {self.rootfs_path}...[/green]')
        chroot.run_command("apt install -y linux-generic")
        chroot.run_command("update-initramfs -u -k all")
        self.console.print(f'[green]🔄 Ядро установлено в {self.rootfs_path}...[/green]')
        
    def _install_zsh(self, username, chroot: ChrootManager):
        chroot.run_command(f'{self.package_manager} install zsh -y')

        user_home = f'/home/{username}'
        ohmyzsh_path = f'{user_home}/.oh-my-zsh'

        self.console.print(f'[green]🔄 Устанавливаем Oh My Zsh в {ohmyzsh_path}...[/green]')
        chroot.run_command(f"runuser -l {username} -c 'sudo curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh'")

        self.console.print(f'[green]🔌 Устанавливаем плагины...[/green]')
        chroot.run_command(f"runuser -l {username} -c 'sudo git clone https://github.com/zsh-users/zsh-autosuggestions {ohmyzsh_path}/custom/plugins/zsh-autosuggestions'")
        chroot.run_command(f"runuser -l {username} -c 'sudo git clone https://github.com/zsh-users/zsh-syntax-highlighting.git {ohmyzsh_path}/custom/plugins/zsh-syntax-highlighting'")

        self.console.print(f'[green]⚙️ Настраиваем Zshrc...[/green]')
        zshrc_path = f"{user_home}/.zshrc"
        chroot.run_command(f"runuser -l {username} -c \"sudo sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' {zshrc_path}\"")
        self.console.print(f'[green]✅ Пользователь {username} успешно настроен с Oh My Zsh![/green]')

    def install_packages(self):
        pakages_list = ['nano', 'curl', 'wget', 'vim', 
                        'rsync', 'unzip', 'git', 'gnupg2', 
                        'htop', 'btop', 'screen', 'tmux', 
                        'psmisc', 'pciutils', 'usbutils', 'lsof', 
                        'strace', 'bash-completion', 'locales', 
                        'tzdata', 'man-db', 'less', 'net-tools', 
                        'iproute2', 'iputils-ping', 'dnsutils', 
                        'traceroute', 'mtr', 'nmap', 'tcpdump', 
                        'ethtool', 'socat', 'ncdu', 'nload', 
                        'iftop', 'iperf3', 'whois', 'lm-sensors', 
                        'smartmontools', 'iotop', 'sysstat', 
                        'stress', 'atop', 'glances', 
                        'parted', 'fdisk', 'gdisk', 'btrfs-progs', 
                        'xfsprogs', 'e2fsprogs', 'f2fs-tools', 'exfatprogs', 
                        'ntfs-3g', 'dosfstools', 'lvm2', 'mdadm', 
                        'cryptsetup', 'nvme-cli', 'memtester', 'fio',
                        'stress-ng', 'ipmitool',
                        'dmidecode', 'inxi', 'lshw', 'hwinfo', 'lsscsi', 
                        'sg3-utils', 'cpuid', 'msr-tools', 'python3', 
                        'python3-pip', 'python3-venv', 'jq', 'ansible', 
                        'wireshark', 'tshark', 'neofetch', 'casper', 
                        'live-boot', 'live-tools', 'grub-efi', 'grub-pc-bin', 
                        'grub-efi-amd64-bin', 'grub-efi-amd64', 'grub-common', 
                        'grub2-common']
        with self.chroot_manager as chroot:
            for pkg in pakages_list:
                chroot.run_command(f'{self.package_manager} install {pkg} -y')