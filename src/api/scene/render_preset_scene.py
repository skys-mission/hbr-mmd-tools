# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
Render Preset Scene
"""


from bpy.props import EnumProperty # pylint: disable=import-error

from ..handler.render import update_render_settings

resolution_preset = EnumProperty(
    items=[
        ('default', 'default', 'default'),
        ('480P', '480P', 'Set resolution to 480P'),
        ('720P', '720P', 'Set resolution to 720P'),
        ('1080P', '1080P', 'Set resolution to 1080P'),
        ('2K', '2K', 'Set resolution to 2K'),
        ('4K', '4K', 'Set resolution to 4K'),
        ('8K', '8K', 'Set resolution to 8K'),
        ('16K', '16K', 'Set resolution to 16K')
    ],
    name="Resolution",
    update=update_render_settings
)

aspect_ratio_preset = EnumProperty(
    items=[
        ('default', 'default', 'default'),
        ('1:1', '1:1', 'Other'),
        ('2:1', '2:1', 'Other'),
        ('2.35:1', '2.35:1', 'Old Film Standards'),
        ('2.39:1', '2.39:1 Film Standards', 'Film Standards'),
        ('4:3', '4:3', 'Old Standard'),
        ('3:2', '3:2', 'Other'),
        ('16:9', '16:9', 'Standard'),
        ('382:239', '382:239 Bilibili cover image', 'Bilibili cover image')
    ],
    name="Aspect Ratio",
    update=update_render_settings
)

orientation_preset = EnumProperty(
    items=[
        ('default', 'default', 'default'),
        ('LANDSCAPE', 'Landscape', ''),
        ('PORTRAIT', 'Portrait', '')
    ],
    name="Rotate",
    update=update_render_settings
)
