# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and SoyMilkWhisky
"""
渲染预设面板
"""
import bpy  # pylint: disable=import-error


# 定义一个Blender的面板类，用于在UI中显示渲染预设选项
class RenderPresetPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """
    渲染预设面板
    """
    # 面板的标题
    bl_label = "Render Preset"
    # 面板的唯一标识符
    bl_idname = "OBJECT_PT_RENDER_PRESET"
    # 面板显示的空间类型
    bl_space_type = 'VIEW_3D'
    # 面板显示的区域类型
    bl_region_type = 'UI'
    # 面板显示的类别，用于在UI中分组面板
    bl_category = 'HBR MMD Tools'
    # 面板的显示顺序
    bl_order = 1

    # 绘制面板中的UI元素
    def draw(self, context):
        """
         在给定的上下文中绘制UI元素。

         参数:
         - context: 当前的上下文对象，包含了关于当前Blender环境的信息。

         此函数负责在UI中添加与场景相关的属性控件，以允许用户编辑场景的属性。
         """
        # 获取当前的布局对象，用于创建UI元素
        layout = self.layout
        # 获取当前的场景对象
        scene = context.scene

        # 在布局中添加一个属性控件，用于显示和编辑场景的分辨率预设属性
        layout.prop(scene, "resolution_preset")
        # 在布局中添加一个属性控件，用于显示和编辑场景的宽高比预设属性
        layout.prop(scene, "aspect_ratio_preset")
        # 在布局中添加一个属性控件，用于显示和编辑场景的图像方向预设属性
        layout.prop(scene, "orientation_preset")
