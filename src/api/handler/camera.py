# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
摄像机操作
"""
from bpy.types import Operator  # pylint: disable=import-error


class CameraApplySettingsOperator(Operator):
    """Apply camera settings to the selected camera."""
    bl_idname = "camera.apply_settings"
    bl_label = "apply camera settings"
    bl_description = "Apply settings to the selected camera"

    @classmethod
    def poll(cls, context):
        """
        类方法，检查当前上下文是否适用于执行此操作。

        参数:
        - cls: 类本身，由装饰器自动提供。
        - context: 当前的上下文对象，包含了Blender当前运行环境的各类信息。

        返回:
        - bool: 如果当前对象存在且类型为'CAMERA'，则返回True，否则返回False。
        """
        return context.object and context.object.type == 'CAMERA'

    def execute(self, context):
        """
        执行相机设置操作。

        参数:
        - self: 方法所属的实例。
        - context: 当前的上下文对象，包含了Blender当前运行环境的各类信息。

        返回:
        - set: 包含字符串'FINISHED'的集合，表示操作完成。
        """
        # 从上下文中获取相机设置和当前对象的数据
        settings = context.scene.camera_settings
        camera = context.object.data

        # 应用焦距设置到相机的镜头长度
        camera.lens = float(settings.focal_length)
        # 设置相机是否使用景深效果
        camera.dof.use_dof = settings.depth_of_field
        # 如果使用景深效果，应用光圈设置
        if settings.depth_of_field:
            camera.dof.aperture_fstop = float(settings.aperture)

        # 如果启用了景深效果并且指定了目标对象，则应用目标对象到景深设置
        if settings.depth_of_field and settings.target_object:
            camera.dof.focus_object = settings.target_object

        # 报告操作完成
        self.report({'INFO'}, "Camera settings have been applied.")
        return {'FINISHED'}
