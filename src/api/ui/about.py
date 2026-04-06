# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
关于面板
"""
import bpy  # pylint: disable=import-error

from ..data.local import LOCAL_CH_36, LOCAL_CH_40


class AboutPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """
    ...
    """
    # 面板的标题
    bl_label = "About"
    # 面板的唯一标识符
    bl_idname = "OBJECT_PT_ABOUT"
    # 面板显示的空间类型
    bl_space_type = 'VIEW_3D'
    # 面板显示的区域类型
    bl_region_type = 'UI'
    # 面板显示的类别，用于在UI中分组面板
    bl_category = 'HBR MMD Tools'
    # 面板的显示顺序
    bl_order = 5

    # 绘制面板中的UI元素
    def draw(self, context):  # pylint: disable=unused-argument
        """
         在给定的上下文中绘制UI元素。

         参数:
         - context: 当前的上下文对象，包含了关于当前Blender环境的信息。

         此函数负责在UI中添加与场景相关的属性控件，以允许用户编辑场景的属性。
         """
        # 获取当前的布局对象，用于创建UI元素
        layout = self.layout

        row = layout.row()
        row.alignment = 'CENTER'
        props = row.operator("wm.url_open", text="user doc", icon='URL')
        props.url = "https://github.com/skys-mission/hbr_mmd_tools#readme"
        row.alignment = 'CENTER'
        props = row.operator("wm.url_open", text="open source", icon='URL')
        props.url = "https://github.com/skys-mission/hbr_mmd_tools"

        row = layout.row()
        row.label(text="author: Half-Bottled Reverie")

        if self._is_chinese_interface(context):
            row = layout.row()
            row.label(text="QQ群：105619180")

    @staticmethod
    def _is_chinese_interface(context):
        language = getattr(context.preferences.view, "language", "")
        if isinstance(language, str) and (
            language in {LOCAL_CH_36, LOCAL_CH_40} or language.startswith("zh")
        ):
            return True

        locale = getattr(bpy.app.translations, "locale", "")
        return isinstance(locale, str) and locale.startswith("zh")
