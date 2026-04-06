# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
Blender Scene About Camera Preset
"""
# 导入Blender内置模块和属性
import bpy  # pylint: disable=import-error
from bpy.props import EnumProperty, BoolProperty, PointerProperty  # pylint: disable=import-error

# 摄像机设置的开始，解释了以下代码块的目的

# 焦距选项
# 定义了一组焦距选项，用于模拟不同焦距镜头的效果
focal_lengths = [
    ('50', '50mm human eye perspective', 'human eye perspective'),
    ('14', '14mm ultra-wide field', 'Highlight background'),
    ('24', '24mm wide angle', 'scenery, street snap'),
    ('35', '35mm', '35mm'),
    ('85', '85mm classic portrait', 'classic portrait, background blur'),
    ('135', '135mm long-focus', 'long-focus, strong background blur')
]

# 光圈选项
# 定义了一组光圈选项，用于模拟在不同光线条件下的拍摄效果
apertures = [
    ('2.8', 'f/2.8 default', 'Background blur, portrait/night scene photography'),
    ('1.4', 'f/1.4 low light env', 'Background blur, portrait/night scene photography'),
    ('4', 'f/4 medium aperture', 'Slightly Blurred. Suitable for average lighting conditions'),
    ('5.6', 'f/5.6', 'Suitable for average lighting conditions'),
    ('8', 'f/8 small aperture', 'Requires strong lighting'),
    ('11', 'f/11', 'Requires strong lighting'),
    ('13', 'f/13', 'Requires a strong light environment'),
    ('22', 'f/22 minimum aperture', 'Requires a strong light environment'),
    ('32', 'f/32', 'f/32'),
    ('0.95', 'f/0.95', 'f/0.95')
]

# 定义摄像机设置属性类
# 该类用于创建摄像机设置的属性，包括焦距、光圈、景深和对焦对象选择
class CameraSettingsProperties(bpy.types.PropertyGroup): # pylint: disable=too-few-public-methods
    """
    Camera Settings Properties
    """
    focal_length: EnumProperty(
        items=focal_lengths,
        name="Focal Length",
        description="Focal Length."
    )
    aperture: EnumProperty(
        items=apertures,
        name="F-Stop",
        description="F-Stop."
    )
    depth_of_field: BoolProperty(
        name="Depth of Field",
        description="Depth of Field",
        default=False
    )
    target_object: PointerProperty(
        type=bpy.types.Object,
        name="Focus on Object",
        description="Select focus object"
    )
