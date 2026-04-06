# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
配置文件管理器
"""

import json
import os

import bpy  # pylint: disable=import-error

from ..util.logger import Log
from .config_schema import ConfigValidationError, validate_config


USER_CONFIG_DIR_NAME = "hbr_mmd_tools"
LEGACY_USER_CONFIG_DIR_NAME = "half_bottled"
CONFIG_TYPES = ("blink", "lip_sync")
CONFIG_SOURCE_PREDEFINED = "predefined"
CONFIG_SOURCE_USER = "user"


class ConfigManager:
    """配置文件管理器类"""

    def __init__(self):
        addon_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_base_path = os.path.join(addon_dir, "configs")
        self.user_config_path = self._ensure_user_config_root()
        Log.info(f"Config base path: {self.config_base_path}")
        Log.info(f"User config path: {self.user_config_path}")
        Log.info(f"Addon directory: {addon_dir}")
        Log.info(f"Config directory exists: {os.path.exists(self.config_base_path)}")
        Log.info(f"User config directory exists: {os.path.exists(self.user_config_path)}")

    def get_user_config_dir(self, config_type=None):
        """返回用户配置目录。"""
        if config_type is None:
            return self.user_config_path
        self._validate_config_type(config_type)
        config_dir = os.path.join(self.user_config_path, config_type)
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def get_config_files(self, config_type):
        """兼容旧调用，返回配置条目列表。"""
        return self.get_config_entries(config_type)

    def get_config_entries(self, config_type):
        """获取指定类型的配置条目列表。"""
        self._validate_config_type(config_type)
        config_entries = []
        for source, config_dir in (
            (CONFIG_SOURCE_PREDEFINED, self._get_predefined_config_dir(config_type)),
            (CONFIG_SOURCE_USER, self.get_user_config_dir(config_type)),
        ):
            if not os.path.exists(config_dir):
                continue
            for file_name in sorted(os.listdir(config_dir)):
                if not file_name.endswith(".json"):
                    continue
                config_path = os.path.join(config_dir, file_name)
                config_data = self._load_config_from_path(config_type, config_path)
                if config_data is None:
                    continue
                config_entries.append(
                    {
                        "id": self._build_config_id(source, file_name),
                        "name": file_name,
                        "path": config_path,
                        "type": source,
                        "display_name": self._build_display_name(file_name, source),
                        "description": self._build_description(config_data, source),
                    }
                )
        return config_entries

    def resolve_config_entry(self, config_type, selection):
        """根据选择值解析配置条目。"""
        if not selection:
            return None

        config_entries = self.get_config_entries(config_type)
        for entry in config_entries:
            if entry["id"] == selection:
                return entry

        if ":" not in selection:
            for source in (CONFIG_SOURCE_USER, CONFIG_SOURCE_PREDEFINED):
                for entry in config_entries:
                    if entry["type"] == source and entry["name"] == selection:
                        return entry

        return None

    def load_config(self, config_type, selection):
        """加载配置文件。"""
        entry = self.resolve_config_entry(config_type, selection)
        if entry is None:
            Log.warning(f"Config entry not found: {config_type}, {selection}")
            return None
        return self._load_config_from_path(config_type, entry["path"])

    def save_config(self, config_type, config_file, config_data):
        """保存配置文件到用户目录。"""
        self._validate_config_type(config_type)
        config_name = self._ensure_json_suffix(config_file)
        config_dir = self.get_user_config_dir(config_type)
        config_path = os.path.join(config_dir, config_name)

        try:
            normalized_config = validate_config(config_type, config_data)
            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(normalized_config, file, indent=2, ensure_ascii=False)
            return True
        except (OSError, TypeError, ConfigValidationError) as exc:
            Log.error(f"Failed to save config {config_path}: {str(exc)}")
            return False

    def import_config(self, config_type, source_path, config_name):
        """导入配置文件到用户配置目录。"""
        self._validate_config_type(config_type)
        if not os.path.exists(source_path):
            Log.error(f"Source file not found: {source_path}")
            return None

        try:
            with open(source_path, "r", encoding="utf-8") as file:
                config_data = json.load(file)
            normalized_config = validate_config(config_type, config_data)
        except (OSError, json.JSONDecodeError, ConfigValidationError) as exc:
            Log.error(f"Invalid config file {source_path}: {str(exc)}")
            return None

        target_dir = self.get_user_config_dir(config_type)
        target_name = self._allocate_user_config_name(
            target_dir,
            self._ensure_json_suffix(config_name),
        )
        target_path = os.path.join(target_dir, target_name)

        try:
            with open(target_path, "w", encoding="utf-8") as file:
                json.dump(normalized_config, file, indent=2, ensure_ascii=False)
            Log.info(f"Successfully imported config to user directory: {target_path}")
        except OSError as exc:
            Log.error(f"Failed to import config: {str(exc)}")
            return None

        return self.resolve_config_entry(
            config_type,
            self._build_config_id(CONFIG_SOURCE_USER, target_name),
        )

    def _ensure_user_config_root(self):
        user_scripts_dir = bpy.utils.user_resource("SCRIPTS")
        configs_dir = os.path.join(user_scripts_dir, "configs")
        user_config_dir = os.path.join(configs_dir, USER_CONFIG_DIR_NAME)
        legacy_config_dir = os.path.join(configs_dir, LEGACY_USER_CONFIG_DIR_NAME)

        os.makedirs(user_config_dir, exist_ok=True)
        for config_type in CONFIG_TYPES:
            os.makedirs(os.path.join(user_config_dir, config_type), exist_ok=True)

        self._migrate_legacy_user_configs(legacy_config_dir, user_config_dir)
        return user_config_dir

    def _migrate_legacy_user_configs(self, legacy_root, target_root):
        if not os.path.exists(legacy_root):
            return

        for config_type in CONFIG_TYPES:
            legacy_dir = os.path.join(legacy_root, config_type)
            target_dir = os.path.join(target_root, config_type)
            if not os.path.exists(legacy_dir):
                continue
            for file_name in sorted(os.listdir(legacy_dir)):
                if not file_name.endswith(".json"):
                    continue
                legacy_path = os.path.join(legacy_dir, file_name)
                target_path = os.path.join(target_dir, file_name)
                if os.path.exists(target_path):
                    continue
                config_data = self._load_config_from_path(config_type, legacy_path)
                if config_data is None:
                    continue
                with open(target_path, "w", encoding="utf-8") as file:
                    json.dump(config_data, file, indent=2, ensure_ascii=False)
                Log.info(f"Migrated legacy config: {legacy_path} -> {target_path}")

    def _get_predefined_config_dir(self, config_type):
        self._validate_config_type(config_type)
        return os.path.join(self.config_base_path, config_type)

    @staticmethod
    def _build_config_id(source, file_name):
        return f"{source}:{file_name}"

    @staticmethod
    def _build_display_name(file_name, source):
        source_label = "Built-in" if source == CONFIG_SOURCE_PREDEFINED else "User"
        return f"{file_name} [{source_label}]"

    @staticmethod
    def _build_description(config_data, source):
        source_label = "Built-in" if source == CONFIG_SOURCE_PREDEFINED else "User"
        return f"{config_data['name']} ({source_label})"

    @staticmethod
    def _ensure_json_suffix(file_name):
        if file_name.endswith(".json"):
            return file_name
        return f"{file_name}.json"

    @staticmethod
    def _allocate_user_config_name(target_dir, desired_name):
        base_name, extension = os.path.splitext(desired_name)
        candidate = desired_name
        index = 1
        while os.path.exists(os.path.join(target_dir, candidate)):
            candidate = f"{base_name}_{index}{extension}"
            index += 1
        return candidate

    @staticmethod
    def _validate_config_type(config_type):
        if config_type not in CONFIG_TYPES:
            raise ValueError(f"Unsupported config type: {config_type}")

    @staticmethod
    def _load_config_from_path(config_type, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                config = json.load(file)
            return validate_config(config_type, config)
        except (OSError, json.JSONDecodeError, ConfigValidationError) as exc:
            Log.error(f"Failed to load config {config_path}: {str(exc)}")
            return None


_config_manager = ConfigManager()


def get_config_manager():
    """获取配置管理器实例"""
    return _config_manager
