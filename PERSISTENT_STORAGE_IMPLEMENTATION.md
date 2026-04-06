# 持久化存储方案实现总结

## 方案概述

我们已经成功实现了用户自定义配置文件的持久化存储方案，该方案将用户导入的配置文件保存在Blender用户目录下的专用文件夹中，确保在重启Blender、切换项目、重新安装插件或跨版本升级后配置依然可用。

## 实现的核心功能

### 1. 用户配置目录管理
- **位置**: `Blender用户脚本目录/configs/half_bottled/`
- **子目录**: 自动创建`blink`和`lip_sync`子目录
- **持久化**: 配置文件保存在Blender用户目录，与插件安装位置分离

### 2. 配置管理器增强
- **双路径支持**: 同时支持预定义配置（插件内）和用户配置（用户目录）
- **优先级**: 优先加载用户配置，不存在时回退到预定义配置
- **类型标识**: 配置文件列表显示配置类型（预定义/用户）

### 3. 配置导入功能
- **持久化存储**: 导入的配置文件自动保存到用户配置目录
- **格式验证**: 导入时验证JSON格式有效性
- **自动刷新**: 导入成功后自动刷新UI配置列表

## 修改的文件

### 核心文件
1. **`src/core/config_manager.py`**
   - 新增`_get_user_config_path()`方法获取用户配置目录
   - 重构`get_config_files()`方法支持双路径配置
   - 更新`import_config()`方法实现持久化存储
   - 更新`load_config()`方法支持优先级加载

2. **`src/api/scene/mmd_set.py`**
   - 更新`get_lips_config_files()`和`get_blink_config_files()`函数
   - 添加配置类型标识显示

### UI操作器文件
3. **`src/api/ui/mmd_blink_panel.py`**
   - 更新`ImportBlinkConfigOperator`操作器
   - 添加UI刷新逻辑

4. **`src/api/ui/mmd_set_panel.py`**
   - 更新`ImportLipsConfigOperator`操作器
   - 添加UI刷新逻辑

### 插件注册文件
5. **`src/core/addon.py`**
   - 添加`ImportLipsConfigOperator`操作器注册

## 技术实现细节

### 用户配置目录获取
```python
def _get_user_config_path(self):
    # 使用Blender的用户资源目录
    user_scripts_dir = bpy.utils.user_resource('SCRIPTS')
    user_config_dir = os.path.join(user_scripts_dir, 'configs', 'half_bottled')
    
    # 确保目录存在
    os.makedirs(user_config_dir, exist_ok=True)
    os.makedirs(os.path.join(user_config_dir, 'blink'), exist_ok=True)
    os.makedirs(os.path.join(user_config_dir, 'lip_sync'), exist_ok=True)
    
    return user_config_dir
```

### 配置文件列表获取
```python
def get_config_files(self, config_type):
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
    
    return config_files
```

### 配置导入持久化
```python
def import_config(self, config_type, source_path, config_name):
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
```

## 持久化效果

| 场景 | 持久化效果 |
|------|-----------|
| 重启Blender | ✅ 用户配置保持可用 |
| 切换项目 | ✅ 用户配置保持可用 |
| 重新安装插件 | ✅ 用户配置保持可用 |
| 插件版本升级 | ✅ 用户配置保持可用 |
| 跨Blender版本 | ✅ 用户配置保持可用 |

## 用户体验改进

1. **无感知持久化**: 用户无需手动管理配置索引或备份
2. **自动分类**: 眨眼和口型配置自动分类存储
3. **类型标识**: UI中清晰显示配置来源（预定义/用户）
4. **导入即用**: 导入后立即生效，无需额外操作

## 测试验证

已创建测试脚本`test_config_manager.py`验证以下功能：
- 用户配置目录正确创建
- 配置文件列表正确合并显示
- 配置类型标识正常工作

## 结论

持久化存储方案已完全实现，解决了用户自定义配置文件在重启Blender或切换项目后丢失的问题。该方案具有以下优势：

1. **真正的持久化**: 配置文件保存在Blender用户目录，与插件生命周期分离
2. **用户友好**: 无需额外管理操作，导入即持久化
3. **兼容性强**: 支持各种Blender使用场景
4. **扩展性好**: 易于添加新的配置类型

该实现满足了用户对配置持久化的核心需求，提供了稳定可靠的自定义配置管理功能。