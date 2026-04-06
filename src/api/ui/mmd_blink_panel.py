# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
# pylint: disable=R0801
"""
随机眨眼面板
"""
import os
import subprocess
import sys

import bpy  # pylint: disable=import-error

from ...core.config_manager import get_config_manager
from ...services.blink_service import generate_random_blink
from ...util.logger import Log


class RandomBlinkPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """
        ...根据まばたき眨眼
    """
    bl_label = "MMD Random Blink"
    bl_idname = "VIEW3D_PT_Random_blink"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HBR MMD Tools'
    bl_order = 4

    def draw(self, context):
        """
        ...
        """
        layout = self.layout

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


class RandomBlinkConfigPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """
    眨眼配置面板
    """
    bl_label = "Config"
    bl_idname = "VIEW3D_PT_Random_Blink_Config"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HBR MMD Tools'
    bl_parent_id = "VIEW3D_PT_Random_blink"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        """
        ...
        """
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene, "blink_config_selection", text="Config")

        row = layout.row()
        row.prop(scene, "blink_custom_config_path", text="Custom Config")
        row.operator("scene.import_blink_config", text="Apply", icon='CHECKMARK')

        row = layout.row()
        row.operator(
            "scene.open_blink_config_folder",
            text="Open Config Folder",
            icon='FILE_FOLDER',
        )



class ImportBlinkConfigOperator(bpy.types.Operator):  # pylint: disable=too-few-public-methods
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

        config_manager = get_config_manager()
        config_name = os.path.splitext(os.path.basename(scene.blink_custom_config_path))[0]

        imported_entry = config_manager.import_config(
            'blink',
            scene.blink_custom_config_path,
            config_name,
        )
        if imported_entry:
            self.report({'INFO'}, f"Successfully imported config: {config_name}")
            scene.blink_config_selection = imported_entry['id']
            # 清空自定义配置路径
            scene.blink_custom_config_path = ""
            # 标记需要刷新UI
            context.area.tag_redraw()
        else:
            self.report({'ERROR'}, "Failed to import config")
            return {'CANCELLED'}

        return {'FINISHED'}


class OpenBlinkConfigFolderOperator(bpy.types.Operator):  # pylint: disable=too-few-public-methods
    """打开眨眼配置文件夹操作器"""
    bl_idname = "scene.open_blink_config_folder"
    bl_label = "Open Blink Config Folder"
    bl_description = "Open the blink configuration folder"

    def execute(self, _context):
        """执行打开文件夹"""
        config_manager = get_config_manager()

        blink_config_dir = config_manager.get_user_config_dir('blink')

        # 确保目录存在
        os.makedirs(blink_config_dir, exist_ok=True)

        # 打开文件夹（跨平台兼容）
        try:
            if os.name == 'nt':  # Windows
                startfile = getattr(os, "startfile", None)
                if not callable(startfile):
                    raise OSError("os.startfile is unavailable on this platform")
                startfile(blink_config_dir)  # pylint: disable=not-callable
            elif os.name == 'posix':  # macOS/Linux
                command = (
                    ['open', blink_config_dir]
                    if sys.platform == 'darwin'
                    else ['xdg-open', blink_config_dir]
                )
                subprocess.run(command, check=True)

            self.report({'INFO'}, f"Opened blink config folder: {blink_config_dir}")
        except (OSError, subprocess.SubprocessError) as exc:
            self.report({'ERROR'}, f"Failed to open folder: {str(exc)}")
            return {'CANCELLED'}

        return {'FINISHED'}


class RandomBlinkOperator(bpy.types.Operator):  # pylint: disable=too-few-public-methods
    """
    ...
    """
    bl_idname = "scene.gen_random_blink"
    bl_label = "Gen random blink"

    def execute(self, context):
        """
        ...
        """
        context.window_manager.progress_begin(0, 100)
        context.window.cursor_modal_set('WAIT')

        try:
            result = generate_random_blink(context)
            context.window_manager.progress_update(100)
            self.report({'INFO'},
                        f"Successfully generated {result['keyframe_count']} blink animations")
        except Exception as e:  # pylint: disable=broad-exception-caught
            context.window_manager.progress_end()
            context.window.cursor_modal_restore()
            Log.raise_error(str(e), e.__class__)

        context.window_manager.progress_end()
        context.window.cursor_modal_restore()
        return {'FINISHED'}
