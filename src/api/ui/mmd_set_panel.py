# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and SoyMilkWhisky
# pylint: disable=R0801
"""
MMD面板
"""

import bpy  # pylint: disable=import-error
import os
import sys

from ...services.lip_sync_service import generate_lip_sync
from ...util.logger import Log


# 定义一个Blender的面板类，用于在UI中显示渲染预设选项
class MMDHelperPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """
    渲染预设面板
    """
    # 面板的标题
    bl_label = "MMD Lip Gen"
    # 面板的唯一标识符
    bl_idname = "OBJECT_PT_MMD_Helper"
    # 面板显示的空间类型
    bl_space_type = 'VIEW_3D'
    # 面板显示的区域类型
    bl_region_type = 'UI'
    # 面板显示的类别，用于在UI中分组面板
    bl_category = 'HBR MMD Tools'
    # 面板的显示顺序
    bl_order = 3

    # 绘制面板中的UI元素
    def draw(self, context):
        """
         在给定的上下文中绘制UI元素。

         参数:
         - context: 当前的上下文对象，包含了关于当前Blender环境的信息。

         此函数负责在UI中添加与场景相关的属性控件，以允许用户编辑场景的属性。
         """
        layout = self.layout
        scene = context.scene

        # 配置选择区域
        box = layout.box()
        box.label(text="Lip Sync Configuration")
        
        # 配置选择下拉框
        row = box.row()
        row.prop(scene, "lips_config_selection", text="Config")
        
        # 自定义配置导入
        row = box.row()
        row.prop(scene, "lips_custom_config_path", text="Custom Config")
        row.operator("mmd.import_lips_config", text="Apply", icon='CHECKMARK')
        
        # 打开配置文件夹
        row = box.row()
        row.operator("mmd.open_lips_config_folder", text="Open Config Folder", icon='FILE_FOLDER')
        
        # 分隔线
        layout.separator()
        
        # 音频和参数设置
        layout.prop(scene, "lips_audio_path")
        layout.prop(scene, "lips_start_frame")
        layout.prop(scene, "db_threshold")
        layout.prop(scene, "rms_threshold")
        layout.prop(scene, "buffer_frame")
        layout.prop(scene, "approach_speed")
        layout.prop(scene, "max_morph_value")

        layout.operator("mmd.gen_lips")


class ImportLipsConfigOperator(bpy.types.Operator):
    """导入口型配置操作器"""
    bl_idname = "mmd.import_lips_config"
    bl_label = "Import Lip Sync Config"
    bl_description = "Import custom lip sync configuration"

    def execute(self, context):
        """执行导入配置"""
        scene = context.scene
        
        if not scene.lips_custom_config_path:
            self.report({'ERROR'}, "Please select a custom config file")
            return {'CANCELLED'}
        
        from ...core.config_manager import get_config_manager
        config_manager = get_config_manager()
        
        # 从文件路径中提取配置名称
        import os
        config_name = os.path.splitext(os.path.basename(scene.lips_custom_config_path))[0]
        
        imported_entry = config_manager.import_config(
            'lip_sync',
            scene.lips_custom_config_path,
            config_name,
        )
        if imported_entry:
            self.report({'INFO'}, f"Successfully imported config: {config_name}")
            scene.lips_config_selection = imported_entry['id']
            # 清空自定义配置路径
            scene.lips_custom_config_path = ""
            # 标记需要刷新UI
            context.area.tag_redraw()
        else:
            self.report({'ERROR'}, "Failed to import config")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class OpenLipsConfigFolderOperator(bpy.types.Operator):
    """打开口型配置文件夹操作器"""
    bl_idname = "mmd.open_lips_config_folder"
    bl_label = "Open Lip Sync Config Folder"
    bl_description = "Open the lip sync configuration folder"

    def execute(self, context):
        """执行打开文件夹"""
        from ...core.config_manager import get_config_manager
        config_manager = get_config_manager()
        
        lips_config_dir = config_manager.get_user_config_dir('lip_sync')
        
        # 确保目录存在
        os.makedirs(lips_config_dir, exist_ok=True)
        
        # 打开文件夹（跨平台兼容）
        try:
            if os.name == 'nt':  # Windows
                os.startfile(lips_config_dir)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                subprocess.run(['open', lips_config_dir] if sys.platform == 'darwin' else ['xdg-open', lips_config_dir])
            
            self.report({'INFO'}, f"Opened lip sync config folder: {lips_config_dir}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open folder: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class GenLipsOperator(bpy.types.Operator):  # pylint: disable=too-few-public-methods
    """
    ...
    """
    bl_idname = "mmd.gen_lips"
    bl_label = "Gen Lips"
    bl_description = ""

    def execute(self, context):
        """
        ...
        :param context:
        :return:
        """
        context.window_manager.progress_begin(0, 100)
        context.window.cursor_modal_set('WAIT')
        context.window_manager.progress_update(98)

        try:
            generate_lip_sync(context)
        except Exception as e:  # pylint: disable=broad-exception-caught
            context.window_manager.progress_end()
            context.window.cursor_modal_restore()
            Log.raise_error(e, Exception)

        context.window_manager.progress_end()
        context.window.cursor_modal_restore()
        return {'FINISHED'}
