# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
Blender Scene文件
"""
import bpy  # pylint: disable=import-error

from ...core.config_manager import get_config_manager
from ...core.lip_sync_profiles import DEFAULT_LIP_SYNC_PRESET, get_lip_sync_preset_values

def get_timeline_audio_items(_self, context):
    """从 VSE 时间线动态获取音频片段列表。"""
    se = context.scene.sequence_editor
    if not se:
        return [("", "None", "No audio strips found")]

    items = []
    seen_ids = set()
    for strip in sorted(se.sequences, key=lambda s: s.channel, reverse=True):
        if strip.type == 'SOUND':
            filepath = getattr(strip.sound, 'filepath', None)
        elif strip.type == 'MOVIE':
            filepath = getattr(getattr(strip, 'sound', None), 'filepath', None)
        else:
            continue
        if not filepath:
            continue
        uid = f"{strip.channel}:{strip.name}"
        if uid not in seen_ids:
            seen_ids.add(uid)
            items.append((uid, strip.name, f"Channel {strip.channel}"))

    return items if items else [("", "None", "No audio strips found")]


lips_audio_source = bpy.props.EnumProperty(
    name="Audio Source",
    description="Where to get the audio for lip sync generation",
    items=(
        ("file", "File", "Use an audio file from disk"),
        ("timeline", "Timeline", "Use audio from the Video Sequence Editor timeline"),
    ),
    default="file",
)

lips_timeline_audio_strip = bpy.props.EnumProperty(
    name="Audio Strip",
    description="Select an audio strip from the timeline",
    items=get_timeline_audio_items,
)

lips_audio_path = bpy.props.StringProperty(
    name="Audio Path",
    description="Path to the Audio file.",
    default="",
    maxlen=512,
    subtype='FILE_PATH',
)

# 口型配置选择属性
def get_lips_config_files(_self, _context):
    """获取口型配置文件列表"""
    config_manager = get_config_manager()
    config_files = config_manager.get_config_entries('lip_sync')
    return [
        (config['id'], config['display_name'], config['description'])
        for config in config_files
    ]

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
def get_blink_config_files(_self, _context):
    """获取眨眼配置文件列表"""
    config_manager = get_config_manager()
    config_files = config_manager.get_config_entries('blink')
    return [
        (config['id'], config['display_name'], config['description'])
        for config in config_files
    ]

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

lips_generation_preset = bpy.props.EnumProperty(
    name="Preset",
    description="Choose the overall lip sync style",
    items=(
        ("natural", "Natural", "Smooth and balanced motion for most dialogue"),
        ("clear", "Clear Speech", "Sharper mouth motion for clearer articulation"),
        ("soft", "Soft Motion", "Smaller and softer mouth motion"),
    ),
    default=DEFAULT_LIP_SYNC_PRESET,
)

lips_use_custom_tuning = bpy.props.BoolProperty(
    name="Custom Tuning",
    description="Use manual advanced tuning instead of the preset",
    default=False,
)

_preset_defaults = get_lip_sync_preset_values(DEFAULT_LIP_SYNC_PRESET)

buffer_frame = bpy.props.FloatProperty(
    name="Delayed Opening",
    description="The mouth does not open immediately upon recognition;"
                " the unit is in milliseconds,"
                " and the buffer value is calculated"
                " based on the acceleration parameters for opening the mouth",
    default=_preset_defaults["buffer"],
    min=0.02,
    max=1.0)

approach_speed = bpy.props.FloatProperty(
    name="Speed Up Opening",
    description="The larger this parameter is, "
                "the greater the value of the morph key for delayed mouth opening will be.",
    default=_preset_defaults["approach_speed"],
    min=1,
    max=10,
)

db_threshold = bpy.props.FloatProperty(
    name="DB Threshold",
    description="Minimum threshold for audio volume detection",
    default=_preset_defaults["db_threshold"],
    min=-65.00,
    max=0)

rms_threshold = bpy.props.FloatProperty(
    name="RMS Threshold",
    description="Minimum threshold for audio root mean square identification",
    default=_preset_defaults["rms_threshold"],
    min=0.001,
    max=1.0,
)

max_morph_value = bpy.props.FloatProperty(
    name="Max Morph Value",
    description="Threshold for the maximum value of the morphological key",
    default=_preset_defaults["max_morph_value"],
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

blinking_half_ratio = bpy.props.FloatProperty(
    name="half blink ratio",
    description="Probability of a half-blink (0=never, 1=always). "
                "Double blinks use twice this chance.",
    default=0.15,
    min=0,
    max=1,
)
