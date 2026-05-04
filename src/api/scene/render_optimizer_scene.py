# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
Render Optimizer Scene Properties
"""
import bpy  # pylint: disable=import-error

render_opt_preset = bpy.props.EnumProperty(
    name="Preset",
    description="Render style preset",
    items=[
        ('PBR', "PBR Realistic", "Standard PBR material enhancement"),
        ('PBR_AGGRESSIVE', "PBR Aggressive", "Significantly enhanced texture and contrast"),
        ('NPR', "NPR Toon", "Preserve native MMD toon + outline"),
    ],
    default='PBR',
)

render_opt_brightness_override = bpy.props.EnumProperty(
    name="Brightness",
    description="Override automatic brightness detection",
    items=[
        ('AUTO', "Auto", "Automatically detect from model tone"),
        ('LIGHT', "Light", "Model is overall light-colored"),
        ('MEDIUM', "Medium", "Standard brightness"),
        ('DARK', "Dark", "Model is overall dark-colored"),
    ],
    default='AUTO',
)

render_opt_use_compositor = bpy.props.BoolProperty(
    name="Compositor Post",
    description="Enable bloom, vignette, contrast",
    default=True,
)

render_opt_outline_strategy = bpy.props.EnumProperty(
    name="Outline",
    description="Outline strategy (NPR mode only)",
    items=[
        ('none', "None", "No outline"),
        ('freestyle_silhouette', "Freestyle Silhouette", "Silhouette only"),
        ('freestyle_auto', "Freestyle Auto", "Topology-aware auto strategy"),
    ],
    default='freestyle_auto',
)

render_opt_engine = bpy.props.EnumProperty(
    name="Engine",
    description="Render engine",
    items=[
        ('EEVEE', "EEVEE", "Blender EEVEE Next (Fast)"),
        ('CYCLES', "Cycles", "Blender Cycles (High Quality)"),
    ],
    default='EEVEE',
)
