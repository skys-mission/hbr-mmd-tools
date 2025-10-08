# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and SoyWhisky
"""
配置文件管理器
"""

import os
import json
import bpy
from ..util.logger import Log


class ConfigManager:
    """配置文件管理器类"""
    
    def __init__(self):
        # 在Blender插件环境中，使用插件的根目录路径
        addon_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_base_path = os.path.join(addon_dir, 'configs')
        
        # 用户配置目录（Blender用户目录下的专用文件夹）
        self.user_config_path = self._get_user_config_path()
        
        # 调试日志
        Log.info(f"Config base path: {self.config_base_path}")
        Log.info(f"User config path: {self.user_config_path}")
        Log.info(f"Addon directory: {addon_dir}")
        Log.info(f"Config directory exists: {os.path.exists(self.config_base_path)}")
        Log.info(f"User config directory exists: {os.path.exists(self.user_config_path)}")
    
    def _get_user_config_path(self):
        """获取用户配置目录路径"""
        # 使用Blender的用户资源目录
        user_scripts_dir = bpy.utils.user_resource('SCRIPTS')
        user_config_dir = os.path.join(user_scripts_dir, 'configs', 'half_bottled')
        
        # 确保目录存在
        os.makedirs(user_config_dir, exist_ok=True)
        
        # 创建blink和lip_sync子目录
        os.makedirs(os.path.join(user_config_dir, 'blink'), exist_ok=True)
        os.makedirs(os.path.join(user_config_dir, 'lip_sync'), exist_ok=True)
        
        return user_config_dir
    
    def get_config_files(self, config_type):
        """获取指定类型的配置文件列表（包含预定义配置和用户配置）"""
        config_files = []
        
        # 获取预定义配置
        predefined_config_dir = os.path.join(self.config_base_path, config_type)
        if os.path.exists(predefined_config_dir):
            for file in os.listdir(predefined_config_dir):
                if file.endswith('.json'):
                    config_files.append({
                        'name': file,
                        'path': os.path.join(predefined_config_dir, file),
                        'type': 'predefined'
                    })
        
        # 获取用户配置
        user_config_dir = os.path.join(self.user_config_path, config_type)
        if os.path.exists(user_config_dir):
            for file in os.listdir(user_config_dir):
                if file.endswith('.json'):
                    config_files.append({
                        'name': file,
                        'path': os.path.join(user_config_dir, file),
                        'type': 'user'
                    })
        
        # 按文件名排序
        config_files.sort(key=lambda x: x['name'])
        
        return config_files
    
    def load_config(self, config_type, config_file):
        """加载配置文件（支持预定义配置和用户配置）"""
        # 首先尝试从用户配置目录加载
        user_config_path = os.path.join(self.user_config_path, config_type, config_file)
        if os.path.exists(user_config_path):
            config_path = user_config_path
        else:
            # 如果用户配置不存在，尝试从预定义配置目录加载
            config_path = os.path.join(self.config_base_path, config_type, config_file)
        
        if not os.path.exists(config_path):
            Log.warning(f"Config file not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            Log.error(f"Failed to load config {config_path}: {str(e)}")
            return None
    
    def save_config(self, config_type, config_file, config_data):
        """保存配置文件"""
        config_dir = os.path.join(self.config_base_path, config_type)
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, config_file)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            Log.error(f"Failed to save config {config_path}: {str(e)}")
            return False
    
    def import_config(self, config_type, source_path, config_name):
        """导入配置文件到用户配置目录"""
        if not os.path.exists(source_path):
            Log.error(f"Source file not found: {source_path}")
            return False
        
        # 验证JSON格式
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except Exception as e:
            Log.error(f"Invalid JSON format: {str(e)}")
            return False
        
        # 确保配置名称以.json结尾
        if not config_name.endswith('.json'):
            config_name = f"{config_name}.json"
        
        # 复制文件到用户配置目录（持久化存储）
        target_dir = os.path.join(self.user_config_path, config_type)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, config_name)
        
        try:
            import shutil
            shutil.copy2(source_path, target_path)
            Log.info(f"Successfully imported config to user directory: {target_path}")
            return True
        except Exception as e:
            Log.error(f"Failed to import config: {str(e)}")
            return False


# 全局配置管理器实例
_config_manager = ConfigManager()


def get_config_manager():
    """获取配置管理器实例"""
    return _config_manager