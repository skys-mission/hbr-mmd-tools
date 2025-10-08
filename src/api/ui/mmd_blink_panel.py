# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and SoyWhisky
# pylint: disable=R0801
"""
...
"""

import random
import bpy  # pylint: disable=import-error
import os
import sys
from ...util.logger import Log


class RandomBlinkPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """
        ...根据まばたき眨眼
    """
    bl_label = "MMD Random Blink"
    bl_idname = "VIEW3D_PT_Random_blink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Whisky Helper'
    bl_order = 4

    def draw(self, context):
        """
        ...
        """
        layout = self.layout

        # 配置选择区域
        box = layout.box()
        box.label(text="Blink Configuration")
        
        # 配置选择下拉框
        row = box.row()
        row.prop(context.scene, "blink_config_selection", text="Config")
        
        # 自定义配置导入
        row = box.row()
        row.prop(context.scene, "blink_custom_config_path", text="Custom Config")
        row.operator("scene.import_blink_config", text="Apply", icon='CHECKMARK')
        
        # 打开配置文件夹
        row = box.row()
        row.operator("scene.open_blink_config_folder", text="Open Config Folder", icon='FILE_FOLDER')
        
        # 分隔线
        layout.separator()

        # 第一行：标签
        row = layout.row()
        row.label(text="Timeline")

        # 第二行：起始和结束参数
        row = layout.row()
        row.prop(context.scene, "blink_start_frame")
        row.prop(context.scene, "blink_end_frame")
        row = layout.row()
        # row = layout.row()
        row.prop(context.scene, "blinking_frequency")
        row = layout.row()
        row.prop(context.scene, "blinking_wave_ratio")
        # 第三行：随机眨眼按钮
        row = layout.row()
        row.operator("scene.gen_random_blink")
        


class ImportBlinkConfigOperator(bpy.types.Operator):
    """导入眨眼配置操作器"""
    bl_idname = "scene.import_blink_config"
    bl_label = "Import Blink Config"
    bl_description = "Import custom blink configuration"

    def execute(self, context):
        """执行导入配置"""
        scene = context.scene
        
        if not scene.blink_custom_config_path:
            self.report({'ERROR'}, "Please select a custom config file")
            return {'CANCELLED'}
        
        from ...core.config_manager import get_config_manager
        config_manager = get_config_manager()
        
        # 从文件路径中提取配置名称
        import os
        config_name = os.path.splitext(os.path.basename(scene.blink_custom_config_path))[0]
        
        if config_manager.import_config('blink', scene.blink_custom_config_path, config_name):
            self.report({'INFO'}, f"Successfully imported config: {config_name}")
            # 设置当前选中项
            scene.blink_config_selection = f"{config_name}.json"
            # 清空自定义配置路径
            scene.blink_custom_config_path = ""
            # 标记需要刷新UI
            context.area.tag_redraw()
        else:
            self.report({'ERROR'}, "Failed to import config")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class OpenBlinkConfigFolderOperator(bpy.types.Operator):
    """打开眨眼配置文件夹操作器"""
    bl_idname = "scene.open_blink_config_folder"
    bl_label = "Open Blink Config Folder"
    bl_description = "Open the blink configuration folder"

    def execute(self, context):
        """执行打开文件夹"""
        from ...core.config_manager import get_config_manager
        config_manager = get_config_manager()
        
        # 获取用户配置目录
        user_config_path = config_manager._get_user_config_path()
        blink_config_dir = os.path.join(user_config_path, 'blink')
        
        # 确保目录存在
        os.makedirs(blink_config_dir, exist_ok=True)
        
        # 打开文件夹（跨平台兼容）
        try:
            if os.name == 'nt':  # Windows
                os.startfile(blink_config_dir)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                subprocess.run(['open', blink_config_dir] if sys.platform == 'darwin' else ['xdg-open', blink_config_dir])
            
            self.report({'INFO'}, f"Opened blink config folder: {blink_config_dir}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open folder: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class RandomBlinkOperator(bpy.types.Operator):
    """
    ...
    """
    bl_idname = "scene.gen_random_blink"
    bl_label = "Gen random blink"

    def generate_blink_frames(self,  # pylint: disable=too-many-arguments,too-many-positional-arguments
                              start_frame,
                              end_frame,
                              fps,
                              interval_seconds,
                              wave_ratio,
                              config=None):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """
        生成眨眼形态键动画帧序列
        
        :param start_frame: 起始帧
        :param end_frame: 结束帧
        :param fps: 帧率
        :param interval_seconds: 眨眼间隔（秒）
        :param wave_ratio: 间隔波动比例（0.1-1）
        :param config: 配置文件数据
        :return: 包含帧数据的字典 {形态键名: [{frame: 帧数, value: 值}]}
        """
        frames = {}
        current_time = start_frame / fps
        end_time = end_frame / fps
        
        # 获取眨眼形态键名称
        if config:
            blink_shape_key = config.get('shape_keys', {}).get('blink', 'まばたき')
        else:
            blink_shape_key = 'まばたき'

        while current_time < end_time:
            # 计算实际间隔（加入随机波动）
            actual_interval = interval_seconds * random.uniform(1 - wave_ratio, 1 + wave_ratio)
            blink_time = current_time + actual_interval

            # 转换为帧数
            blink_frame = int(blink_time * fps)

            # 确保在有效范围内
            if blink_frame > end_frame:
                break

            # 强制设置起始帧和结束帧为0
            # 生成眨眼动画（从0到1再回到0）
            frames.setdefault(blink_shape_key, []).extend([
                {'frame': blink_frame - 2, 'value': 0.0},
                {'frame': blink_frame, 'value': 1.0},
                {'frame': blink_frame + 2, 'value': 0.0}
            ])

            current_time = blink_time

        # 强制设置起始帧和结束帧为0
        if blink_shape_key in frames:
            frames[blink_shape_key].insert(0, {'frame': start_frame, 'value': 0.0})
            frames[blink_shape_key].append({'frame': end_frame, 'value': 0.0})

        return frames

    @staticmethod
    def find_shape_keys_recursive(obj, shape_key_name):
        """
        ...
        """
        found = []
        if obj.type == 'MESH' and obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                if key.name == shape_key_name:
                    found.append(obj)
                    break

        for child in obj.children:
            found.extend(RandomBlinkOperator.find_shape_keys_recursive(child, shape_key_name))
        return found

    def apply_blink_animation(self, mesh, blink_data, start_frame):
        """
        ...
        """
        morph_key = 'まばたき'
        # 强制设置起始帧为0
        blink_data[morph_key].insert(0, {
            'frame': start_frame,
            'value': 0.0,
            'frame_type': 'KEYFRAME'})
        # 获取最大帧并清除旧关键帧
        max_frame = max(f['frame'] for f in blink_data[morph_key])
        for i in range(start_frame, max_frame + 1):
            self.clear_shape_key_keyframe(mesh, morph_key, i)

        # 查找有效形态键
        found_key = next((k for k in mesh.data.shape_keys.key_blocks if k.name == morph_key), None)
        morph_key = found_key.name if found_key else 'まばたき'

        # 应用关键帧并记录日志
        for frame_data in blink_data[morph_key]:
            try:
                self.set_shape_key_value(  # pylint: disable=too-many-function-args
                    mesh,
                    morph_key,
                    frame_data['value'],
                    frame_data['frame'],
                )  # pylint: disable=too-many-function-args
                Log.info(
                    f"Successfully set shape key '{morph_key}':"
                    f" frame {frame_data['frame']}, value {frame_data['value']}")
            except Exception as e:
                Log.warning(f"Keyframe setting failed.：{str(e)}")
                raise

    @staticmethod
    def set_shape_key_value(obj, shape_key_name, value, frame):
        """
        ...
        """
        if obj and obj.type == 'MESH':
            shape_keys = obj.data.shape_keys
            if shape_keys and shape_key_name in shape_keys.key_blocks:
                shape_key = shape_keys.key_blocks[shape_key_name]
                # 设置关键帧插值类型
                shape_key.value = value
                shape_key.keyframe_insert(
                    data_path="value",
                    frame=frame
                )

    @staticmethod
    def clear_shape_key_keyframe(obj, shape_key_name, frame):
        """
        ...
        """
        if obj and obj.type == 'MESH':
            shape_keys = obj.data.shape_keys
            if shape_keys and shape_key_name in shape_keys.key_blocks:
                try:
                    shape_keys.key_blocks[shape_key_name].keyframe_delete(
                        data_path="value",
                        frame=frame
                    )
                except RuntimeError:
                    pass

    def execute(self, context):
        """
        ...
        """
        scene = context.scene
        fps = scene.render.fps

        context.window_manager.progress_begin(0, 100)
        context.window.cursor_modal_set('WAIT')

        # 加载配置
        config = self.load_blink_config(context)
        if not config:
            context.window_manager.progress_end()
            context.window.cursor_modal_restore()
            return {'CANCELLED'}

        try:
            # 生成眨眼动画数据
            blink_data = self.generate_blink_frames(
                start_frame=scene.blink_start_frame,
                end_frame=scene.blink_end_frame,
                fps=fps,
                interval_seconds=scene.blinking_frequency,
                wave_ratio=scene.blinking_wave_ratio,
                config=config
            )

            # 应用动画到选中的网格对象
            meshes = find_mmd_meshes_with_config(config)
            for mesh in meshes:
                apply_blink_animation_with_config(mesh, blink_data, config)

            context.window_manager.progress_update(100)
            
            # 获取眨眼形态键名称
            blink_shape_key = config.get('shape_keys', {}).get('blink', 'まばたき')
            self.report({'INFO'},
                        f"Successfully generated {len(blink_data[blink_shape_key])} blink animations")
        except Exception as e:  # pylint: disable=broad-exception-caught
            # 结束进度条
            context.window_manager.progress_end()
            # 恢复鼠标指针
            context.window.cursor_modal_restore()
            Log.raise_error(str(e), e.__class__)

        # 结束进度条
        context.window_manager.progress_end()

        # 恢复鼠标指针
        context.window.cursor_modal_restore()
        return {'FINISHED'}
    
    def load_blink_config(self, context):
        """加载眨眼配置"""
        from ...core.config_manager import get_config_manager
        config_manager = get_config_manager()
        
        # 检查是否选择了自定义配置
        if context.scene.blink_custom_config_path:
            # 导入自定义配置
            config_name = context.scene.blink_config_selection
            if not config_name:
                self.report({'ERROR'}, "Please select a configuration")
                return None
            
            config = config_manager.load_config('blink', config_name)
        else:
            # 使用预定义配置
            config_name = context.scene.blink_config_selection
            if not config_name:
                self.report({'ERROR'}, "Please select a configuration")
                return None
            
            config = config_manager.load_config('blink', config_name)
        
        if not config:
            self.report({'ERROR'}, f"Failed to load config: {config_name}")
            return None
        
        return config


def find_shape_keys_with_name(obj, shape_key_name):
    """
    递归查询对象及其子对象中的所有网格体，并查找是否包含指定名称的形态键。

    参数:
        obj (bpy.types.Object): 要查询的对象。
        shape_key_name (str): 要查找的形态键名称。

    返回:
        list: 包含指定名称形态键的对象列表。
    """
    found_objects = []

    # 检查当前对象是否为网格体，并且是否有形态键
    if obj.type == 'MESH' and obj.data.shape_keys:
        for shape_key in obj.data.shape_keys.key_blocks:
            if shape_key.name == shape_key_name:
                found_objects.append(obj)
                break

    # 递归查询子对象
    for child in obj.children:
        found_objects.extend(find_shape_keys_with_name(child, shape_key_name))

    return found_objects


def find_mmd_meshes():
    """
    ...
    """
    # 记录包含指定形态键的对象
    found_objects = []

    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        Log.raise_error("Please select an object first.", Exception)
        return found_objects

    # 要查找的形态键名称
    shape_key_name = 'まばたき'

    for obj in selected_objects:
        found_objects.extend(find_shape_keys_with_name(obj, shape_key_name))

    # 打印结果
    if found_objects:
        Log.info(f"Found  {len(found_objects)} "
                 f"objects containing the shape key '{shape_key_name}'.")
        for obj in found_objects:
            Log.info(f"Object containing the shape key '{shape_key_name}', {obj.name} found.")
    else:
        Log.raise_error(f"No object containing the shape key "
                        f"'{shape_key_name}' was found.", Exception)
    return found_objects


def find_mmd_meshes_with_config(config):
    """
    根据配置文件查找包含指定眨眼形态键的网格对象
    
    :param config: 配置文件数据
    :return: 包含配置中眨眼形态键的网格对象列表
    """
    meshes = []
    
    # 获取眨眼形态键名称
    if config:
        blink_shape_key = config.get('shape_keys', {}).get('blink', 'まばたき')
    else:
        blink_shape_key = 'まばたき'
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            if obj.data.shape_keys and obj.data.shape_keys.key_blocks:
                for shape_key in obj.data.shape_keys.key_blocks:
                    if shape_key.name == blink_shape_key:
                        meshes.append(obj)
                        break
    return meshes


def apply_blink_animation_with_config(mesh, frames, config=None):
    """
    根据配置文件将眨眼动画应用到网格对象
    
    :param mesh: 网格对象
    :param frames: 包含帧数据的字典 {形态键名: [{frame: 帧数, value: 值}]}
    :param config: 配置文件数据
    """
    # 获取眨眼形态键名称
    if config:
        blink_shape_key = config.get('shape_keys', {}).get('blink', 'まばたき')
    else:
        blink_shape_key = 'まばたき'
    
    for shape_key_name, keyframes in frames.items():
        # 只处理配置中指定的眨眼形态键
        if shape_key_name == blink_shape_key:
            # 查找形态键
            shape_key = None
            for key_block in mesh.data.shape_keys.key_blocks:
                if key_block.name == shape_key_name:
                    shape_key = key_block
                    break
            
            if shape_key:
                # 清除现有关键帧 - 使用keyframe_delete方法
                # 获取所有关键帧的帧数
                frame_numbers = set()
                for keyframe in keyframes:
                    frame_numbers.add(keyframe['frame'])
                
                # 删除指定帧数的关键帧
                for frame in frame_numbers:
                    try:
                        shape_key.keyframe_delete(data_path="value", frame=frame)
                    except RuntimeError:
                        # 关键帧不存在时忽略错误
                        pass
                
                # 添加关键帧
                for keyframe in keyframes:
                    shape_key.value = keyframe['value']
                    shape_key.keyframe_insert(data_path="value", frame=keyframe['frame'])
                    
                # 更新动画数据
                mesh.data.update_tag()


def register():
    """注册眨眼面板相关类"""
    bpy.utils.register_class(RandomBlinkPanel)
    bpy.utils.register_class(ImportBlinkConfigOperator)
    bpy.utils.register_class(RandomBlinkOperator)


def unregister():
    """注销眨眼面板相关类"""
    bpy.utils.unregister_class(RandomBlinkPanel)
    bpy.utils.unregister_class(ImportBlinkConfigOperator)
    bpy.utils.unregister_class(RandomBlinkOperator)
