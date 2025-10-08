# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and SoyMilkWhisky
"""
Blender Scene文件
"""
import bpy  # pylint: disable=import-error

lips_audio_path = bpy.props.StringProperty(
    name="Audio Path",
    description="Path to the Audio file.",
    default="",
    maxlen=512,
    subtype='FILE_PATH',
)

# 口型配置选择属性
def get_lips_config_files(self, context):
    """获取口型配置文件列表"""
    from ...core.config_manager import get_config_manager
    config_manager = get_config_manager()
    config_files = config_manager.get_config_files('lip_sync')
    # 返回格式: (identifier, name, description)
    return [(config['name'], config['name'], f"{config['name']} ({config['type']})") for config in config_files]

lips_config_selection = bpy.props.EnumProperty(
    name="Lip Sync Config",
    description="Select lip sync configuration",
    items=get_lips_config_files
)

lips_custom_config_path = bpy.props.StringProperty(
    name="Custom Config Path",
    description="Path to custom lip sync configuration file",
    default="",
    maxlen=512,
    subtype='FILE_PATH',
)

# 眨眼配置选择属性
def get_blink_config_files(self, context):
    """获取眨眼配置文件列表"""
    from ...core.config_manager import get_config_manager
    config_manager = get_config_manager()
    config_files = config_manager.get_config_files('blink')
    # 返回格式: (identifier, name, description)
    return [(config['name'], config['name'], f"{config['name']} ({config['type']})") for config in config_files]

blink_config_selection = bpy.props.EnumProperty(
    name="Blink Config",
    description="Select blink configuration",
    items=get_blink_config_files
)

blink_custom_config_path = bpy.props.StringProperty(
    name="Custom Config Path",
    description="Path to custom blink configuration file",
    default="",
    maxlen=512,
    subtype='FILE_PATH',
)

lips_start_frame = bpy.props.IntProperty(name="Start Frame", default=1)

buffer_frame = bpy.props.FloatProperty(
    name="Delayed Opening",
    description="The mouth does not open immediately upon recognition;"
                " the unit is in milliseconds,"
                " and the buffer value is calculated"
                " based on the acceleration parameters for opening the mouth",
    default=0.15,
    min=0.02,
    max=1.0)

approach_speed = bpy.props.FloatProperty(
    name="Speed Up Opening",
    description="The larger this parameter is, "
                "the greater the value of the morph key for delayed mouth opening will be.",
    default=1.6,
    min=1,
    max=10,
)

db_threshold = bpy.props.FloatProperty(
    name="DB Threshold",
    description="Minimum threshold for audio volume detection",
    default=-50.00,
    min=-65.00,
    max=0)

rms_threshold = bpy.props.FloatProperty(
    name="RMS Threshold",
    description="Minimum threshold for audio root mean square identification",
    default=0.05,
    min=0.001,
    max=1.0,
)

max_morph_value = bpy.props.FloatProperty(
    name="Max Morph Value",
    description="Threshold for the maximum value of the morphological key",
    default=0.97,
    min=0.01,
    max=1.0,
)

blink_start_frame = bpy.props.IntProperty(name="start", default=1, min=1)
blink_end_frame = bpy.props.IntProperty(name="end", default=250, min=1)

blinking_frequency = bpy.props.FloatProperty(
    name="blink interval",
    description="The interval in seconds between blinks.",
    default=4.0,
    min=1.0,
    max=3600.0,
)

blinking_wave_ratio = bpy.props.FloatProperty(
    name="blinking wave ratio",
    description="Blink interval = "
                "blink interval + "
                "rand(-fluctuation ratio, fluctuation ratio)",
    default=0.1,
    min=0,
    max=1,
)
