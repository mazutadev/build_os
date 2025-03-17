import os
import shutil
from rich.console import Console
from modules.command_executor import CommandExecutor
from modules.chroot_manager.chroot_manager import ChrootManager
from modules.build_manager.grub_installer import GrubInstaller

class SystemSetup:
    def __init__(self, executer=None, console=None, rootfs_path=None, project_root=None, 
                 chroot_manager=None, distro=None, release=None, arch=None, hostname=None,
                 timezone=None):
        
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
        self.hostname = hostname
        self.timezone = timezone
        
        self.chroot_manager = chroot_manager or ChrootManager(chroot_destination=self.rootfs_path,
                                                               executer=self.executer, console=self.console)
        self.grub_installer: GrubInstaller = None
        
    def init_system(self, interactive:False):
        if self.distro == 'ubuntu':
            self.package_manager = 'apt'

            self._set_mirrors()
            self._set_hostname()

            with self.chroot_manager as chroot:
                self._set_locale(chroot=chroot)
                self._set_timezone(chroot=chroot)
                self._set_fonts(chroot=chroot)
                self._update_package_manager(chroot=chroot, package_manager=self.package_manager)
                self._install_kernel(chroot=chroot)
                self._update_package_manager(chroot=chroot, package_manager=self.package_manager)
                self._update_initramfs(chroot=chroot)

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
        self.console.print(f'[green]🔄 Ядро установлено в {self.rootfs_path}...[/green]')

    def _update_initramfs(self, chroot: ChrootManager):
        chroot.run_command('update-initramfs -u -k all')

    def _update_package_manager(self, chroot: ChrootManager, package_manager):
        chroot.run_command(f'{package_manager} update -y')

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
        packages_list = ['nano', 'curl', 'wget', 'vim', 
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
                        'grub2-common', 'isc-dhcp-client']
        
        packages_list_min = ['nano', 'curl', 'wget', 'htop',
                             'neofetch', 'casper', 'live-boot', 
                             'live-tools', 'grub-efi', 'grub-pc-bin', 
                             'grub-efi-amd64-bin', 'grub-efi-amd64', 
                             'grub-common', 'grub2-common', 'isc-dhcp-client']

        with self.chroot_manager as chroot:
            for pkg in packages_list_min:
                chroot.run_command(f'{self.package_manager} install {pkg} -y')

    def _set_hostname(self):
        hostname_path = os.path.join(self.rootfs_path, 'etc/hostname')
        with open(hostname_path, 'w') as f:
            f.write(self.hostname)

        hosts_path = os.path.join(self.rootfs_path, 'etc/hosts')
        with open(hosts_path, 'a') as f:
            f.write(f'\n127.0.1.1 {self.hostname}\n')

    def _set_locale(self, chroot: ChrootManager):
        locale_gen_path = os.path.join(self.rootfs_path, 'etc/locale.gen')
        with open(locale_gen_path, 'w') as f:
            f.write('en_US.UTF-8 UTF-8\n')
            f.write('ru_RU.UTF-8 UTF-8\n')

        locale_conf_path = os.path.join(self.rootfs_path, 'etc/default/locale')
        with open(locale_conf_path, 'w') as f:
            f.write('LANG=en_US.UTF-8\n')
            f.write('LC_ALL=en_US.UTF-8\n')
            f.write('LC_MESSAGES=en_US.UTF-8\n')
            f.write('LC_CTYPE=ru_RU.UTF-8\n')
            f.write('LC_TIME=ru_RU.UTF-8\n') 

        chroot.run_command('locale-gen en_US.UTF-8 ru_RU.UTF-8')
        chroot.run_command('update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8')

    def _set_timezone(self, chroot: ChrootManager):
        localtime_path = os.path.join(self.rootfs_path, 'etc/localtime')
        timezone_path = os.path.join(self.rootfs_path, 'etc/timezone')


        chroot.run_command(f'ln -sf /usr/share/zoneinfo/{self.timezone} /etc/localtime')

        with open(timezone_path, 'w') as f:
            f.write(self.timezone)

    def _set_mirrors(self):
        source_list_dir = os.path.join(self.project_root, 'src/configs/mirrors/ubuntu/noble/ubuntu.sources')
        source_list_dir_dest = os.path.join(self.rootfs_path, 'etc/apt/sources.list.d/ubuntu.sources')

        self.console.print(f'[cyan]Копирование {source_list_dir} в {source_list_dir_dest}[/cyan]')
        shutil.copy2(source_list_dir, source_list_dir_dest)

    def _set_fonts(self, chroot: ChrootManager):
        fonts_host_path = '/usr/share/consolefonts'
        font_rootfs_path = os.path.join(self.rootfs_path, 'usr/share/consolefonts')

        self.console.print(font_rootfs_path)
        self.console.print(f'{self.rootfs_path} - Директория проекта')

        try:
            self.executer.run(f'cp {fonts_host_path}/* {font_rootfs_path}/')
        except Exception as e:
            self.console.print(f'{e}')

        chroot.run_command(f'localectl set-keymap us,ru')
        chroot.run_command(f'localectl set-x11-keymap us,ru pc105 grp:alt_shift_toggle')