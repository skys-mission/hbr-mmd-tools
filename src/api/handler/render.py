# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
除了渲染预设
"""
import math


def update_render_settings(self, context):  # pylint: disable=unused-argument
    """
    更新渲染设置
    """
    scene = context.scene
    render = scene.render

    resolution_presets = {
        '480P': (854, 480),
        '720P': (1280, 720),
        '1080P': (1920, 1080),
        '2K': (2560, 1440),
        '4K': (3840, 2160),
        '8K': (7680, 4320),
        '16K': (15360, 8640)
    }

    res_preset = scene.resolution_preset
    if res_preset in resolution_presets:
        render.resolution_x, render.resolution_y = resolution_presets[res_preset]

    aspect_ratios = {
        '1:1': (1, 1),
        '2:1': (2, 1),
        '2.35:1': (235, 100),
        '2.39:1': (239, 100),
        '4:3': (4, 3),
        '3:2': (3, 2),
        '16:9': (16, 9),
        '382:239': (382, 239),
    }

    aspect_ratio_preset = scene.aspect_ratio_preset
    if aspect_ratio_preset in aspect_ratios and aspect_ratio_preset != "16:9":
        render.resolution_y = math.ceil(
            (render.resolution_x / aspect_ratios[aspect_ratio_preset][0]) * \
            aspect_ratios[aspect_ratio_preset][1]
        )

    orientation = scene.orientation_preset
    if orientation == "PORTRAIT":
        render.resolution_x, render.resolution_y = (
            render.resolution_y, render.resolution_x
        )
