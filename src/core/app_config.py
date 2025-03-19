from dataclasses import dataclass, asdict, field
import json
import yaml
import os
from typing import Dict, List

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

@dataclass
class PackageConfig:
    packages: Dict[str, List[str]] = field(default_factory=dict)

    def add_package(self, category: str, package: str):
        if category not in self.packages:
            self.packages[category] = []
        self.packages[category].append(package)

    def remove_package(self, category: str, package: str):
        if category in self.packages and package in self.packages[category]:
            self.packages[category].remove(package)

    def get_packages(self, category: str):
        return self.packages.get(category, [])
    
    def get_all_categories(self):
        return list(self.packages.keys())


class AppConfig:
    storage: StorageConfig = StorageConfig()
    project_meta: MetaConfig = MetaConfig()
    package_config: PackageConfig = PackageConfig()
    _config_file = 'config.json'
    _packages_file = 'pakages_list.yaml'

    _storage_dirs = {}
    _project_meta = {}

    @classmethod
    def load_packages(cls):
        __packages_file_path = os.path.join(cls.storage.project_root, 'src', 'configs', 'packages', cls._packages_file)
        print(__packages_file_path)
        if os.path.exists(__packages_file_path):
            with open(__packages_file_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                cls.package_config = PackageConfig(data.get('packages', {}))

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