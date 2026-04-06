# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and SoyMilkWhisky
"""
...
"""
import bpy  # pylint: disable=import-error


# 定义一个Blender面板类CameraSetPanel，用于在3D视图的UI侧边栏中显示相机设置
class CameraSetPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """
    ...
    """
    # 设置面板的标题为"Set Camera"
    bl_label = "Set Camera"
    # 设置面板的唯一标识符为"OBJECT_PT_SET_CAMERA"
    bl_idname = "OBJECT_PT_SET_CAMERA"
    # 指定面板显示的空间类型为"VIEW_3D"
    bl_space_type = 'VIEW_3D'
    # 指定面板显示的区域类型为"UI"
    bl_region_type = 'UI'
    # 将面板分类到"Tools"标签页下
    bl_category = 'HBR MMD Tools'
    # 设置面板的显示顺序为2
    bl_order = 2

    # 实现draw方法以绘制面板界面
    def draw(self, context):
        """
        This method is used to draw the panel interface.
        """
        # 获取布局对象
        layout = self.layout
        # 获取当前场景对象
        scene = context.scene

        # 获取场景的相机设置
        settings = scene.camera_settings

        # 在布局中添加属性控件，用于显示和编辑相机的焦距
        layout.prop(settings, "focal_length")
        # 在布局中添加属性控件，用于显示和编辑相机的光圈
        layout.prop(settings, "aperture")
        # 在布局中添加属性控件，用于显示和编辑相机的景深效果启用状态
        layout.prop(settings, "depth_of_field")

        # 如果启用了景深效果，则在布局中添加属性控件，用于选择目标对象
        if settings.depth_of_field:
            layout.prop(settings, "target_object")

        # 创建一个新的行布局
        row = layout.row()
        # 在行布局中添加一个操作按钮，用于应用相机设置
        row.operator("camera.apply_settings")
        # 根据当前对象是否为相机类型，启用或禁用行布局中的按钮
        row.enabled = context.object and context.object.type == 'CAMERA'
