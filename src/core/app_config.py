from dataclasses import dataclass, asdict
import json

@dataclass
class StorageConfig:
    project_root: str = ''
    build_dir: str = ''
    rootfs_path: str = ''
    squashfs_path: str = ''
    live_os_path: str = ''
    boot_dir: str = ''
    boot_dir_efi: str = ''
    live_os_path: str = ''
    bios_boot_live: str = ''
    uefi_boot_live = str = ''

@dataclass
class MetaConfig:
    distro: str = ''
    release: str = ''
    arch: str = ''
    method: str = ''
    force_reinstall: bool = False
    interactive: bool = False
    installer: str = ''
    package_manager: str = ''
    build_date: str = ''
    build_name: str = ''


class AppConfig:
    storage: StorageConfig = StorageConfig()
    project_meta: MetaConfig = MetaConfig()
    _config_file = 'config.json'

    _storage_dirs = {}
    _project_meta = {}

    @classmethod
    def set_storage_dir(cls, name, dir):
        cls._storage_dirs[name] = dir

    @classmethod
    def get_storage_dir(cls, name):
        dir = cls._storage_dirs.get(name)
        return dir
    
    @classmethod
    def set_project_meta(cls, name, value):
        cls._project_meta[name] = value

    @classmethod
    def get_project_meta(cls, name):
        meta = cls._project_meta.get(name)
        return meta
    
    @classmethod
    def save(cls):
        """Сохраняет конфиг в JSON"""
        with open(cls._config_file, "w") as f:
            json.dump({
                "storage": cls.storage.__dict__,
                "project_meta": cls.project_meta.__dict__,
            }, f, indent=4)